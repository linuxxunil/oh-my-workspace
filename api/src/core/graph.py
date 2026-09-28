"""LangGraph 编译器（core owner）：DAG JSON → 可执行图，平台唯一执行底层。
节点语义：
- start/end：透传；llm：prompt.format(**vars) → provider chat → output_key；
- code：沙箱执行（data=vars，需 result=...）→ output_key；
- retrieval：query.format(**vars) → 知识检索 → output_key；
- if：vars[var] == equals → true/false 分支。
"""

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from src.dag import Dag
from src.services import knowledge_service, provider_service, sandbox_client


class WFState(TypedDict):
    vars: dict[str, Any]


def _render(tpl: str, variables: dict[str, Any]) -> str:
    try:
        return tpl.format(**variables)
    except KeyError:
        return tpl


def compile_and_run(
    dag: Dag, *, db: Session, tenant_id: str, inputs: dict[str, Any]
) -> dict[str, Any]:
    """编译并同步执行；任一节点异常即向上传播（service 记 failed）。"""
    by_id = {n.id: n for n in dag.nodes}
    outgoing: dict[str, list] = {}
    for e in dag.edges:
        outgoing.setdefault(e.source, []).append(e)
    start_id = next(n.id for n in dag.nodes if n.type == "start")

    def _llm_fn(node_id: str):  # type: ignore[no-untyped-def]
        def _fn(state: WFState) -> WFState:
            node = by_id[node_id]
            cfg = node.config
            prompt = _render(str(cfg["prompt"]), state["vars"])
            text = provider_service.chat(
                db,
                tenant_id=tenant_id,
                provider_id=str(cfg["provider_id"]),
                model=str(cfg["model"]),
                messages=[{"role": "user", "content": prompt}],
            )
            return {"vars": {**state["vars"], str(cfg["output_key"]): text}}

        return _fn

    def _code_fn(node_id: str):  # type: ignore[no-untyped-def]
        def _fn(state: WFState) -> WFState:
            node = by_id[node_id]
            cfg = node.config
            res = sandbox_client.run_code(code=str(cfg["code"]), data=dict(state["vars"]))
            if res.exit_code != 0 or res.timed_out:
                raise RuntimeError(f"code 节点 {node_id} 失败：{res.stderr[-500:]}")
            return {"vars": {**state["vars"], str(cfg["output_key"]): res.result}}

        return _fn

    def _retrieval_fn(node_id: str):  # type: ignore[no-untyped-def]
        def _fn(state: WFState) -> WFState:
            node = by_id[node_id]
            cfg = node.config
            query = _render(str(cfg["query"]), state["vars"])
            hits = knowledge_service.search(
                db, tenant_id=tenant_id, query=query, top_k=int(cfg.get("top_k", 3))
            )
            return {"vars": {**state["vars"], str(cfg["output_key"]): hits}}

        return _fn

    def _passthrough(state: WFState) -> WFState:
        return state

    def _if_route(node_id: str):  # type: ignore[no-untyped-def]
        def _fn(state: WFState) -> str:
            node = by_id[node_id]
            actual = state["vars"].get(str(node.config.get("var")))
            return "true" if str(actual) == str(node.config.get("equals")) else "false"

        return _fn

    builder: StateGraph = StateGraph(WFState)
    for node in dag.nodes:
        if node.type == "llm":
            builder.add_node(node.id, _llm_fn(node.id))
        elif node.type == "code":
            builder.add_node(node.id, _code_fn(node.id))
        elif node.type == "retrieval":
            builder.add_node(node.id, _retrieval_fn(node.id))
        else:
            builder.add_node(node.id, _passthrough)
    builder.add_edge(START, start_id)
    for node in dag.nodes:
        outs = outgoing.get(node.id, [])
        if node.type == "if":
            mapping = {e.condition: e.target for e in outs}
            builder.add_conditional_edges(node.id, _if_route(node.id), mapping)
        elif not outs:
            builder.add_edge(node.id, END)
        else:
            for e in outs:
                builder.add_edge(e.source, e.target)
    graph = builder.compile()
    final = graph.invoke({"vars": dict(inputs)})
    return dict(final["vars"])
