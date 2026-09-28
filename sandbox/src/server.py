"""沙箱 HTTP 服务：仅 Python，无网络声明，超时+内存限。
执行语义与 api/src/services/code_exec.py 保持一致（正典在 api，本文件为独立部署的同构复刻）。
发布时镜像底座：本地 python:3.11-slim（docker images 已核验），跑时 net=none。
"""
import resource
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="workspace2-sandbox", version="0.1.0")


class ExecuteRequest(BaseModel):
    code: str = Field(min_length=1, max_length=20000)
    data: dict = Field(default_factory=dict)
    timeout_s: int = Field(default=30, ge=1, le=120)
    memory_mb: int = Field(default=256, ge=64, le=1024)


class ExecuteResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    result: object = None


_WRAPPER = """\
import json as _json
_data = _json.loads({data_json!r})
data = _data
result = None
{user_code}
print("__RESULT__" + _json.dumps(result, default=str))
"""


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/execute", response_model=ExecuteResponse)
def execute(payload: ExecuteRequest) -> ExecuteResponse:
    import json

    wrapped = _WRAPPER.format(data_json=json.dumps(payload.data), user_code=payload.code)
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "snippet.py"
        target.write_text(wrapped)

        def _limits() -> None:
            try:
                mem = payload.memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
                resource.setrlimit(resource.RLIMIT_CPU, (payload.timeout_s, payload.timeout_s))
            except (OSError, ValueError):
                pass

        try:
            p = subprocess.run(
                [sys.executable, "-I", "-c", target.read_text()],
                capture_output=True,
                text=True,
                timeout=payload.timeout_s,
                check=False,
                preexec_fn=_limits,
                env={"PATH": "/usr/bin:/bin", "PYTHONNOUSERSITE": "1"},
            )
        except subprocess.TimeoutExpired as e:
            out = e.stdout if isinstance(e.stdout, str) else ""
            err = e.stderr if isinstance(e.stderr, str) else ""
            return ExecuteResponse(stdout=out, stderr=err, exit_code=124, timed_out=True)
    result: object = None
    lines: list[str] = []
    for line in p.stdout.splitlines():
        if line.startswith("__RESULT__"):
            try:
                result = json.loads(line[len("__RESULT__") :])
            except ValueError:
                result = None
        else:
            lines.append(line)
    return ExecuteResponse(
        stdout="\n".join(lines),
        stderr=p.stderr,
        exit_code=p.returncode,
        timed_out=False,
        result=result,
    )
