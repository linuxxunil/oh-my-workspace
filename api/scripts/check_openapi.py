"""openapi 新鲜度门禁（PLAN-002 S1）：落盘 web/openapi.json 必须与当前 app.openapi() 一致。

分工：`make openapi` 负责生成，`make openapi-check` 负责校验（CI/本地门禁）。
用法：PYTHONPATH=api uv run --project api python api/scripts/check_openapi.py
"""

import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "web" / "openapi.json"


def main() -> int:
    from src.main import app

    current = json.dumps(app.openapi(), ensure_ascii=False, indent=2)
    if not SPEC.exists():
        print(f"FAIL: {SPEC} 不存在，先跑 make openapi 生成")
        return 1
    committed = SPEC.read_text()
    if committed == current:
        routes = len(app.openapi()["paths"])
        print(f"OK: web/openapi.json 新鲜（{routes} 路由）")
        return 0
    diff = difflib.unified_diff(
        committed.splitlines(), current.splitlines(), "committed", "current", lineterm=""
    )
    print("FAIL: web/openapi.json 过期，先跑 make openapi 重生成")
    for line in list(diff)[:40]:
        print(line)
    return 1


if __name__ == "__main__":
    sys.exit(main())
