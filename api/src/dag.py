"""DAG JSON schema（Pydantic v2，后端拥有形状，前端画布只消费）。
最小闭环五节点：start/llm/code/if/retrieval/end。
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

NodeType = Literal["start", "end", "llm", "code", "if", "retrieval"]


class Position(BaseModel):
    x: float = 0
    y: float = 0


class DagNode(BaseModel):
    id: str = Field(min_length=1)
    type: NodeType
    # llm: {provider_id, model, prompt, output_key}
    # code: {code, output_key}
    # if: {var, equals}
    # retrieval: {query, top_k, output_key}
    config: dict = Field(default_factory=dict)
    position: Position = Field(default_factory=Position)


class DagEdge(BaseModel):
    id: str = Field(min_length=1)
    # if 节点的出边用 condition 区分："true" | "false"，其余出边无需 condition。
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    condition: Literal["true", "false"] | None = None


class Dag(BaseModel):
    nodes: list[DagNode]
    edges: list[DagEdge]

    @model_validator(mode="after")
    def check_structure(self) -> "Dag":
        ids = [n.id for n in self.nodes]
        if len(set(ids)) != len(ids):
            raise ValueError("节点 id 重复")
        by_id = {n.id: n for n in self.nodes}
        starts = [n for n in self.nodes if n.type == "start"]
        ends = [n for n in self.nodes if n.type == "end"]
        if len(starts) != 1:
            raise ValueError("有且仅有一个 start 节点")
        if not ends:
            raise ValueError("至少一个 end 节点")
        for e in self.edges:
            if e.source not in by_id or e.target not in by_id:
                raise ValueError(f"边 {e.id} 端点不存在")
            src = by_id[e.source]
            if src.type == "if" and e.condition not in ("true", "false"):
                raise ValueError(f"if 节点出边 {e.id} 必须带 condition true/false")
            if src.type != "if" and e.condition is not None:
                raise ValueError(f"非 if 节点出边 {e.id} 不应带 condition")
        for n in self.nodes:
            if n.type == "if":
                conds = sorted(str(e.condition) for e in self.edges if e.source == n.id)
                if conds != ["false", "true"]:
                    raise ValueError(f"if 节点 {n.id} 必须有 true/false 两条出边")
            elif n.type == "llm":
                for k in ("provider_id", "model", "prompt", "output_key"):
                    if not n.config.get(k):
                        raise ValueError(f"llm 节点 {n.id} 缺 {k}")
            elif n.type == "code":
                if not n.config.get("code") or not n.config.get("output_key"):
                    raise ValueError(f"code 节点 {n.id} 缺 code/output_key")
            elif n.type == "retrieval":
                if not n.config.get("query") or not n.config.get("output_key"):
                    raise ValueError(f"retrieval 节点 {n.id} 缺 query/output_key")
        return self


class WorkflowCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=512)
    dag: Dag


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str


class VersionResponse(BaseModel):
    id: str
    workflow_id: str
    version_no: int
    dag: dict
    is_published: bool


class VersionCreateRequest(BaseModel):
    dag: Dag


class RunRequest(BaseModel):
    inputs: dict = Field(default_factory=dict)


class RunResponse(BaseModel):
    id: str
    status: str
    outputs: dict
    error: str = ""


class DocumentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    content: str = Field(min_length=1)


class DocumentResponse(BaseModel):
    id: str
    title: str
    chunk_count: int
