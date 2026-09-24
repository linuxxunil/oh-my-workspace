# Web Agent Guide (Vue3) / 前端指南

## Workflow / 工作流

- 跑测试只认 `web/docs/test.md`，做静态检查只认 `web/docs/lint.md`。
- 涉及组件归属、状态划分、数据流、effect、交互边界取舍时，调用 `how-to-write-component-vue`；纯文案、纯样式、纯测试改动不加载该技能。
- 收到显式 review 请求时用 `frontend-code-review-vue`；新增或修改 Vitest 时用 `frontend-testing-vue`。

## Package Contracts / 包契约

- 新增后端调用统一走生成式客户端（`src/service/generated/*`，由 orval/openapi-typescript 产出）。不手写 REST helper，不镜像 DTO，不伪造应用态 mock，不直接改生成物。生成物有问题先修后端 schema 再重新生成。
- 优先复用 `@/packages/ui/*` 基元、data 属性与 design tokens；保留可见的 focus 指示。
- 文案收敛到 `web/i18n/locales/zh-CN/*.json + en-US/*.json`，新增或改名 key 时同步所有 locale。
- 保存与提交流程保留真实 `<form>` 边界、可见 label 与可访问错误信息；复杂校验用 `vee-validate + zod`。
- 按钮语义、loading 态、可访问名以 `packages/ui/docs/button.md` 为准；不在 web 侧再包一层 wrapper 遮住基元契约。
- Overlay（dialog/menu/popover）以 `packages/ui/docs/overlays.md` 为准；信息类提示用 `Infotip` 基元。
- 自定义 SVG 图标以 `packages/iconify/README.md` 为准，不新增生成式图标组件。
- 截断文本、landmarks、可访问命名分别以 `web/docs/truncated-text.md, landmarks.md, accessible-names.md` 为准。
- `web/docs/test.md` 是测试唯一的真相源，skill 只负责路由执行，不另行定义规则。

## Vue Prohibitions / 禁止项

- 不写 React 风格代码（hooks/Jotai/nuqs/Next 导航）。路由状态的唯一 owner 是 `vue-router`，全局状态的唯一 owner 是 `pinia`，服务端缓存走 Vue Query。
- 不把 live 应用态写入 `localStorage`；该存储只放低频偏好。
- 不用 `value || undefined` 丢掉有意的空串；`null/undefined/''` 一直保留到最终消费边界再处理。
