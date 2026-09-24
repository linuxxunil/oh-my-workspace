# Forms / 表单契约

表单基元组合原生表单语义、字段可访问性与本包样式，不做表单状态管理与 schema 框架。

## 提交边界

一组共同保存或提交的控件必须有真实 `<form>` 边界。不把输入框与纯点击按钮拼成非正式表单。

基元拥有结构化提交值、合并错误、校验模式，渲染原生 `<form>`。其他表单库拥有提交与校验时仍用原生表单，不嵌套两个表单 owner。

提交按钮显式 `type="submit"`，表单内其余按钮 `type="button"`。

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <UiButton type="submit">保存</UiButton>
  </form>
</template>
```

## 值与归属

基元拥有提交与校验边界，不拥有每个字段草稿。

受控性按是否需拥有当前值决定：应用渲染无需拥有则用 `defaultValue`；编辑中需拥有则用 `v-model` 与变更处理。监听变更、跟踪脏态、校验本身不强制要求受控。

草稿归寿命匹配的最窄组件；局部受控不必上提；非受控字段可在显式持久边界被工作流取值。挂载寿命由所在界面定义，归属位置决定草稿在寿命内外。

## 字段与标签

需共享名称、标签、校验、描述、错误态用 `Field`；独立输入可用原生 `<label for>`，常规表单行优先可见标签。`FieldDescription` 与 `FieldError` 拥有对应可访问消息关系。

按控件选标签基元：文本输入、`Textarea`、单选框、每项 `Radio`、`Switch`、`NumberField` 用 `FieldLabel`；触发式 `Select` 用 `SelectLabel`；`Slider` 按其结构用 `SliderLabel`，多拇指才给每拇指 `aria-label` 区分；选项组标签不是字段标签。

前缀、后缀、动作同占输入视觉面用 `InputGroup`。

## 分组控件

一组相关控件（复选组、单选组、多拇指滑杆、一节相关输入）用 `Fieldset` 加 legend 语义，每项包 `FieldItem` 并给独立标签。`Fieldset` 只拥有分组语义，不拥有交互态；`disabled/value/defaultValue/变更` 传给分组基元。

每项 `Radio` 必属 `RadioGroup`，组名用 legend，每项名用标签，不渲染孤立 `Radio`。

表单态、schema、服务端校验、重置行为放寿命匹配的最近业务方，不进基元内部；可观察态经公开属性透传，不替换语义结构。
