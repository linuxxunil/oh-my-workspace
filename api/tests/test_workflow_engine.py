"""S4 验收：AC1 LangGraph 最小闭环 + AC5 版本/发布/运行历史（REQ-001）。"""

from src.services.code_exec import ExecResult
from tests.conftest import auth_headers, login


def _dag(provider_id: str) -> dict:
    return {
        "nodes": [
            {"id": "s", "type": "start", "config": {}},
            {
                "id": "r",
                "type": "retrieval",
                "config": {"query": "{q}", "top_k": 2, "output_key": "ctx"},
            },
            {
                "id": "l",
                "type": "llm",
                "config": {
                    "provider_id": provider_id,
                    "model": "mock",
                    "prompt": "ctx:{ctx} q:{q}",
                    "output_key": "answer",
                },
            },
            {"id": "i", "type": "if", "config": {"var": "branch", "equals": "yes"}},
            {
                "id": "c",
                "type": "code",
                "config": {"code": "result = 'x'", "output_key": "final"},
            },
            {"id": "e", "type": "end", "config": {}},
            {"id": "e2", "type": "end", "config": {}},
        ],
        "edges": [
            {"id": "e1", "source": "s", "target": "r"},
            {"id": "e2", "source": "r", "target": "l"},
            {"id": "e3", "source": "l", "target": "i"},
            {"id": "e4", "source": "i", "target": "c", "condition": "true"},
            {"id": "e5", "source": "i", "target": "e2", "condition": "false"},
            {"id": "e6", "source": "c", "target": "e"},
        ],
    }


def test_full_loop_true_branch(client, monkeypatch):
    from src.core import graph

    monkeypatch.setattr(graph.provider_service, "chat", lambda *a, **kw: "mock-answer")
    monkeypatch.setattr(
        graph.sandbox_client,
        "run_code",
        lambda *a, **kw: ExecResult(
            stdout="", stderr="", exit_code=0, timed_out=False, result="coded!"
        ),
    )
    root = auth_headers(login(client, "super_admin"))
    # 知识种子
    r = client.post(
        "/documents",
        headers=root,
        json={"title": "退款政策", "content": "本店支持七天无理由退款，退款流程详见说明。"},
    )
    assert r.status_code == 201, r.text
    # 建 provider（llm 配置校验用 id，不真实调用）
    r = client.post(
        "/models/providers",
        headers=root,
        json={"type": "openai_compatible", "name": "p1", "base_url": "https://api.example.com/v1"},
    )
    pid = r.json()["id"]
    r = client.post(
        "/workflows", headers=root, json={"name": "w1", "description": "", "dag": _dag(pid)}
    )
    assert r.status_code == 201, r.text
    wid = r.json()["id"]
    # 发布
    r = client.post(f"/workflows/{wid}/publish", headers=root)
    assert r.json()["is_published"] is True
    # 运行 true 分支
    r = client.post(
        f"/workflows/{wid}/run", headers=root, json={"inputs": {"q": "退款", "branch": "yes"}}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "succeeded"
    assert body["outputs"]["answer"] == "mock-answer"
    assert body["outputs"]["final"] == "coded!"
    assert isinstance(body["outputs"]["ctx"], list) and len(body["outputs"]["ctx"]) >= 1
    # false 分支无 final
    r = client.post(
        f"/workflows/{wid}/run", headers=root, json={"inputs": {"q": "退款", "branch": "no"}}
    )
    assert r.json()["status"] == "succeeded"
    assert "final" not in r.json()["outputs"]
    # 运行历史
    r = client.get(f"/workflows/{wid}/runs", headers=root)
    assert len(r.json()) == 2


def test_member_cannot_create_but_can_run(client, monkeypatch):
    from src.core import graph

    monkeypatch.setattr(graph.provider_service, "chat", lambda *a, **kw: "hi")
    root = auth_headers(login(client, "super_admin"))
    member = auth_headers(login(client, "member"))
    r = client.post(
        "/models/providers",
        headers=root,
        json={"type": "openai_compatible", "name": "p2", "base_url": "https://api.example.com/v1"},
    )
    pid = r.json()["id"]
    r = client.post(
        "/workflows", headers=member, json={"name": "wm", "description": "", "dag": _dag(pid)}
    )
    assert r.status_code == 403
    r = client.post(
        "/workflows", headers=root, json={"name": "w2", "description": "", "dag": _dag(pid)}
    )
    wid = r.json()["id"]
    r = client.post(
        f"/workflows/{wid}/run", headers=member, json={"inputs": {"q": "x", "branch": "no"}}
    )
    assert r.json()["status"] == "succeeded"


def test_invalid_dag_rejected(client):
    root = auth_headers(login(client, "super_admin"))
    bad = _dag("00000000-0000-0000-0000-000000000000")
    bad["edges"] = [
        e for e in bad["edges"] if not (e["source"] == "i" and e.get("condition") == "false")
    ]
    r = client.post("/workflows", headers=root, json={"name": "bad", "description": "", "dag": bad})
    assert r.status_code == 422


def test_delete_workflow_removes_versions_and_runs(client, monkeypatch):
    from src.core import graph

    monkeypatch.setattr(graph.provider_service, "chat", lambda *a, **kw: "mock-answer")
    monkeypatch.setattr(
        graph.sandbox_client,
        "run_code",
        lambda *a, **kw: ExecResult(
            stdout="", stderr="", exit_code=0, timed_out=False, result="coded!"
        ),
    )
    root = auth_headers(login(client, "super_admin"))
    member = auth_headers(login(client, "member"))
    r = client.post(
        "/workflows",
        headers=root,
        json={"name": "wdel", "description": "", "dag": _dag("unused")},
    )
    wid = r.json()["id"]
    r = client.post(f"/workflows/{wid}/versions", headers=root, json={"dag": _dag("unused")})
    assert r.json()["version_no"] == 2
    r = client.post(
        f"/workflows/{wid}/run", headers=root, json={"inputs": {"q": "x", "branch": "yes"}}
    )
    assert r.json()["status"] == "succeeded"
    # member 无 workflows:write → 403；资源仍在
    r = client.delete(f"/workflows/{wid}", headers=member)
    assert r.status_code == 403
    r = client.delete(f"/workflows/{wid}", headers=root)
    assert r.status_code == 204
    r = client.get(f"/workflows/{wid}/versions/latest", headers=root)
    assert r.status_code == 404
    r = client.get(f"/workflows/{wid}/runs", headers=root)
    assert r.status_code == 404
    r = client.delete(f"/workflows/{wid}", headers=root)
    assert r.status_code == 404
