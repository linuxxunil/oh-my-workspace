"""S5 验收：AC6 沙箱仅 Python（REQ-001）。
本地执行三用例 + client HTTP 路径（mock）+ SSRF 拦截。
"""

import httpx

from src.services.code_exec import execute_code


def test_local_normal():
    r = execute_code(code="result = data['a'] + 1", data={"a": 1}, timeout_s=10)
    assert (r.exit_code, r.timed_out, r.result) == (0, False, 2)


def test_local_error():
    r = execute_code(code="raise RuntimeError('boom')", data={}, timeout_s=10)
    assert r.exit_code != 0 and "boom" in r.stderr


def test_local_timeout():
    r = execute_code(code="import time; time.sleep(30)", data={}, timeout_s=2)
    assert r.timed_out is True and r.exit_code == 124


def test_client_http_path(monkeypatch):
    from src.services import sandbox_client

    monkeypatch.setattr(sandbox_client.settings, "sandbox_url", "http://sandbox:8090")

    def _fake_post(url, json, timeout):
        assert url == "http://sandbox:8090/execute"
        req = httpx.Request("POST", url)
        return httpx.Response(
            200,
            json={"stdout": "", "stderr": "", "exit_code": 0, "timed_out": False, "result": 7},
            request=req,
        )

    monkeypatch.setattr(sandbox_client.httpx, "post", _fake_post)
    r = sandbox_client.run_code(code="result = 7", data={})
    assert r.result == 7 and r.exit_code == 0


def test_client_allows_configured_loopback(monkeypatch):
    from src.services import sandbox_client

    monkeypatch.setattr(sandbox_client.settings, "sandbox_url", "http://localhost:8090")

    def _fake_post(url, json, timeout):
        assert url == "http://localhost:8090/execute"
        req = httpx.Request("POST", url)
        return httpx.Response(
            200,
            json={"stdout": "", "stderr": "", "exit_code": 0, "timed_out": False, "result": 1},
            request=req,
        )

    monkeypatch.setattr(sandbox_client.httpx, "post", _fake_post)
    r = sandbox_client.run_code(code="result = 1", data={})
    assert r.result == 1


def test_client_blocks_inner_url(monkeypatch):
    from src.services import sandbox_client

    monkeypatch.setattr(sandbox_client.settings, "sandbox_url", "http://169.254.169.254/")
    try:
        sandbox_client.run_code(code="result = 1", data={})
    except ValueError as e:
        assert "内网" in str(e)
    else:
        raise AssertionError("应拦截内网地址")
