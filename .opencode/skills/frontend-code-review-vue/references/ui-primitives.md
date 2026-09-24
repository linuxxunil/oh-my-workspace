# UI Primitives (Vue) / 基元库评审路由

评审是否正确使用共享界面基元，不在业务侧重复造轮子。

| 评审面 | 唯一归属方 |
|---|---|
| 包边界与文档路由 | `packages/ui/AGENTS.md` |
| 引入、导出、公开类型 | `packages/ui/docs/authoring.md` |
| 按钮与图标按钮 | `packages/ui/docs/button.md` |
| 复合输入 | `packages/ui/docs/input-group.md` |
| 表单语义 | `packages/ui/docs/forms.md` |
| 选择与类型值 | `packages/ui/docs/selection.md` |
| 挂载点、层级、浮层 | `packages/ui/docs/overlays.md` |
| 状态样式与 Tailwind | `packages/ui/docs/styling.md` |
| 测试与 Storybook | `packages/ui/docs/testing.md` |

实现、公开类型、测试、示例不一致时，先确定实际归属方再报告；只报告可复现的契约违反，不报告风格偏好。
