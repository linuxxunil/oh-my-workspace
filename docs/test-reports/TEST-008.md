# TEST-008 PLAN-008 画布页 UX 整体优化核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-008.md`（S1/S2/S3/S4，对应 `docs/requirements/REQ-008.md` AC1–AC4）
- 核验时间 / Date：2026-09-29（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`
- 本轮改动域（`git diff HEAD --stat` 实测，共 +175/−54）：`web/src/views/CanvasView.vue`（+189/−54 行计：双栏布局 + 右侧 aside 面板 + 运行历史区 + 运行区基元化 + confirm + 高度自适应）+ `web/src/i18n/zh-CN.json` + `en-US.json`（各 +12 键）+ `e2e/src/steps/workflows.steps.ts`（+11：关面板两行 + 历史断言一步）+ `e2e/features/workflow.smoke.feature`（+1：历史断言行）。`api/`、`packages/ui/`、dialog 基元、列表页零 diff。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!`（exit 0） |
| V2 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 33 source files`（exit 0） |
| V3 | `make test`（全量） | 通过：`24 passed`（与 TEST-007 基线一致，无失败；本轮无后端改动，回归绿） |
| V4 | `make web-check` | 通过：`pnpm --dir web exec vue-tsc --noEmit` 无输出（exit 0，含 `CanvasView.vue` 新增 `runs`/`loadRuns`/`formatOutputs` + `Badge`/`RunResponse` 引入） |
| V5 | `make web-test` | 通过：`2 files / 6 tests passed`（回归绿） |
| V6 | `make ui-test` | 通过：`6 files / 17 tests passed`（`packages/ui` 本轮零改动，回归绿） |
| V7 | `make web-build` | 通过：`✓ built in 1.31s`（`CanvasView` chunk 231.93 kB，AC1 构建口径） |
| V8 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0，AC4 口径） |
| V9 | `pnpm -C e2e e2e -- --tags @smoke` | 通过：`8 scenarios (8 passed)`，`58 steps (58 passed)`（TEST-007 基线 8 场景 57 步 → 本轮 58 步，新增历史断言步全绿，旧 57 步无回退） |
| V10 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`2 scenarios (2 passed)`，`10 steps (10 passed)`（登录页 + 画布页零 critical/serious，回归绿） |
| V11 | 旧锚点核对（只读）：`e2e/src/steps/workflows.steps.ts` 定位串 vs `CanvasView.vue` + `zh-CN.json` 渲染值 | 全部保留：`打开画布`（`:86` 未动）/ `+ code`（`:90` 未动）/ `保存配置`（`:98` 未动；模板 `:130` 改走 `canvas.saveConfig` 但渲染值仍为 `保存配置`，V9 绿实证命中）/ `ok`（`:99` vs `:372` `notice='ok'` 未动）/ `保存版本`（`:122` 未动；模板 `:137` 改走 `canvas.saveVersion` 但渲染值仍为 `保存版本`，V9 绿实证）/ `saved`（`:123` vs `:399` 未动）/ `发布`+`published`（`:129-130` vs `:138/:404` 未动）/ `输入 JSON`（`:131` vs `flows.inputs` 未动）/ `outputs`（`:149` `getByLabel('outputs')` vs `:156` `aria-label="outputs"` 未动）/ `role=status`（`:139` 未动） |
| V12 | i18n 对照（只读）：`zh-CN.json` vs `en-US.json` 的 `canvas` key 集 + 模板硬编码扫描 | `canvas` key 集完全对称（28 键，双方 `missing` 均为空；新增 12 键两侧齐备：`nodePanel/deleteSelected/configPanel/nodeConfig/closePanel/saveConfig/saveVersion/confirmRemoveNode/invalidInputs/runHistory/noRuns/runOutputs`）；`rg` 扫描 `CanvasView.vue` 模板中文硬编码（`删除选中\|保存配置\|保存版本\|inputs JSON\|节点 \|确定删除`）零命中；`saveConfig/saveVersion/deleteSelected` 中文渲染值与旧锚点逐字一致（`保存配置`/`保存版本`/`删除选中`） |
| V13 | 零后端审查（只读）：`git diff -- api/` + `git status --short -- api/` | 输出为空（0 行 diff，`api/` 无 tracked/untracked 变动）；V8 21 路由新鲜佐证无 schema 漂移 |
| V14 | Badge 契约审查（只读）：`packages/ui/src/badge/Badge.vue:14-24` | `BadgeTone` 含 `green \| red`，`tones` 映射齐备（`green→bg-green-50/text-green-700`，`red→bg-red-50/text-red-700`）；`CanvasView.vue:172` 的三元 `succeeded→green/else→red` 落在契约内；`indigo`（`:37` 面板头类型 Badge）同为合法 tone |

## 逐条验收结论 / AC Verdicts（PLAN-008 S1/S2/S3/S4 → REQ-008 AC1–AC4）

- S1 布局重构 → AC1（右侧面板随选中出现/收起，画布高度自适应，`web-build` 通过）：**通过**（`CanvasView.vue:15-16` `flex items-stretch` 双栏、左画布 `min-w-0 flex-1`、右 `aside w-80 shrink-0` 以 `v-if="selectedNode"`（`:32`）收起、关闭键 `:41-48` 置 `selectedNode = null`；画布高度 `:423-424` `calc(100vh - 340px) + min-height 420px` 替代 480px 写死；h1 `:3-6` `flows.title` + `font-mono text-xs text-slate-600` workflowId 截断展示；`fit-view-on-init`（`:24`）保留；V4 类型绿 + V7 构建绿）。
- S2 i18n 补漏 + 删除确认 + 运行区基元化 → AC2（画布页零硬编码，`canvas.*` 中英对称；删除节点有 confirm）：**通过**（V12：28 键对称、模板零硬编码、旧锚点逐字一致；删除 `removeSelected`（`:347-355`）经 `window.confirm(t('canvas.confirmRemoveNode', {id}))` 二次确认、取消即返，PLAN-006 同款模式；运行区 `:141-153` `Field + Textarea` 基元化（`input-id="run-inputs"`，`flows.inputs` label 保留）；`role=status`（`:139`）与 `aria-label="outputs"`（`:156`）锚点保留，V11 逐项核对）。
- S3 运行历史 + S4 e2e 同步 → AC3（run 后列表出现该次记录；`@smoke` 编排场景绿、`@a11y` 绿）：**通过**（历史区 `:159-186`：`runs-title` heading + `Badge`（status 精确文本，绿/红）+ `error` 摘要（`:175`）+ `details/summary` 展开 outputs（`:176-183`，`formatOutputs` JSON -safe `:282-288`）；`run()` 后 `await loadRuns()`（`:417`），初载 `void loadRuns()`（`:280`）；S4 关面板后连线（`workflows.steps.ts:100-102` 关 `关闭配置面板` + 断言 `aside[aria-label="节点配置"]` 计数 0，R1 处置）+ 新增历史断言（`:135-141`，heading `运行历史` 域内精确文本）+ smoke feature `:25` 新增断言行；V9 8 场景 58 步全绿，V10 2 场景全绿）。
- S5 收尾 → AC4（`make openapi-check` 绿且 `api/` diff 为空；i18n 同步；PLAN-001~007 回归面）：**通过**（V13 `api/` 零 diff + V8 21 路由新鲜；V12 key 集对称；回归面：V1/V2/V3 后端门禁全绿 + V4/V5/V6/V7 前端门禁全绿 + V9/V10 `@smoke/@a11y` 全绿，视为回归通过）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据；V9/V10 全绿）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；V11 旧锚点逐项保留且 V9 浏览器实证全绿；V13/V8 后端零变更）。
- P2：无。
- P3：无（本次为 AC 口径核验，非全面审计，不展开轻微清理项；边际项见 Gaps，如实记录为非缺陷）。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. 删除 confirm 的“取消不删”路径仅静态代码审查（`CanvasView.vue:350` 取消即返），无浏览器端到端用例；V9 画布场景不覆盖删除动作（与 TEST-006 Gaps 第 1 条同类缺口）。
2. 运行历史 error 分支（`:175`）与 outputs 展开（`:176-183`）无 e2e 断言；V9 新增断言仅覆盖 succeeded 记录可见性，未覆盖失败记录红 Badge / error 摘要 / details 展开内容。
3. a11y 扫描未覆盖面板展开与历史有数据态：`canvas.a11y.feature:18` 的“打开当前流程的画布页”为空画布态（无选中、无运行记录），`CanvasView.vue` 残留 3 处 `text-slate-500` 小字（`:51` noConfig、`：65` loadingProviders、`：173` 运行 id，均为白底按 4.5:1 理论通过）未经 axe 实测；本轮两处 contrast 修正在白底外语境，已绿不追溯。
4. PLAN-001~007 回归为抽查口径：全量门禁 + `@smoke` + `@a11y` 全绿即视为通过，未重跑 TEST-001 全部实况探针。
5. 后端集成测试按仓约束默认只在 CI 跑：本地仅执行 `api/tests` 单测域（24 项）。
