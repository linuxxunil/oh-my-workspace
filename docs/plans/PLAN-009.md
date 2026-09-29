# PLAN-009 全站 Layout 与导航 UX 优化

- 关联 REQ / Linked REQ：`docs/requirements/REQ-009.md`（AC1–AC5）。
- 范围 / Scope：`packages/ui/src/overlay/**`（DropdownMenu/Drawer 基元）；`packages/ui` 导出索引、overlay 文档、基元测试和示例；`web/src/App.vue` + i18n + 导航标记；`e2e/` 导航交互。零后端。
- 架构 / Architecture：
  - DropdownMenu：共享基元拥有触发/展开态、Teleport 内容、方向键/Home/End 导航、Escape/外部关闭、激活项关闭及焦点恢复；调用方通过 trigger/content slot 组合用户内容。
  - Drawer：受控 open prop + update 事件；Teleport 到 body，modal 语义、遮罩、Escape、Tab 焦点循环、滚动锁定和关闭后焦点恢复；App 持有打开状态，路由切换时显式关闭。
  - Layout：认证路由使用 sticky 顶栏；用户 Trigger 显示邮箱/角色，菜单“修改密码”RouterLink 至 `/account`、“登出”执行现有 auth.logout + router.push；侧栏桌面展开 240px/收窄 64px，以短标识保留导航语义；`localStorage` 仅保存 boolean 收窄偏好；移动端 breakpoint 下改用 Drawer。
  - 侧栏收窄状态为低频展示偏好，不与 Pinia auth 混合；Account 从侧栏移除。
- 编号 Todo / Steps：
  1. S1 DropdownMenu：按 overlays 契约实现共享基元，补类型/测试/示例/文档并更新索引。AC4；验证 `make ui-test ui-check`。
  2. S2 Drawer：实现模态移动导航抽屉及焦点/滚动行为，补四件套并更新 overlay 文档。AC4；验证 `make ui-test ui-check`。
  3. S3 Layout：固定顶栏、用户动作菜单、桌面可收窄导航、手机 Drawer、偏好持久化、i18n 中英同步。AC1/AC2/AC3；验证 `make web-check web-test web-build`。
  4. S4 Browser 验收：增加桌面用户菜单/收窄偏好与手机导航 e2e；运行 `@smoke`、`@a11y`。AC1–AC3/AC5。
  5. S5 收尾：运行全门禁、检查 API 零 diff、TEST-009；无 P0/P1 后 Review 并本地 commit，不 push。
- 风险 / Risks：R1 焦点循环和恢复跨 Teleport 容易回归→基元单测 + 浏览器 e2e；R2 手机 Drawer 打开时页面背景滚动→基元契约锁滚动并测试恢复；R3 收窄侧栏只留短标识可能降低可发现性→保留 aria-label/title 并用键盘/a11y 验收。
- 验证命令 / Verification：`make ui-test ui-check web-check web-test web-build openapi-check lint type-check test`；`pnpm -C e2e e2e -- --tags @smoke`；`pnpm -C e2e e2e -- --tags @a11y`。
