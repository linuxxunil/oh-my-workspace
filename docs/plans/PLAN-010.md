# PLAN-010 侧栏缩排键下移 + 节点连线左右手柄

- 关联 REQ / Linked REQ：`docs/requirements/REQ-010.md`（AC1–AC3）。
- 范围 / Scope：`web/src/App.vue`（缩排键下移）+ `web/src/components/CanvasNode.vue`（手柄左右）。不碰后端、DB、i18n、边样式。
- 架构 / Architecture：
  - S1：顶栏移除缩排键；侧栏 `nav` 后加 `mt-auto` 底部切换键（收窄态居中图标，`aria-label`/`aria-expanded` 原样，复用 `nav.collapseSidebar/expandSidebar`）。
  - S2：`CanvasNode` 的 `Handle` 改 `target=Left/source=Right`；横向排布已就绪，无需动坐标。
- 开发步骤 / Steps：
  - S1 缩排键下移。验收 AC1（vue-tsc+目检+e2e 收窄场景）。
  - S2 手柄改左右。验收 AC2（@smoke 画布场景）。
  - S3 收尾：`web-build` + `@smoke` + `@a11y` + TEST-010 + 本地 commit。
- 风险 / Risks：R1 收窄态底部键宽度→复用 `justify-center` 模式；R2 手柄与节点间距→横向已有 400px 间隔。
- 验证命令 / Verification：`make web-check web-build` / `pnpm -C e2e e2e -- --tags @smoke,@a11y`。
