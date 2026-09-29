# PLAN-005 画布美化二期

- 关联 REQ / Linked REQ：`docs/requirements/REQ-005.md`（AC1–AC4）。
- 范围 / Scope：`web/`（CanvasView、CanvasNode 新文件、i18n `canvas.*`）、`e2e/`（画布步骤改写）。不碰后端、`packages/ui`、其他页面。
- 架构 / Architecture：
  - 依赖：`@vue-flow/minimap` + `@vue-flow/controls`（`^1` 对齐 core 1.42）+ css 引入；`<Background pattern=dots>` 用 core 自带。
  - 节点：`web/src/components/CanvasNode.vue`（`NodeProps` 签名，六类型配色点，`selected` 环），
    `nodeTypes` 注册；`addNode` 的 `label` 沿用 kind（dag 往返只认 `data.nodeType`，label 仅显示），
    load 处统一 `type: 'flowNode'`（`fromVueFlow` 不读 type，不动）。
  - chrome：Minimap/Controls/Background 均用官方独立包
    （v1 与 core 同系拆分：`@vue-flow/minimap`、`@vue-flow/controls`、`@vue-flow/background`）。
  - 表单：选中节点按 kind 渲染字段组，草稿态 `draft`（Record），`applyConfig` 组装回 `node.data.config`（键名与后端 graph.py 一致：`code/output_key/prompt/provider_id/model/query/top_k/var/equals`）；llm 供应商下拉数据源自 `useListProvidersModelsProvidersGet`。
  - e2e：画布步骤改填“代码/输出键”两栏 + 保存配置；`config JSON` 定位器删除。
- 开发步骤 / Steps：
  - S1 chrome：装依赖 + Minimap/Controls/Background/边样式。验收 AC1。
  - S2 自定义节点：CanvasNode + 接线 + 配色。验收 AC2。
  - S3 类型表单 + i18n + e2e 改写。验收 AC3。
  - S4 收尾：全量门禁 + `@smoke/@a11y` + TEST-005 + 本地 commit。
- 风险 / Risks：R1 v1 自定义节点事件（click/选中类名）与默认节点差异→以 e2e selectNode 重试 + `selected` 类断言为准；R2 表单字段与后端键名错位→对照 `api/src/core/graph.py:43-86` 逐键核对；R3 minimap/controls 新增可聚焦控件→@a11y 回归兜底。
- 验证命令 / Verification：`pnpm --dir web build` / `vue-tsc` / `vitest` / `pnpm -C e2e e2e -- --tags @smoke|@a11y` / `make openapi-check` + `git diff --stat api/ web/openapi.json` 为空。
