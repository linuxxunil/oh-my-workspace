"""opencode-go 原生协议 spike（PLAN-002 S2，收敛 PLAN-001 R1）。

只读探测，无业务副作用（不写库、不改配置）。
输入（环境变量，均可选）：
  OPENCODE_GO_BASE_URL  待测远端地址（无则直接给 downgrade 结论，不伪造验证）
  OPENCODE_GO_API_KEY    远端凭证（可空）
探测顺序：OpenAI-compatible wire（GET {base}/models）→ 候选原生形态。
退出码：0=探测完成并给出结论；1=脚本自身异常。
用法：PYTHONPATH=api uv run --project api python api/scripts/spike_opencode_go.py
"""

import json
import os
import sys

import httpx

# 候选原生形态（opencode-go 无公开协议文档，只能逐个试并如实记录）。
NATIVE_CANDIDATES = ["/api/models", "/api/v1/models", "/v1/models"]


def _probe(method: str, url: str, headers: dict, timeout_s: float = 10.0) -> dict:
    try:
        r = httpx.request(method, url, headers=headers, timeout=timeout_s)
        body = r.text[:300]
        return {"url": url, "status": r.status_code, "body_head": body}
    except Exception as e:  # noqa: BLE001 -- spike 要求把失败收敛为记录而非抛错
        return {"url": url, "status": None, "body_head": f"{type(e).__name__}: {e}"}


def main() -> int:
    base = (os.environ.get("OPENCODE_GO_BASE_URL") or "").rstrip("/")
    api_key = os.environ.get("OPENCODE_GO_API_KEY") or ""
    if not base:
        verdict = {
            "verdict": "downgrade",
            "reason": "no-credentials",
            "detail": "未提供 OPENCODE_GO_BASE_URL，无法验证原生协议；维持 OpenAI-compatible 承载（见 provider_service 模块注释）",
        }
        print(json.dumps(verdict, ensure_ascii=False, indent=2))
        return 0

    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    probes = [_probe("GET", base + "/models", headers)]
    native_hit = None
    for path in NATIVE_CANDIDATES:
        if path == "/v1/models" and base.endswith("/v1"):
            continue
        try:
            r = httpx.get(base + path, headers=headers, timeout=10.0)
            rec = {"url": base + path, "status": r.status_code, "body_head": r.text[:300]}
            if r.status_code == 200:
                try:
                    data = r.json()
                except Exception:  # noqa: BLE001 -- 非 JSON 即不算模型列表形态
                    data = None
                if isinstance(data, dict) and ("data" in data or "models" in data):
                    native_hit = path
        except Exception as e:  # noqa: BLE001 -- spike 要求把失败收敛为记录而非抛错
            rec = {"url": base + path, "status": None, "body_head": f"{type(e).__name__}: {e}"}
        probes.append(rec)

    compatible_ok = probes[0]["status"] == 200
    if native_hit:
        verdict = {
            "verdict": "native-candidate",
            "reason": f"{native_hit} 返回模型列表形态，需人工确认后加原生 client",
            "probes": probes,
        }
    elif compatible_ok:
        verdict = {
            "verdict": "downgrade",
            "reason": "仅 OpenAI-compatible wire 可用，维持现状",
            "probes": probes,
        }
    else:
        verdict = {"verdict": "downgrade", "reason": "远端不可达，维持现状", "probes": probes}
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001 -- 顶层兜底，保证退出码语义
        print(json.dumps({"verdict": "error", "reason": str(e)[:300]}, ensure_ascii=False))
        sys.exit(1)
