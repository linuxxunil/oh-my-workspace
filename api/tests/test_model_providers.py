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
