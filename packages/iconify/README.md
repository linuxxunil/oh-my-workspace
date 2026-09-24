# Iconify Collections / 自定义图标契约

自定义 SVG 图标注册、命名、尺寸以本文件为准，不加生成式图标组件。

## 流程

1. SVG 放 `packages/iconify/collections/<name>.svg`，文件名即图标名，小写连字符。
2. 尺寸只用 `size-4/5/6` 三档；装饰图标 `aria-hidden="true"`，语义图标走按钮命名契约。
3. 引用经统一入口，不直引文件路径；新增图标同步更新本目录索引。

禁在 `web` 下加生成式图标组件目录。
