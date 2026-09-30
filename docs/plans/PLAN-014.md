# PLAN-014 opencode-go 原生协议

- 关联 REQ / Linked REQ：`docs/requirements/REQ-014.md`（AC1–AC5）。
- 范围 / Scope：`api/scripts/spike_opencode_go.py`（按需补候选形态）+ `api/src/services/provider_service.py`（按 `type` 分发的原生 URL/头/payload/解析 + 模块注释结论回写）+ `api/tests/test_model_providers.py`（原生单测）或新增 `api/tests/test_opencode_go_native.py`。不碰 models/controllers/schema/迁移/缓存语义/web/packages/ui/e2e；零新依赖。
- 架构 / Architecture：
  - S1 证据：以用户配好的 `opencode_go` 供应商为目标做 wire 探测（经本地 API，不经手 Key 明文；裸地址探测仅必要时用 `OPENCODE_GO_*` 单次注入）；按实测形态定原生路径（先 models 列表形态，后 chat 形态）；结论回写 service 模块注释。
  - S2 分发：`_models_url/_chat_url/_auth_headers` 按 `p.type` 分支（openai 分支逐行不动）；`fetch_models/test_connection/chat` 解析侧分支；失败回退语义沿用（列表空/check `ok:false`/chat 上抛）。
  - S3 真实验证：env 远端一次 `fetch_models`（或 `/test`），非空/`ok:true` 即过，证据（host、status、模型数、body 形态）记 TEST-014；远端只通 OpenAI 形态 → verdict downgrade 并终止 S2 写码（不留死代码）。
  - 脱敏：任何落盘物禁凭证明文；验证输出先过 `body_head ≤300 字符`（spike 脚本已有口径）。
- 开发步骤 / Steps：
  | Todo | 改动 | 验收 | 验证命令 |
  |---|---|---|---|
  | S1 | wire 探测 + 结论回写模块注释 | AC1 | 本地 API 供应商连通验证（+按需 `make spike-opencode-go`） |
  | S2 | 原生分发 + monkeypatch 单测（成功/回退） | AC2+AC4+AC5 前半 | `make lint type-check` + `make test TARGET_TESTS=./api/tests/test_model_providers.py` |
  | S3 | 用户供应商真实验证一次，证据记 TEST | AC3 | 连通 `ok:true` 或模型列表非空（经本地 API 一次，不进单测） |
  | S4 | 收尾：全门禁 + TEST-014 + 本地 commit | AC5 | `make lint type-check test` + `make openapi-check` + `pnpm -C e2e e2e:full -- --tags @smoke` |
- 风险 / Risks：R1 协议无公开文档 → 证据优先，无证据不写 client；R2 远端抖动/不可达 → live 只做证据，门禁以 mock 单测为准；R3 凭证明文泄露 → 环境变量单向注入，落盘前脱敏审计（`git diff` 扫 `KEY/key/token`）。
- 验证命令 / Verification：`make spike-opencode-go` / `make lint type-check test` / `make test TARGET_TESTS=./api/tests/test_model_providers.py` / `make openapi-check` / `pnpm -C e2e e2e:full -- --tags @smoke`。
