# Styling / 样式契约

## 组件状态

状态样式优先基元 data 属性（如 `data-checked:`、`data-disabled:`），动态值用其 CSS 变量（如浮层锚宽与可用高）。不为样式在业务侧镜像基元状态。

能在调用方读到部件态先看 data 属性与变量是否已表达；确需直读加短注释说明原因。`render` 用于元素组合，不只为换样式；回调放在外层基元，类字符串放目标。组合不改变部件归属的状态。

## Tailwind v4

消费者根样式先引入 Tailwind，再引入本包样式入口：

```css
@import 'tailwindcss';
@import '@/packages/ui/styles.css';
```

工作区直接扫描本包源码时，按消费者样式表位置加 `@source` 到 `src/`，排除测试与示例文件。

## 圆角

先查设计稿实际像素再选 `rounded-*`，记号名相同不代表值相同（如 6px 对 `rounded-md` 而非 `rounded-sm`）。优先语义记号与现有变体，无匹配才用任意值（如 10px 用 `rounded-[10px]`）。

`important` 只做紧凑兼容覆写，且拥有变体、data 属性、选择器结构都表达不了时才用。

焦点样式挂在视觉呈现焦点的元素上；可见包层含原生焦点目标时从包层选中后代焦点态。
