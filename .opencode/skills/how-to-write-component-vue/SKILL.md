---
name: how-to-write-component-vue
description: 实现/重构Vue/TS组件，且涉及归属、feature边界、状态、数据流、watch、交互归属决策时用。不用于纯review、纯测试、纯文案、纯样式。
---

# How To Write Component (Vue) / 组件写作

按命中主题只读对应文档，不全量加载。

## Topic Routing / 主题路由

- 组件移动、模块边界、属性、类型、归属方：`references/ownership.md`
- 界面基元、状态样式：`packages/ui/docs/authoring.md` 加 `packages/ui/docs/styling.md`
- 本地状态、表单草稿、路由身份、地址、持久化：`references/state.md`
- 生成契约、可空值、查询、变更、鉴权、工作区：`references/data.md`
- 快捷键、焦点、对话框、菜单、弹出层：`references/interactions.md` 加浮层指南；存在本地会话草稿时再读 `state.md`
- 副作用、导航、记忆化、预取、渲染开销：`references/runtime.md`

## Scope And Verification / 范围与验证

从附近实现确定行为归属方、状态寿命、公开契约；守住垂直切片，只有契约要求才跨界。运行 `web/docs/test.md` 的测试与 `web/docs/lint.md` 的静态检查。

## Tailwind CSS / 样式写法

书写规范 Tailwind v4 形式：`w-105` 不写 `w-[420px]`，`px-2.25` 不写 `px-[9px]`，`bg-linear-to-b` 不写 `bg-gradient-to-b`，`wrap-break-word` 不写 `break-words`。
