"""Python 代码执行正典实现（api owner）。S5 沙箱 HTTP 服务复用同一语义。
namespace：`data`（上游变量 dict，读）→ 必须 `result = ...`（写）。
无网络声明：本函数不提供 socket（S5 容器层再做 net=none）；超时杀死，内存限额。
"""

import resource
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExecResult:
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


def execute_code(*, code: str, data: dict, timeout_s: int = 30, memory_mb: int = 256) -> ExecResult:
    """受限执行用户代码；超时/超内存/异常均收敛为 ExecResult，不抛错。"""
    import json

    wrapped = _WRAPPER.format(data_json=json.dumps(data), user_code=code)
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "snippet.py"
        target.write_text(wrapped)

        def _limits() -> None:
            try:
                mem = memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
                resource.setrlimit(resource.RLIMIT_CPU, (timeout_s, timeout_s))
            except (OSError, ValueError):
                pass  # macOS 无 RLIMIT_AS/无权限时退化为仅 timeout（S5 容器层补足隔离）

        try:
            p = subprocess.run(
                [sys.executable, "-I", "-c", target.read_text()],
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
                preexec_fn=_limits,
                env={"PATH": "/usr/bin:/bin", "PYTHONNOUSERSITE": "1"},
            )
        except subprocess.TimeoutExpired as e:
            out = (e.stdout or "") if isinstance(e.stdout, str) else ""
            err = (e.stderr or "") if isinstance(e.stderr, str) else ""
            return ExecResult(stdout=out, stderr=err, exit_code=124, timed_out=True)
    result: object = None
    stdout_lines: list[str] = []
    for line in p.stdout.splitlines():
        if line.startswith("__RESULT__"):
            try:
                result = json.loads(line[len("__RESULT__") :])
            except ValueError:
                result = None
        else:
            stdout_lines.append(line)
    return ExecResult(
        stdout="\n".join(stdout_lines),
        stderr=p.stderr,
        exit_code=p.returncode,
        timed_out=False,
        result=result,
    )
