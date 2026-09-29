# PLAN-008 画布页 UX 整体优化

- 关联 REQ / Linked REQ：`docs/requirements/REQ-008.md`（AC1–AC4）。
- 范围 / Scope：`web/`（CanvasView 双栏+右侧面板+i18n+运行历史）+ `e2e/`（画布 steps 锚点同步 + 历史断言）。不碰后端、dialog 基元、列表页。
- 架构 / Architecture：
  - 布局：`flex` 双栏——左画布 `flex-1`（高度 `calc(100vh-…)` 自适应，替代 480px 写死），右面板 `w-80`，`selectedNode` 为空收起；面板头节点类型 Badge + 关闭键。
  - i18n：新增 `canvas.deleteSelected/nodeConfig/saveConfig/saveVersion/runHistory/noRuns/invalidInputs/confirmRemoveNode/closePanel` 等 key 中英同步；模板零硬编码。
  - 删除：原生 `confirm`（PLAN-006 同款模式）。
  - 运行历史：底部列表（status Badge + error 摘要 + 可展开 outputs），`run()` 后刷新；保留 `role=status` 与 `aria-label=outputs` 锚点。
  - 运行区：`Field + Textarea` 基元化。
  - e2e：steps 锚点随新文案同步（预期内作废）；新增“运行历史出现 succeeded 记录”断言。
- 开发步骤 / Steps：
  - S1 布局重构（双栏+右侧面板+高度自适应）。验收 AC1（vue-tsc+目检）。
  - S2 i18n 补漏 + 删除确认 + 运行区基元化。验收 AC2。
  - S3 运行历史列表 + 刷新联动。验收 AC3（前半）。
  - S4 e2e 锚点同步 + 历史断言 + `@smoke`/`@a11y`。验收 AC3（后半）。
  - S5 收尾：全量门检 + TEST-008 + 本地 commit。
- 风险 / Risks：R1 面板收起影响 e2e 节点点击流→S4 同步验证；R2 自适应高度多视口表现→`fit-view-on-init` 保留 + a11y 验证；R3 i18n 改动波及中文锚点→S4 锚点清单核对。
- 验证命令 / Verification：`vue-tsc` / `make web-test web-build openapi-check` / `pnpm -C e2e e2e -- --tags @smoke,@a11y`。
