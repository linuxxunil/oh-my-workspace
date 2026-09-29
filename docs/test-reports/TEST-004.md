# TEST-004 PLAN-004 模型字段 + 密码两步走验收核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-004.md`（S1/S2A/S2B/S3，对应 `docs/requirements/REQ-004.md` AC1–AC4）
- 核验时间 / Date：2026-09-29（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`（`API_AUTO_MIGRATE=1`）；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`
- 本轮改动域（`git status` 实测）：`api/src/controllers/models.py`（`ProviderUpdateRequest` + PATCH 路由 + 409/400/404 映射）、`api/src/services/provider_service.py`（`update_provider`）、`api/src/controllers/auth.py` + `api/src/schemas.py` + `api/src/errors.py` + `api/src/services/auth_service.py`（`POST /auth/password` authn-only，`BadRequest`→400）、`api/tests/test_model_providers.py`（PATCH 用例追加）、`api/tests/test_auth_password.py`（新增 2 用例）、`web/src/views/ModelsView.vue`（新建 Key 栏 + 行内编辑地址/Key）、`web/src/views/UsersView.vue`（行内重置）、`web/src/views/AccountView.vue`（新增）+ `web/src/router/index.ts`（`/account`）+ `web/src/App.vue`（侧栏入口）+ `web/src/i18n/zh-CN.json` + `en-US.json`、`web/openapi.json` + `web/src/service/generated/api.ts` + `e2e/src/generated/api.ts`（双客户端重生成）、`e2e/features/workflow.smoke.feature`（换 Key 场景追加）、`e2e/features/password.feature`（新增 2 场景）+ `e2e/src/steps/password.steps.ts`（新增）+ `e2e/src/steps/models.steps.ts`（编辑步骤追加）+ `e2e/src/support/nav.ts`（`loginAs`/`logoutViaUI` + `/account` 映射）。`packages/ui/`、`e2e` 其余步骤、`web/src/views/CanvasView.vue` 本轮零 diff。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!`（exit 0） |
| V2 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 33 source files`（exit 0） |
| V3 | `make test TARGET_TESTS=./api/tests/test_model_providers.py` | 通过：`3 passed`（既有 2 + 新增 PATCH 用例 1） |
| V4 | `make test TARGET_TESTS=./api/tests/test_auth_password.py` | 通过：`2 passed`（三角色自改 + 管理员重置红线） |
| V5 | `make test`（全量） | 通过：`22 passed`（TEST-003 时 19 + 本轮新增 3，无失败；定点先行后全量仍绿，单测互相隔离见 Gaps-1） |
| V6 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（20→21：`/auth/password` 为新 path，PATCH 复用既有 `/models/providers/{provider_id}` path，计数一致） |
| V7 | `make web-check` | 通过：`pnpm --dir web exec vue-tsc --noEmit` 无输出（exit 0，含新增 `AccountView.vue`） |
| V8 | `make web-test` | 通过：`2 files / 6 tests passed`（旧单测仍绿） |
| V9 | `make ui-test` | 通过：`6 files / 17 tests passed`（`packages/ui` 本轮零改动，回归绿） |
| V10 | `make web-build` | 通过：`✓ built in 1.12s`（无报错） |
| V11 | `pnpm -C e2e e2e -- --tags @smoke` | 通过：`5 scenarios (5 passed)`，`34 steps (34 passed)`（2 旧 + 换 Key 1 + 密码 2，全绿） |
| V12 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`2 scenarios (2 passed)`，`10 steps (10 passed)`（登录页 + 画布页零 critical/serious，全绿） |
| V13 | 生成物 grep（只读）：`updateProviderModelsProvidersProviderIdPatch\|changePasswordAuthPasswordPost` | `web/src/service/generated/api.ts:18` 处、`e2e/src/generated/api.ts:5` 处（双客户端均已重生成，AC4 双客户端口径满足） |
| V14 | i18n 对照（只读）：`zh-CN.json` vs `en-US.json` 三组 key 集合 | `users` 8 键、`models` 11 键、`account` 7 键，中英 key 集合完全一致（含新增 `users.resetPassword/newPassword`、`models.apiKey/apiKeyHint/edit/save/cancel`、`account.*`） |
| V15 | 旧锚点 diff 审查（只读）：`git diff HEAD -- e2e/ web/src/i18n/` + `nav.ts` 全文 | 旧 feature/step 零修改（`workflow.smoke.feature` 纯追加 10 行；`models.steps.ts` 纯追加 12 行；`workflows.steps.ts`/`canvas.a11y.feature`/登录链零 diff）；`nav.ts` 的 `getByLabel('邮箱'/'密码')`、`getByRole('登录')` 锚点字符串一字未动，`loginViaUI` 语义等价转调 `loginAs`（同填 `browserEmail` + `E2E_PASSWORD`），`gotoSection` 函数体零改动；`LINKS` 仅新增 `/account` 一项。V11 全绿为旁证 |

## 逐条验收结论 / AC Verdicts（PLAN-004 S1/S2A/S2B → REQ-004 AC1–AC4）

- S1 模型 → AC1（PATCH 403/404/409/Key 留空均有单测；两类型均见三栏 + 行内编辑生效；`@smoke` 换 Key 场景绿）：**通过**（V3 单测一次断言 403/404/409/400/Key 替换连通带新 Key/空 Key 保持旧 Key/`api_key` 不在响应体；新建表单 `np-key` 字段与类型选择无关、两类型恒见三栏，见 `ModelsView.vue:80-91`；V11 换 Key 场景绿，编辑后连通性检查显示结果）。
- S2A 重置 → AC2（管理员行内重置后新密码 200/旧密码 401；admin 动 super_admin 仍 403）：**通过**（V11 密码重置场景绿：浏览器内重置→退出→新密码登录；V4 `test_admin_reset_member_password` 断言新密码可登录/旧密码 401/member 改他人 403/admin 动 super_admin 403）。
- S2B 自改 → AC3（三角色自改；旧密码错 400；改后新密码可登录；场景覆盖）：**通过**（V4 `test_self_change_password_all_roles` 覆盖 super_admin/admin/member：未登录 401、旧密码错 400、过短新密码 422、自改 204 + 新密码 200/旧密码 401；V11 自改场景绿：账号页改密→退出→新密码登录）。
- S3 收尾 → AC4（`openapi-check` 绿；双客户端重生成；i18n 中英同步；旧锚点零改动）：**通过**（V6 21 路由新鲜 + V13 双客户端均含新端点 + V14 三组 key 中英同构 + V15 旧锚点语义零改动）。
- PLAN-001/002/003 回归面 → **通过**（V1/V2/V5 后端门禁全绿 22 项 + V7/V8/V9/V10 前端门禁全绿 + V11/V12 `@smoke/@a11y` 全绿，视为回归通过；未重做 TEST-001 全部实况探针，见 Gaps）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据；Key 只收不返经单测锁定 `test_model_providers.py:104`）。
- P1：无（未见越权：PATCH 需 `models:write` 且 member 403 有单测；自改端点 authn-only 无 `require(...)`，见 `api/src/controllers/auth.py:28-42`；未见可见功能回退与公开契约错误，V11/V12 全绿）。
- P2：无。
- P3-1（功能完整性/对照 REQ 目标）：行内编辑未提供改名入口，后端 PATCH 的改名能力无前端路径。
  - 文件行号：`web/src/views/ModelsView.vue:29-56`（编辑表单仅 `ep-url` + `ep-key`，无名称栏）vs `api/src/services/provider_service.py:87-112`（`update_provider` 支持 `name`，改名冲突 409 有单测）vs `docs/requirements/REQ-004.md:7`（目标明示“改名/地址/Key”）。
  - 复现/证据：只读审查 + V11（换 Key 路径绿，改名路径前端不可达；改名仅 API 可达且单测覆盖）。
  - 影响面：当前验收不受影响（AC1“行内编辑保存生效”以地址/Key 为断言对象，已绿）；用户改名须走 API，属 REQ 目标未足额落地的尾巴。
  - 修复方向：在编辑表单追加名称栏（留空=不改，与 Key 语义对称）或在 REQ 明确改名前端延期至二期，并以 V11 回归验证（仅建议，不承揽）。
- P3-2（PLAN 架构偏离/可维护性）：`providerFields[type]` 按类型字段表未落地，实际为与类型无关的静态单字段。
  - 文件行号：`docs/plans/PLAN-004.md:8`（`providerFields[type]`，两类型同形、opencode_go hint 不同）vs `web/src/views/ModelsView.vue:80-91`（`np-key` 恒渲染，不读 `ptype`）+ `web/src/i18n/zh-CN.json`（`apiKeyHint` 单一文案，无按类型差异）。
  - 复现/证据：只读审查；功能等价（两类型恒见三栏，AC1 通过），opencode_go 专属 hint 无体现。
  - 影响面：功能无影响；后人按 PLAN 找字段表会落空，`extra_headers` 二期再开时需补回按类型分发表。
  - 修复方向：二选一——补 `providerFields` 表（两类型同形、hint 分写）或订正 PLAN-004 架构段为“静态单字段（首批同形）”，并以 V7/V11 回归验证（仅建议，不承揽）。
- P3-3（正确性收口/可访问反馈）：用户页行内重置失败无错误反馈，异常时抛未捕获 rejection。
  - 文件行号：`web/src/views/UsersView.vue:125-129`（`savePassword` 直接 `await mutateAsync`，无 try/catch、无 `role=alert`）vs `web/src/views/AccountView.vue:43-48,75-97`（同仓对照：`role=alert` + try/catch + `role=status`）。
  - 复现/证据：只读审查 + V4（admin 改 super_admin 403 仅单测覆盖；若经 UI 对 super_admin 行操作，请求 403 后表单无提示、控制台未捕获 rejection）。
  - 影响面：主流程正常时无感知（V11 重置场景绿）；红线/网络异常时管理员得不到“无权限/失败”提示，需看控制台。
  - 修复方向：照抄 `AccountView` 错误态（`error ref` + `role=alert` + catch 取 `detail`），失败时保持表单展开，并以 V11 回归验证（仅建议，不承揽）。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. 单测隔离性为间接证据：V4 改三种子账号密码后 V5 全量仍绿，推定 `client` fixture 隔离（sqlite/事务回滚）；未逐行审计 `api/tests/conftest.py` 本轮无 diff 即沿用旧隔离。
2. 两类型三栏的浏览器断言仅覆盖 `openai_compatible`（V11 换 Key 场景）；`opencode_go` 三栏以静态审查为据（字段与 `ptype` 无关故恒可见），无独立浏览器用例。
3. 旧密码错 400 与 admin 动 super_admin 403 仅单测覆盖，无浏览器负向场景（PLAN-004 S2A 原文“单测已覆盖只加 e2e”即此口径）。
4. a11y 沿用既有门禁：仅登录页 + 画布页、仅拦截 critical/serious；新增 `/account` 页与两处行内编辑表单未纳入 axe 扫描。
5. PLAN-001 回归为抽查口径：全量门禁 + `@smoke` + `@a11y` 全绿即视为通过，未重跑 TEST-001 V11–V19 全部实况探针。
6. 后端集成测试按仓约束默认只在 CI 跑：本地仅执行 `api/tests` 单测域（22 项）；DB 迁移幂等、并发改密/改 Key 竞态等长尾路径无覆盖。
7. `extra_headers` 后端 PATCH 已透传但前端未暴露，属 REQ-004 非目标（二期），不记为问题。
