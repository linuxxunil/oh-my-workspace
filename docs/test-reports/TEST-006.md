# TEST-006 PLAN-006 供应商删除补齐 + 绑定拒绝验收核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-006.md`（S1/S2/S3/S4，对应 `docs/requirements/REQ-006.md` AC1–AC4）
- 核验时间 / Date：2026-09-29（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`（`API_AUTO_MIGRATE=1`）；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`
- 本轮改动域（`git status` + `git diff --stat HEAD` 实测）：`api/src/services/provider_service.py`（+40/−2：`_referencing_workflows` + `_latest_dag` + `delete_provider` 引用检查）+ `api/src/controllers/models.py`（+2：`Conflict→409`）+ `api/tests/test_model_providers.py`（+52：403/204/409 单测）+ `web/src/views/ModelsView.vue`（+29：行删除键 + `remove` + `rowErrors` alert）+ `web/src/i18n/zh-CN.json` + `en-US.json`（各 +2：`models.delete/confirmDelete`）+ `e2e/src/steps/models.steps.ts`（+29）+ `e2e/src/support/api.ts`（+26：`createWorkflowWithLlm`）+ `e2e/features/provider.feature`（untracked 新文件，2 场景）。矩阵、画布、基元零 diff。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!`（exit 0） |
| V2 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 33 source files`（exit 0） |
| V3 | `make test`（全量） | 通过：`23 passed`（TEST-005 基线 22 + 本轮 `test_delete_provider_bound_by_latest_version_returns_409` 1，无失败；既有 `PATCH` 等用例回归绿） |
| V4 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0，无 schema 变更下更须绿） |
| V5 | `make web-check` | 通过：`pnpm --dir web exec vue-tsc --noEmit` 无输出（exit 0，含 `ModelsView.vue` 新增 `remove`/`rowErrors`） |
| V6 | `make web-test` | 通过：`2 files / 6 tests passed`（`dag.spec.ts` 3 + `mutator.spec.ts` 3，回归绿） |
| V7 | `make ui-test` | 通过：`6 files / 17 tests passed`（`packages/ui` 本轮零改动，回归绿） |
| V8 | `make web-build` | 通过：`✓ built in 1.24s`（`ModelsView` chunk 5.71 kB，AC2 构建口径） |
| V9 | `pnpm -C e2e e2e -- --tags @smoke` | 通过：`7 scenarios (7 passed)`，`48 steps (48 passed)`（基线 5 → 7，本轮 2 新场景全绿） |
| V10 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`2 scenarios (2 passed)`，`10 steps (10 passed)`（回归绿） |
| V11 | 旧锚点审查（只读）：`git diff HEAD --name-only -- e2e/` + `git diff HEAD -- e2e/features/` | 仅 `e2e/src/steps/models.steps.ts`（+29 纯新增）+ `e2e/src/support/api.ts`（+26 纯新增）；`e2e/features/` 下 diff 为空（`provider.feature` 为 untracked 新文件），旧 feature/steps 零改动 |
| V12 | i18n 对照（只读）：`zh-CN.json:33-34` vs `en-US.json:33-34` | `models.delete`（删除/Delete）+ `models.confirmDelete`（`确定删除供应商 {name}？`/`Delete provider {name}?`）中英 key 集合对称、`{name}` 插值两侧一致 |

## 逐条验收结论 / AC Verdicts（PLAN-006 S1/S2/S3 → REQ-006 AC1–AC4）

- S1 后端检查 → AC1（被引用删→409 且供应商仍在；无引用→204；member→403；既有用例回归绿）：**通过**（`provider_service.py:83-89` 先查后删、`:92-106` 扫本租户各流程最新版本 `llm.provider_id`、`models.py:119-120` `Conflict→409`；`test_model_providers.py:139-144` 断言 403/204、`：176-179` 断言 409 + `detail` 含 `w-bound` + 列表仍含该供应商；V3 全量 23 项绿）。
- S2 前端删除 → AC2（删除键存在；confirm 取消不删；确认删后列表消失；被引用时红字出现且行仍在）：**通过**（`ModelsView.vue:19-21` 行删除键 `models.delete`、`：171-173` `window.confirm(t('models.confirmDelete', {name}))` 取消即返、`：174-184` 409 `detail` 进 `rowErrors[id]` + 成功 `invalidateQueries` 刷新、`：31-37` `role=alert` 红字行；V5/V8 类型与构建绿 + V9 两新场景浏览器实证）。
- S3 e2e 两场景 → AC3（新增“删除”与“被引用拒绝”两场景绿；旧锚点零改动）：**通过**（V9 7 场景全绿；`provider.feature:8-14` 无引用删除后消失、`：17-25` 引用后拒绝且行仍在；`models.steps.ts:73-100` 删除/消失/准备引用/拒绝四步、`api.ts:67-91` `createWorkflowWithLlm` 准备层；V11 旧锚点零改动：steps/support 均为纯新增，features 无 tracked 改动）。
- S4 收尾 → AC4（i18n 中英同步；`openapi-check` 绿）：**通过**（V12 两键中英对称 + 插值一致；V4 21 路由新鲜；PLAN-001~005 回归面：V1/V2/V3 后端门禁全绿 + V5/V6/V7/V8 前端门禁全绿 + V9/V10 `@smoke/@a11y` 全绿，视为回归通过）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据；409 文案仅含同租户流程名，`provider_service.py:96` 以 `tenant_id` 过滤，无跨租户泄露）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；member→403、`require("models:write")` 沿用见 `models.py:111`；V9/V10 全绿）。
- P2：无。
- P3：无（本次为 AC 口径核验，非全面审计，不展开轻微清理项）。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. AC2 的“confirm 取消不删”路径仅静态代码审查（`ModelsView.vue:173` 取消即返），无浏览器端到端用例；V9 两场景均走 `dialog accept` 路径（`models.steps.ts:76` `page.once('dialog', accept)`）。
2. 脏版本跳过逻辑（`provider_service.py:119-122` `ValidationError→None`）无专项单测；单测仅覆盖合法最新版本引用与无引用两态，未构造脏版本断言“不挡删除”。
3. 历史版本引用不检查为 REQ 非目标（快照不管），本轮未验证“旧版本引用、新版本已解绑→允许删除”的边界态；实现按 `version_no.desc().first()` 只取最新，与约束一致。
4. PLAN-001~004 回归为抽查口径：全量门禁 + `@smoke` + `@a11y` 全绿即视为通过，未重跑 TEST-001 全部实况探针。
5. 后端集成测试按仓约束默认只在 CI 跑：本地仅执行 `api/tests` 单测域（23 项）。
