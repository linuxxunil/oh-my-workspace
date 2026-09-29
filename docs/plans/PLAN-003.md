# PLAN-003 Dify 式浅色换肤

- 关联 REQ / Linked REQ：`docs/requirements/REQ-003.md`（AC1–AC4）。
- 范围 / Scope：`web/`（tailwind 接入、styles 入口、四页换肤、App 壳）、`packages/ui/src/`（六基元四件套）、`docs/dev-spec/01-workflow.md`（AC4 条款）。不碰后端、画布功能、i18n key、e2e steps。
- 架构 / Architecture：
  - 消费链：`web/src/styles.css`（`@import 'tailwindcss'` 在先）→ `@/packages/ui/styles.css`（tokens + 基元样式入口）；tailwind 经 `@tailwindcss/vite` 插件 + `@source ../packages/ui/src` 扫描基元类。
  - 别名：`@/packages/*` → `<root>/packages/*`（vite + tsconfig 同步），`@/*` 仍指 `web/src`。
  - 基元目录（一基元一目录）：`button/`、`form/`（Field）、`input/`（TextInput/Textarea）、`selection/`（Select）、`badge/`、`empty-state/`，各含实现 + `index.ts` 子路径入口 + `.spec.ts` + `.example.vue`；README 索引登记新增子路径。
  - e2e 锚点冻结：导航 `流程/模型/用户`、按钮 `登录/新建流程/打开画布/模型供应商/连通性检查/运行/发布/保存版本`、label `邮箱/密码/流程/名称/类型/地址/config JSON/输入 JSON` 一字不动。
- 开发步骤 / Steps：
  - S1 地基：装 `tailwindcss@^4` + `@tailwindcss/vite`；`styles.css` 两处；tokens；别名；`web-build` 通过。验收 AC1。
  - S2 基元：六基元四件套 + README 登记；装 `@vue/test-utils` + `happy-dom` 跑组件单测。验收 AC2。
  - S3 换肤：App 壳 + 四页；锚点文本 diff 为零。验收 AC3。
  - S4 收尾：全量门禁 + `@smoke/@a11y` + `@tester` 出 TEST-003 + 本地 commit。验收 AC3/AC4。
- 风险 / Risks：R1 Tailwind v4 与 vite 6 插件兼容→以 `web-build` 为准；R2 组件测试环境缺失→S2 先立 happy-dom；R3 换肤误改锚点→S3 用 grep diff 门（锚点文本逐个核对）。
- 验证命令 / Verification：`pnpm --dir web build` / `pnpm --dir web exec vitest run --project unit` / `pnpm --dir web exec vue-tsc --noEmit` / `pnpm -C e2e e2e -- --tags @smoke|@a11y`。
