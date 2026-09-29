# TEST-010 PLAN-010 侧栏缩排键下移 + 节点连线左右手柄核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-010.md`（S1/S2/S4，对应 `docs/requirements/REQ-010.md` AC1–AC3）
- 核验时间 / Date：2026-09-29（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`
- 本轮改动域（实测）：tracked 3 文件（`web/src/App.vue` 缩排键顶栏→侧栏底部；`web/src/components/CanvasNode.vue` 手柄 Top/Bottom→Left/Right；`e2e/src/steps/workflows.steps.ts` 测试 infra：`deleteEdge` 加 `force: true` + 注释）。`api/` 零 diff（V7）。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make web-check`（`vue-tsc --noEmit`） | 通过：无输出（exit 0） |
| V2 | `make web-test` | 通过：`2 files / 6 tests passed`（`dag.spec` 3 + `mutator.spec` 3，回归绿） |
| V3 | `make web-build` | 通过：`✓ built in 1.38s`（`AccountView` chunk 2.26 kB 等全量构建绿，AC3 口径） |
| V4 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0，AC3 口径） |
| V5 | `pnpm -C e2e e2e -- --tags @smoke` | 通过（一次全绿，无需重跑）：`12 scenarios (12 passed)`，`82 steps (82 passed)`（含画布连线场景与收窄侧栏场景；本轮未触发任务书预告的 30s 登录超时抖动） |
| V6 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`4 scenarios (4 passed)`，`21 steps (21 passed)` |
| V7 | 零后端审查（只读）：`git diff HEAD -- api/` + `git status --short -- api/` | 输出为空（0 行 diff，无 tracked/untracked 变动）；V4 的 21 路由新鲜佐证无 schema 漂移 |
| V8 | e2e 锚点兼容性（只读 + V5/V6 实证） | 兼容：收窄/展开锚点（`layout.steps.ts:30-42` 的 `收窄侧栏/展开侧栏/aria-expanded/localStorage`）、连线锚点（`workflows.steps.ts:109-118` 的 `.vue-flow__handle.source/.target` 类定位，与方位无关，符合 REQ-010 约束）、保存版本/发布/运行锚点（`:124-135` 的 `保存版本/发布/运行` + `status` 文案）全部零改动可用，V5/V6 全绿实证 |
| V9 | 非目标守卫（只读）：`git diff HEAD --stat` + diff 全文 | `web/src/App.vue` 仅缩排键搬家（顶栏删除 9 行 + 侧栏底新增 13 行，`toggleCollapsed`/`COLLAPSED_KEY`/navItems 逻辑零改动）；`CanvasNode.vue` 仅两行 `Position` 改值；无 i18n key 增减、无边样式、无 `blankDag` 坐标、无后端/DB 改动 |

## 逐条验收结论 / AC Verdicts（PLAN-010 S1/S2/S4 → REQ-010 AC1–AC3）

- S1 → AC1（缩排键位于侧栏底部 `mt-auto` 区，收窄/展开/`aria-expanded`/偏好记忆不变；顶栏无残留）：**通过**（`App.vue:130` 底部容器 `mt-auto pt-3`；`:131-138` 按钮复用 `toggleCollapsed`（`:172-175`）、`aria-label` 在 `nav.expandSidebar/nav.collapseSidebar` 间切换（`:135`）、`aria-expanded=!collapsed`（`:136`）、收窄态 `justify-center px-1` 居中图标（`:134`）+ `›/‹` 装饰 `aria-hidden`（`:139`）+ 展开态文案 `t('nav.collapseSidebar')`（`:140`）；偏好键 `workspace2.navigation.collapsed` 读写对称（`:158/:162/:174`）；顶栏 `:4-102` 无残留缩排键（diff 确认删除唯一顶栏实例）；V5 `layout.smoke.feature:25-29` 收窄场景绿实证）。
- S2 → AC2（节点左进右出，start→code→end 连线保存正常；`@smoke` 画布场景绿）：**通过**（`CanvasNode.vue:9` `target=Position.Left`、`:12` `source=Position.Right`，两行改值之外模板/脚本零改动；V5 `workflow.smoke.feature:18-26`“编排最小流程并运行成功”（连线→删模板边→保存版本→发布→运行→`m=42`）全绿实证；连线步骤按 `source/target` 类定位与方位无关，符合 REQ 约束）。
- S4（测试 infra）→ AC2/AC3 支撑（`deleteEdge` 加 `force`，选中+Backspace 逻辑不变）：**通过**（`workflows.steps.ts:13-16` 注释写明左右手柄下模板 e1 边为完全水平线（bbox 高度 0）致 Playwright 可见性检查恒失败故 `force` 点选；`:21` 仅加 `force: true`，`:22` `Backspace` + 3 次重试 + `toHaveCount(0)` 硬断言不变；`dragHandle`（`:6-11`）零改动；属非产品改动，不计入 AC 口径回退；V5 画布场景绿实证）。
- S3 收尾 → AC3（`web-build` + `@smoke` + `@a11y` 绿；`api/` 零 diff）：**通过**（V3 构建绿 + V5 12/82 + V6 4/21 全绿 + V7 `api/` 零 diff + V4 21 路由新鲜；回归面 V1/V2 全绿视为通过）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据；V5/V6 全绿）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；V8 锚点逐项可用且浏览器实证全绿；V7/V4 后端零变更）。
- P2：无。
- P3：无（本次为 AC 口径核验，非全面审计，不展开轻微清理项；边际项见 Gaps，如实记录为非缺陷）。
- 结论：`No issues found`。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. 环境抖动本轮未触发：`@smoke`/`@a11y` 各跑一次即全绿，无需重跑；任务书预告的内存压力 30s 登录超时本轮零出现，故无抖动归因项。若后续重跑出现失败集合不一致的超时，仍按任务书口径先重跑确认再定级。
2. AC1“偏好记忆”仅经 `localStorage` 值断言（`layout.steps.ts:40-41`）+ 初始化读取代码（`App.vue:162`）覆盖，未做 reload 后状态复测；旁路概率低（读写键一致，`toggleCollapsed` 对称）。
3. 侧栏底部键的浏览器级键盘操作（Tab 到达 + Enter/Space 触发）未被 e2e 覆盖，仅由可访问名（`aria-label` 切换）+ `@a11y` 全绿间接覆盖；行为层由 `toggleCollapsed` 复用保证。
4. `deleteEdge` 的 `force: true` 掩盖了水平边不可见点击的真实用户路径，但删边本就是测试脚手架动作（真实用户拖拽连线走 `dragHandle`，方位无关类定位已覆盖），故记为可接受的测试 infra 让步。
5. PLAN-001~009 回归为抽查口径：全量门禁 + `@smoke` + `@a11y` 全绿即视为通过，未重跑 TEST-001 全部实况探针。
6. 后端集成测试按仓约束默认只在 CI 跑：本地仅执行前端门禁 + e2e 门禁，未执行 `api/tests`。
