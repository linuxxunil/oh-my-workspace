# UI Package Guide (Vue3) / 共享基元库指南

本包是基元契约的唯一归属：`authoring.md / styling.md / forms.md / overlays.md / selection.md / testing.md` 定义行为，`web/` 只消费，不各自重写。

## Package Rules / 包规则

- 对外子路径以 `packages/ui/README.md` 的索引为准；新增基元一次配齐类型、测试、story、文档四件套。
- 样式采用 Tailwind v4 canonical 写法（`w-105` 不写 `w-[420px]`，`bg-linear-to-b` 不写 `bg-gradient-to-b`）；状态样式经由 data 属性表达，不对裸 class 做断言。
- 表单字段的受控行为、overlay 的 Root/content 挂载与生命周期、按钮与图标按钮的语义，均按文档执行，不自行放宽。
