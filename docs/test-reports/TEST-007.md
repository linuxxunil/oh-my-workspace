# TEST-007 PLAN-007 extra_headers 端到端暴露核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-007.md`（S1/S2/S3/S4，对应 `docs/requirements/REQ-007.md` AC1–AC4）
- 核验时间 / Date：2026-09-29（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`（本轮改动已含）；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`
- 本轮改动域（`git diff HEAD --stat` 实测，共 +282/−32）：`api/src/services/provider_service.py`（+23：`_check_extra_headers` helper + create/update 接入）+ `api/tests/test_model_providers.py`（+63：`test_extra_headers_validation_and_passthrough`）+ `web/src/views/ModelsView.vue`（+99：新建 `headers` + 编辑 `editHeaders` 两套 KV 行编辑器 + `headersObject` + create/save 接入）+ `web/src/i18n/zh-CN.json` + `en-US.json`（各 +7）+ `e2e/src/steps/models.steps.ts`（+103/−29：原新建体下沉 `createProviderViaForm` + 附带自定义头新步骤 + 打开编辑/不回显两步）+ `e2e/features/provider.feature`（+12：纯新增一场景）。`ProviderResponse`、矩阵、画布、基元库零 diff。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!`（exit 0） |
| V2 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 33 source files`（exit 0） |
| V3 | `make test`（全量） | 通过：`24 passed`（TEST-006 基线 23 + 本轮 `test_extra_headers_validation_and_passthrough` 1，无失败；既有用例回归绿） |
| V4 | `make test TARGET_TESTS=./api/tests/test_model_providers.py` | 通过：`5 passed`（本文件 4 既有用例 + 1 新增；400×4 种 + 透传 + 替换/保持 + 非法 PATCH 旧头保持均在同一用例内断言） |
| V5 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0；`ProviderResponse` 零变更下更须绿） |
| V6 | `make web-check` | 通过：`pnpm --dir web exec vue-tsc --noEmit` 无输出（exit 0，含 `ModelsView.vue` 新增 `headers`/`editHeaders`/`headersObject`） |
| V7 | `make web-test` | 通过：`2 files / 6 tests passed`（回归绿） |
| V8 | `make ui-test` | 通过：`6 files / 17 tests passed`（`packages/ui` 本轮零改动，回归绿） |
| V9 | `make web-build` | 通过：`✓ built in 1.29s`（`ModelsView` chunk 8.20 kB，AC2 构建口径） |
| V10 | `pnpm -C e2e e2e -- --tags @smoke` | 通过：`8 scenarios (8 passed)`，`57 steps (57 passed)`（TEST-006 基线 7 → 8，本轮 1 新场景全绿，旧 7 场景无回退） |
| V11 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`2 scenarios (2 passed)`，`10 steps (10 passed)`（回归绿） |
| V12 | 旧锚点审查（只读）：`git diff HEAD -- e2e/features/provider.feature`（删行数）+ 新旧步骤正则对照 | `provider.feature` diff 仅 `+12`、零删行（旧两场景逐字未动）；`models.steps.ts` 旧步骤正则 `'新建供应商 类型 {string} 名称以 {string} 为前缀 地址 {string}'` 字面未变，原实现体逐行下沉 `createProviderViaForm`（删行即搬移，`headers` 默参 `[]` 时旧路径行为一致），新增为独立正则（`附带自定义头 {string} 值为 {string}`）+ `打开该供应商的编辑` / `编辑表单不回显自定义头` 两步；`e2e/` 下无其他 tracked 改动 |
| V13 | i18n 对照（只读）：`models` 命名空间 key 集对称性 | `zh-CN` 与 `en-US` 的 `models` key 集完全相等（新增 7 键两侧齐备：`headers`/`headersHintCreate`/`headersHintEdit`/`headerKey`/`headerValue`/`headerAdd`/`headerRemove`，无单边键）；编辑 hint 中英语义一致（`留空=保持不变；填写=整体替换旧头；只收不返` / `Empty = keep; filled = replace all; write-only`） |
| V14 | Response 零变更审查（只读）：`api/src/controllers/models.py:25-30` | `ProviderResponse` 仍仅 `id/type/name/base_url/is_active` 五字段，无 `extra_headers`/`api_key` 回显；`_to`（`:41-44`）未动；V5 绿佐证无 schema 漂移 |

## 逐条验收结论 / AC Verdicts（PLAN-007 S1/S2/S3 → REQ-007 AC1–AC4）

- S1 后端校验 → AC1（`authorization` 大小写不敏感→400；非法键名→400；值超长/超条数→400；合法头透传且 `Authorization` 不被顶掉；PATCH 整体替换；既有用例回归绿）：**通过**（`provider_service.py:44-60` helper：键 `^[A-Za-z0-9-]+$`、禁 `authorization`（`k.lower()`）、值 ≤1024、≤20 条，非法抛 `ValueError`；`:83` create 先验后存、`:173-175` update 仅 `is not None` 时验并替换；`controllers/models.py:75-77` create 与 `:104-105` update 的 `ValueError→400` 为既有通道，未新开异常映射；`test_model_providers.py:183-240` 断言 `Authorization/authorization/AUTHORIZATION` 三变体 400 + 非法键名/1025 长值/21 条各 400 + 201 且响应无 `extra_headers` + monkeypatch `_http_get` 透传断言含 `X-Custom`/`X-Api-Key` 且无 `Authorization` 注入 + PATCH 替换后旧头消失 + 不带 `extra_headers` 的 PATCH 保持 + 非法 PATCH 400 且旧头保持；V3/V4 全绿）。
- S2 前端 KV → AC2（新建+编辑均有 KV 行编辑器，增/删行，空行忽略；hint 写清留空=保持、填写=整体替换；`models.*` 文案中英同步；头值 password 型输入）：**通过**（`ModelsView.vue:68-103` 编辑区 `editHeaders` + `138-166` 新建区 `headers`：各有 `加一行`/`删`、头名/头值双输入、头值 `type="password" + autocomplete="new-password"`；`:213-223` `headersObject` trim 键、空键行跳过、全空返 `undefined`（新建=不带，编辑=保持）；`:234-249` create 接入、`：274-289` save 接入、`：271-285` `toggleEdit` 打开编辑时 `editHeaders` 从空开始（只收不返、无法回显）；`:70/:140` hint 分别引用 `headersHintEdit`/`headersHintCreate`；V13 中英 key 集对称；V6/V9 类型与构建绿）。
- S3 e2e 新场景 → AC3（新场景绿；旧锚点零改动）：**通过**（V10 8 场景全绿，基线 7→8；`provider.feature` 新增场景“建供应商附带自定义头后连通性正常且编辑不回显”经浏览器 KV 行编辑器填头（`models.steps.ts:30-47` 新步骤 + `createProviderViaForm:55-95` 的 `加一行`/`头名`/`头值` 填行动线）→ 列表断言 → 连通性 → 打开编辑 → `头名` 输入框计数为 0（`:103-107`）；V12 旧 feature 零删行、旧步骤正则字面未变）。
- S4 收尾 → AC4（`ProviderResponse` 不动，`openapi-check` 绿；i18n 同步）：**通过**（V14 Response 五字段未动、`_to` 未动；V5 21 路由新鲜；V13 key 集对称；PLAN-001~006 回归面：V1/V2/V3/V4 后端门禁全绿 + V6/V7/V8/V9 前端门禁全绿 + V10/V11 `@smoke/@a11y` 全绿，视为回归通过）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据；`authorization` 禁写大小写不敏感，`_auth_headers`（`provider_service.py:30-33`）在无 api_key 时不产生 `Authorization` 头，单测已断言无注入）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；`require("models:write")` 沿用，`ProviderResponse` 零变更，V10/V11 全绿）。
- P2：无。
- P3：无（本次为 AC 口径核验，非全面审计，不展开轻微清理项；已识别的边际项见 Gaps，如实记录为非缺陷）。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. 透传断言的字面组合缺口：单测建供应商时未设 `api_key`，故透传断言为“含自定义头且无 `Authorization` 注入”（`test_model_providers.py:225-230`），未覆盖“`api_key` 非空时 `Authorization == Bearer <key>` 与自定义头并存”的 AC1 字面组合；因写入层已禁 `authorization`（含大小写）且 `_auth_headers` 先置 Bearer，旁路概率低。
2. 存量脏数据未验证：`_auth_headers`（`provider_service.py:30-33`）为先置 Bearer 后 `update(extra_headers)`，若校验上线前已存在小写 `authorization` 键的行（或绕 service 直接写库），字典将同时存在两键，httpx 大小写不敏感合并行为未定；本轮无存量清洗/迁移（非 AC 口径），记录备查。
3. 编辑提交替换的浏览器实证缺口：e2e 新场景覆盖“新建填头→连通性→编辑无回显”，未覆盖“编辑填头→保存→透传新头”的浏览器路径；编辑替换语义由单测 PATCH 层 + `headersObject`（`ModelsView.vue:213-223`）静态审查覆盖。
4. PLAN-001~005 回归为抽查口径：全量门禁 + `@smoke` + `@a11y` 全绿即视为通过，未重跑 TEST-001 全部实况探针。
5. 后端集成测试按仓约束默认只在 CI 跑：本地仅执行 `api/tests` 单测域（24 项）。
