"""沙箱 client（service owner）。开发直跑默认本地执行；配 SANDBOX_URL 后走 HTTP。
SSRF-safe：云元数据/内网后缀一律禁；显式配置的本机回环地址视为 operator intent 放行。"""

from urllib.parse import urlparse

import httpx

from src.config import settings
from src.libs.http import assert_safe_url
from src.services.code_exec import ExecResult, execute_code

_LOOPBACK = {"localhost", "127.0.0.1", "::1"}


def _sandbox_url() -> str:
    return getattr(settings, "sandbox_url", "")


def run_code(*, code: str, data: dict, timeout_s: int = 30) -> ExecResult:
    """code 节点统一入口；返回 ExecResult（exit_code 非 0 即节点失败）。"""
    base = _sandbox_url().rstrip("/")
    if not base:
        return execute_code(code=code, data=data, timeout_s=timeout_s)
    url = base + "/execute"
    host = (urlparse(base).hostname or "").lower()
    if host not in _LOOPBACK:
        assert_safe_url(url)
    r = httpx.post(
        url, json={"code": code, "data": data, "timeout_s": timeout_s}, timeout=timeout_s + 5
    )
    r.raise_for_status()
    body = r.json()
    return ExecResult(
        stdout=body.get("stdout", ""),
        stderr=body.get("stderr", ""),
        exit_code=int(body.get("exit_code", 1)),
        timed_out=bool(body.get("timed_out", False)),
        result=body.get("result"),
    )
