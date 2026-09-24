# Frontend Testing Guide (Vue) / 前端测试指南

## Mindset / 心智

只围绕稳定可观察的契约写测试：交互结果、路由与 URL、持久化、权限、数据流、可达的 loading/success/error/empty、a11y、工具函数行为、可复现的回归。不写文件覆盖率式断言，不写 render 不 crash，不碰实现细节、私有 DOM 与 class 名断言。覆盖率只用于诊断，不设目标。

## Boundary / 边界

- 纯函数走单测；可复用的 composable 才直接测，否则经由 owning 组件覆盖；组件测试用 Vue Test Utils + happy-dom；跨模块走集成；browser 项目满足三准入（价值、增量证据、忠实边界）才建。
- 需要重置隐藏面的回归，统一走公开 transition：open → 修改 → close 等待消失 → reopen 后再断言。

## Query / 查询

- 优先级：`getByRole>label>text/testid`（canvas、编辑器这类无语义边界才用 testid）；语义容器内用 `within` 收窄；缺语义先修产品 markup 再补测试。

## Mock / 隔离

- 只隔离目标契约之外的部分（网络、导航、外部 SDK、重型 provider）；不隔离被测 UI 基元；不打真实网络；Query 测试每例新建 client；`userEvent` 对应 VTU `trigger` 加 browser 定位器的组合；异步操作一律 await。

## Commands / 命令（web/ 下执行）

```bash
vp test run --project unit path/to/spec
vp test run --project browser path/to/*.browser.spec.ts
vp test run --project unit --coverage path/to/spec  # 仅诊断
```

裸 `vp test` 会跑双项目，不算标准命令。`*.browser.spec.ts` 必须自带回归说明与增量证据。
