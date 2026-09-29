"""S3 验收：AC2 模型双通道（REQ-001）。HTTP 层 monkeypatch，不打真实网络。"""

import httpx

from tests.conftest import auth_headers, login


def _fake_models(request: httpx.Request) -> httpx.Response:
    assert request.url.path.endswith("/models")
    return httpx.Response(
        200, json={"data": [{"id": "gpt-4o"}, {"id": "qwen-max"}]}, request=request
    )


def test_provider_crud_and_test_connection(client, monkeypatch):
    root = auth_headers(login(client, "super_admin"))
    # 建两通道
    for ptype, name in (("openai_compatible", "openai"), ("opencode_go", "OGO")):
        r = client.post(
            "/models/providers",
            headers=root,
            json={"type": ptype, "name": name, "base_url": "https://api.example.com/v1"},
        )
        assert r.status_code == 201, r.text
        assert "api_key" not in r.json()
    # member 只读：建应 403
    member = auth_headers(login(client, "member"))
    r = client.post(
        "/models/providers",
        headers=member,
        json={"type": "openai_compatible", "name": "x", "base_url": "https://x.example.com"},
    )
    assert r.status_code == 403
    # 连通性 + 模型列表（mock）
    import src.services.provider_service as svc

    monkeypatch.setattr(
        svc,
        "_http_get",
        lambda url, headers, timeout_s=10.0: _fake_models(httpx.Request("GET", url)),
    )
    providers = client.get("/models/providers", headers=root).json()
    pid = providers[0]["id"]
    r = client.post(f"/models/providers/{pid}/test", headers=root)
    assert r.json()["ok"] is True and r.json()["model_count"] == 2
    r = client.get(f"/models/providers/{pid}/models", headers=root)
    assert r.json() == ["gpt-4o", "qwen-max"]
    # 缓存命中：即使上游坏了仍返回缓存
    monkeypatch.setattr(
        svc,
        "_http_get",
        lambda url, headers, timeout_s=10.0: (_ for _ in ()).throw(RuntimeError("down")),
    )
    r = client.get(f"/models/providers/{pid}/models", headers=root)
    assert r.json() == ["gpt-4o", "qwen-max"]


def test_reject_inner_base_url(client):
    root = auth_headers(login(client, "super_admin"))
    r = client.post(
        "/models/providers",
        headers=root,
        json={"type": "openai_compatible", "name": "bad", "base_url": "http://169.254.169.254/"},
    )
    assert r.status_code == 400


def test_update_provider_patch_and_key_keep_semantics(client, monkeypatch):
    import src.services.provider_service as svc

    root = auth_headers(login(client, "super_admin"))
    member = auth_headers(login(client, "member"))
    r = client.post(
        "/models/providers",
        headers=root,
        json={
            "type": "openai_compatible",
            "name": "p-edit",
            "base_url": "https://api.example.com/v1",
            "api_key": "old-key",
        },
    )
    assert r.status_code == 201, r.text
    pid = r.json()["id"]
    # member 无 models:write → 403；不存在 → 404
    r = client.patch(f"/models/providers/{pid}", headers=member, json={"name": "x"})
    assert r.status_code == 403
    r = client.patch(
        "/models/providers/00000000-0000-0000-0000-000000000000",
        headers=root,
        json={"name": "x"},
    )
    assert r.status_code == 404
    # 改名冲突 → 409；内网地址 → 400
    client.post(
        "/models/providers",
        headers=root,
        json={"type": "openai_compatible", "name": "p-other", "base_url": "https://o.example.com"},
    )
    r = client.patch(f"/models/providers/{pid}", headers=root, json={"name": "p-other"})
    assert r.status_code == 409
    r = client.patch(
        f"/models/providers/{pid}", headers=root, json={"base_url": "http://127.0.0.1:9/"}
    )
    assert r.status_code == 400
    # 换 Key：连通请求带新 Key；空 Key：保持旧 Key
    seen: list[str] = []

    def _fake(url: str, headers: dict, timeout_s: float = 10.0):
        seen.append(headers.get("Authorization", ""))
        return _fake_models(httpx.Request("GET", url))

    monkeypatch.setattr(svc, "_http_get", _fake)
    r = client.patch(f"/models/providers/{pid}", headers=root, json={"api_key": "new-key"})
    assert r.status_code == 200, r.text
    assert "api_key" not in r.json()
    client.post(f"/models/providers/{pid}/test", headers=root)
    assert seen[-1] == "Bearer new-key"
    r = client.patch(
        f"/models/providers/{pid}",
        headers=root,
        json={"api_key": "", "base_url": "https://api2.example.com/v1"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["base_url"] == "https://api2.example.com/v1"
    client.post(f"/models/providers/{pid}/test", headers=root)
    assert seen[-1] == "Bearer new-key"


def test_delete_provider_bound_by_latest_version_returns_409(client):
    root = auth_headers(login(client, "super_admin"))
    member = auth_headers(login(client, "member"))
    r = client.post(
        "/models/providers",
        headers=root,
        json={"type": "openai_compatible", "name": "p-bound", "base_url": "https://b.example.com"},
    )
    pid = r.json()["id"]
    # member 删 → 403
    r = client.delete(f"/models/providers/{pid}", headers=member)
    assert r.status_code == 403
    # 无引用 → 204
    r = client.delete(f"/models/providers/{pid}", headers=root)
    assert r.status_code == 204
    # 重建 + 被最新版本引用 → 409，被引用名在 detail 中，供应商仍在
    r = client.post(
        "/models/providers",
        headers=root,
        json={"type": "openai_compatible", "name": "p-bound", "base_url": "https://b.example.com"},
    )
    pid = r.json()["id"]
    dag = {
        "nodes": [
            {"id": "s", "type": "start", "config": {}},
            {
                "id": "l",
                "type": "llm",
                "config": {
                    "provider_id": pid,
                    "model": "m",
                    "prompt": "hi",
                    "output_key": "answer",
                },
            },
            {"id": "e", "type": "end", "config": {}},
        ],
        "edges": [
            {"id": "e1", "source": "s", "target": "l"},
            {"id": "e2", "source": "l", "target": "e"},
        ],
    }
    r = client.post(
        "/workflows", headers=root, json={"name": "w-bound", "description": "", "dag": dag}
    )
    assert r.status_code == 201, r.text
    r = client.delete(f"/models/providers/{pid}", headers=root)
    assert r.status_code == 409, r.text
    assert "w-bound" in r.json()["detail"]
    assert any(p["id"] == pid for p in client.get("/models/providers", headers=root).json())
