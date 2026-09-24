# Accessible Names / 可访问命名契约

跨组件契约，归基元库拥有，业务组合时遵守，不重定义。

## 起手式

可访问名是读屏识别元素的扁平串，不是每个角色都允许命名；描述是可选补充；选中、展开、禁用等状态与名称分离，进度播报归业务状态 owner。

每个改动元素：看最终渲染元素与角色；优先可见文本或原生标签关联；有别处可见文本用 `aria-labelledby`；无可见文本且角色允许才用 `aria-label`；有益补充才加 `aria-describedby`，不复述名称；每种响应与交互态都验算一次。

## 常用决策

| 界面 | 契约 |
|---|---|
| 文本按钮或链接 | 子文本命名动作，不复述进 `aria-label`；聚焦中标签变化看按钮契约 |
| 表单控件 | 走表单契约标签基元或原生 label，保持激活关系 |
| 图标独占命令 | 走图标按钮契约，一命名源一装饰图形 |
| 对话框或命名区 | 复用可见标题经标题 API 或 `aria-labelledby`，无标题才 `aria-label` |
| 分组控件 | `Fieldset` 加 legend，每控件独立标签 |
| 表格或图形 | 优先 `caption/figcaption` |
| 图片 | 有意义 `alt`，装饰 `alt=""` |
| 普通 `div/span` | 保持可读，不加命名属性 |

命名权来自语义，不来自属性存在；不为命名虚构角色。

## 书写

可见标签词放可访问名前部；相同动作加目标上下文消歧义；措辞简洁动作化，不追加角色词与已暴露状态；本地化文本经公开属性传入，基元不直连业务 i18n：

```vue
<template>
  <span :id="fileNameId">{{ fileName }}</span>
  <UiButton :aria-labelledby="`${deleteLabelId} ${fileNameId}`">
    <span :id="deleteLabelId">{{ deleteLabel }}</span>
  </UiButton>
</template>
```

## 描述关联

`aria-describedby` 关联简短帮助或后果；引用内容变纯串，富 instructions 仍须正文可达。字段描述与错误走 `FieldDescription/FieldError`，不覆写第二套关联。对话框摘要短写，不把整个表单体变描述。Tooltip 内容不是触发器命名源。

## 隐藏文本

- `sr-only` 视觉隐藏但读屏保留，可参与命名；不是 `aria-label` 自动替代。
- `hidden/display:none/aria-hidden` 一般排除计算；显式引用隐藏节点仍可能贡献，先查引用再下结论。
- 删标签前验折叠导航、响应式图标态、加载禁用态的最终名称；截断不断底层文本。
