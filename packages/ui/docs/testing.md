# Testing / 基元测试契约

本包测试拥有基元边界、Storybook 与验证命令，是 `frontend-testing-vue` 在基元侧的真相源。

## 边界

- 测集成与覆写：语义角色、状态属性、传送、焦点行为、`render` 组合契约。
- 不重复测上游与浏览器：原生语义、键盘模型已由上游保证，只测本包集成与已知回归。
- 一基元一 story，覆盖默认、禁用、加载、错误四态。

## 命令

```bash
vp test run --project unit packages/ui/src/<name>
vp test run --project browser packages/ui/src/<name>/*.browser.spec.ts
```

禁真实网络；Storybook 只做视觉回归，不代功能断言。
