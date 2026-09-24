# Button / 按钮契约

`Button` 给带可见文本标签的动作；图标独占命令用 `IconButton`，持久按下态用 `Toggle`，跳转用原生链接。

本包 `Button` 在原生按钮上加变体、尺寸、内容间距与 `loading` 态，保留原生按钮、焦点与组合行为。

## 语义

默认渲染原生 `<button type="button">`，提交表单显式 `type="submit"`：

```vue
<template>
  <form @submit.prevent="handleSubmit">
    <UiButton type="submit">保存</UiButton>
  </form>
</template>
```

不用 `Button` 渲染链接；导航走原生锚点或路由链接，只复用视觉变体。非按钮元素需按钮语义才用组合 API，且不是链接模式。

## Loading 与禁用

| 属性 | 含义 | 默认焦点行为 |
|---|---|---|
| `disabled` | 动作不可用 | 原生禁用，移出 Tab 序 |
| `loading` | 已触发待定 | 阻断激活但保留焦点 |

`loading` 拥有禁用交互、保留焦点与装饰 spinner；按钮留 Tab 序并 `aria-disabled`，基元抑制激活。待定态只传 `loading`，独立可用条件放 `disabled`：

```vue
<template>
  <UiButton :loading="isSaving" :disabled="!canManage">保存</UiButton>
</template>
```

spinner 仅装饰；loading 全程保留非空可见标签，标签不变则其文本继续命名按钮。聚焦中标签变化时给变化文本稳定 ID 并显式引用，调用方拥有该关系，不拿 `aria-label` 替换变化文本。

不加 `aria-busy` 泛化待定；长任务播报归业务状态或进度 owner。

## 内容间距

`Button` 拥有直接子项间距，调用方不加图标边距与常规 `gap`：

```vue
<template>
  <UiButton><span aria-hidden="true" class="i-rocket size-4" />启动</UiButton>
</template>
```

中、大尺寸分别 4px、6px，小尺寸 3-4px；文档化布局例外才经 `className` 覆写。

## 相关

- 图标独占看 `IconButton`；命名来源看可访问命名契约；状态样式看样式契约。
