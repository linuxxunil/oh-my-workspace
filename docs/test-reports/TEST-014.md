# TEST-014 PLAN-014 opencode-go 原生协议核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-014.md`（S1–S4，对应 `docs/requirements/REQ-014.md` AC1–AC5）。
- 核验时间 / Date：2026-09-30（UTC）
- 环境快照 / Env：未重起服务；后端单测直跑（sqlite），e2e 经 `e2e:full`（reset + 确定性全量）。
- 本轮改动域（PLAN-014 部分，`git diff` 实测）：`api/src/services/provider_service.py:1-7` 模块注释结论回写 1 处（S1 证据）；`docs/requirements/REQ-014.md` + `docs/plans/PLAN-014.md`（新增计划文档）。S2/S3 结论为 downgrade（远端仅通 OpenAI 形态），故零原生 client 代码、零单测新增。
- 树上另有未提交 PLAN-012 遗留改动（`api/src/libs/crypto.py` 新增、`api/src/config.py`、`api/src/models.py:api_key 1024→2048`、`api/alembic/versions/0002_api_key_2048.py`、`api/tests/test_crypto.py` + `test_model_providers.py` 内加密用例、`docker/envs/api.env.example`、`docs/release.md` 等），dev 库已在 0002（head）；本报告只按 PLAN-014 的 AC verdict，PLAN-012 归属 TEST-012。`provider_service.py` 内 `_auth_headers`/`create_provider`/`update_provider` 的加解密行即 PLAN-012 改动，不计入 PLAN-014。

## 验证命令与结果 / Verification

| # | 命令（仓根，只读） | 结果 |
|---|---|---|
| V1 | `make spike-opencode-go`（无凭证） | 通过：stdout `{"verdict":"downgrade","reason":"no-credentials","detail":"未提供 OPENCODE_GO_BASE_URL…"}`（exit 0，无伪造验证） |
| V2 | `OPENCODE_GO_BASE_URL=http://127.0.0.1:9 make spike-opencode-go`（本地回环，不出外网） | 通过：`{"verdict":"downgrade","reason":"远端不可达，维持现状"}`，4 个端点（`/models` + 3 候选原生形态）均为 `ConnectError: [Errno 61] Connection refused`（exit 0） |
| V3 | `make test TARGET_TESTS=./api/tests/test_model_providers.py` | 通过：`6 passed`（含 PLAN-012 新增加密用例 1；PLAN-014 零新增单测，符合 downgrade 约定） |
| V4 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!`（exit 0） |
| V5 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 34 source files`（exit 0） |
| V6 | `make test`（全量） | 通过：`34 passed`（7 文件：auth 2、crypto 5、knowledge 4、providers 6、rbac 7、sandbox 6、workflow 2；exit 0） |
| V7 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0；零 schema 改） |
| V8 | `pnpm -C e2e e2e:full -- --tags @smoke`（首轮） | 偶发 1 败：`12 scenarios (1 failed, 11 passed)`，`82 steps (82 passed)` 全过；败因系场景「更换供应商 API Key 后连通性检查仍可用」的 `After` hook（`e2e/src/support/hooks.ts:28-35`：tracing 停止 + `runCleanups` + context 关闭）30s 超时，非步骤断言失败 |
| V9 | `pnpm -C e2e e2e:full -- --tags @smoke`（重放） | 通过：`12 scenarios (12 passed)`，`82 steps (82 passed)`（约 13s；V8 判为 teardown 偶发抖动，见 P3-2） |
| V10 | 源码阅读 + 泄露扫描（只读） | `provider_service.py:1-7` 注释断言与 `spike_opencode_go.py:19/44-61` 探测逻辑一致（见 AC1）；`_models_url:41-42`、`_chat_url:45-46`、`_auth_headers:33-38` 均无 `p.type` 分支（`grep p.type` 零命中；`ProviderType` 仅 `create_provider:81` 签名引用）；`_http_get:24`、`_http_post:29`、`create_provider:87`、`update_provider:174` 仍经 `assert_safe_url`；`git diff` 扫 `KEY/key/token` 仅命中 PLAN-012 测试固件（`test_model_providers.py` 内 `"super-secret"` / `"legacy-plain"` / `"Bearer legacy-plain"` 断言），无真实凭证明文、无 `sk-` 形态、无落盘 Key |

## 逐条验收结论 / AC Verdicts（REQ-014 AC1–AC5）

- AC1 spike 证据（wire 探测 + verdict 回写注释 + 落盘物脱敏）：**通过**。注释（`provider_service.py:2-5`）记 host（`https://opencode.ai/zen/go/v1`）、`GET {base}/models 200 标准 list 形态（30 模型）`、` /api/models`、`/api/v1/models 均为 404`、verdict `downgrade`；与脚本逻辑一致：base 以 `/v1` 结尾时 `spike_opencode_go.py:47-48` 跳过 `/v1/models`（与 `/models` 同义去重），故实际探测集恰为注释所列 3 端点；输出口径 `body_head ≤300 字符`（`:25/:51`）满足截断约束；V1/V2 确认脚本无凭证不伪造验证；V10 确认落盘物无凭证明文。但注释所载 `30 模型 / 404` 实测数值为 build 期 S1 远端探测结果，tester 无凭证不可重放（禁贴禁试 Key 明文），仓内亦无原始 spike 输出落盘，故该数值本身只能做一致性核验而非独立复现（见 Gaps）。
- AC2 原生分发（三调用点按 `type` 分发 + 成功/回退单测）：**不适用（downgrade 豁免）**。按 PLAN-014 S3 与 REQ-014 AC3 约定，远端仅通 OpenAI 形态时终止 S2 写码、不留死代码；实测 `_models_url/_chat_url/_auth_headers` 无 `p.type` 分支、零原生 client 代码、零新增单测，正符合约定，不记为缺失。
- AC3 真实验证（用户供应商一次真实验证，证据记 TEST；仅通 OpenAI 形态则 downgrade）：**通过（downgrade 路径）**。注释回写即 S3 证据载体（host、status、模型数、body 形态四要素齐：地址 + 200 + 30 模型 + 标准 list/404 形态）；未写推测性 client 代码（V10 源码确认）。同 AC1，远端真实验证不可重放，见 Gaps。
- AC4 通道隔离（`openai_compatible` 行为零变化，`test_model_providers` 全绿即证）：**通过**（V3 `6 passed`；V6 全量 `34 passed` 无回退；wire 路径无 `type` 分支，`openai_compatible` 逐行未动）。
- AC5 红线（全门禁 + openapi-check + `@smoke` + 出站全经 `assert_safe_url`）：**通过**（V4/V5/V6 全绿；V7 `21 路由`新鲜即零 schema 改；V9 `@smoke 12/12`；V10 确认出站 4 处仍经 `assert_safe_url`，内网地址单测沿用既有覆盖）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据；V10 泄露扫描无真实凭证明文）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；V6/V9 全绿）。
- P2：无。
- P3-1（注释完备性）：模块注释只列被探测的 2 个候选原生形态（`/api/models`、`/api/v1/models` 404），未说明脚本第三候选 `/v1/models` 因 base 以 `/v1` 结尾被 `spike_opencode_go.py:47-48` 跳过。读者对照 `NATIVE_CANDIDATES:19` 三候选时可能误以为少测一处。
  - 文件行号：`api/src/services/provider_service.py:4`；对照 `api/scripts/spike_opencode_go.py:19,47-48`。
  - 影响范围：仅注释阅读体验，无行为影响；探测集本身正确（`/v1/models` 与 `/models` 同义）。
  - 修复建议（不代写实现，仅建议）：注释末补半句，如「（`/v1/models` 因 base 以 `/v1` 结尾被脚本去重跳过）」。
- P3-2（观察项，非缺陷）：V8 首轮 `@smoke` 1 败为 `After` hook teardown 30s 超时（82 步骤全过，失败场景恰为触及 PLAN-012 加解密路径的 Key 轮换场景），V9 原样重放 12/12 全绿，判为偶发抖动。如后续复现且集中于 cleanup 超时，建议另起任务排查 `runCleanups` 在 0002 加密库下的耗时，而非归入 PLAN-014。
  - 文件行号：`e2e/src/support/hooks.ts:28-35`（`setDefaultTimeout(30_000)` 见 `:11`）。
  - 影响范围：仅 e2e teardown 稳定性；被测行为断言不受影响。

## 验证盲区 / Gaps

1. 有凭证远端探测不可重放：tester 全程未持有 Key（符合 REQ-014 约束），注释中 `200 / 30 模型 / 双 404` 数值仅与脚本逻辑做一致性核对，未独立复现；且仓内无 S1 原始 spike 输出落盘（如脱敏后的 probes JSON），后人无法对账。建议未来 S1 将脱敏 verdict（含 probes 状态码与 body 形态摘要）贴入 TEST 报告正文。
2. PLAN-012 混叠：工作树含未提交 PLAN-012 改动且 dev 库已在 0002；本报告 V3/V6/V8 结果均在此混合树上取得。PLAN-014 自身改动仅为注释 1 处（行为零变化），故混合不影响上述 verdict；但 `test_crypto`、0002 迁移、`api_key` 加解密语义的 verdict 归属 TEST-012。
3. 出站探测仅用无凭证 spike（V1/V2）与本地只读查询；未对 `https://opencode.ai/zen/go/v1` 发起任何tester 侧出站请求。
