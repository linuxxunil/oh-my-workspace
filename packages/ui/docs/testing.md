# Testing / 基元测试契约

本包测试拥有基元边界、Storybook 与验证命令，是 `frontend-testing-vue` 在基元侧的真相源。

## 边界

- 测集成与覆写：语义角色、状态属性、传送、焦点行为、`render` 组合契约。
- 不重复测上游与浏览器：原生语义、键盘模型已由上游保证，只测本包集成与已知回归。
- 一基元一 story，覆盖默认、禁用、加载、错误四态。

## 命令（packages/ui 下执行，也可仓根 `pnpm -C packages/ui`）

```bash
pnpm test                              # 全部基元单测（happy-dom）
pnpm test src/<name>                   # 单基元，如 pnpm test src/button
pnpm check                             # vue-tsc 类型检查
```

禁真实网络；Storybook 只做视觉回归，不代功能断言。
（注：历史命令里的 `vp` 在本仓不存在，以上为准。）
