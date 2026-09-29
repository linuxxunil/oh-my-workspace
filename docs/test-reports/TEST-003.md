# TEST-003 PLAN-003 Dify 式浅色换肤验收核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-003.md`（S1–S4，对应 `docs/requirements/REQ-003.md` AC1–AC4）
- 核验时间 / Date：2026-09-29（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`（沿用 TEST-001 实测有效的三角色）
- 本轮改动域（`git status` 实测）：`Makefile`（ui-test/ui-check）、`web/package.json` + `pnpm-lock.yaml`（tailwindcss@4.3.3、`@tailwindcss/vite`、`@vue/test-utils`、`happy-dom`）、`web/vite.config.ts`（tailwind 插件 + `@/packages/ui` 别名 + `fs.allow` 放行仓根）、`web/tsconfig.json`（基元子路径映射 + include 基元源码）、`web/src/main.ts`（引入 styles.css +1 行）、`web/src/styles.css`（新增：先 `@import 'tailwindcss'` 再相对路径引 ui 样式 + `@source` 扫描基元）、`packages/ui/styles.css`（新增：`--color-surface: #f4f6fb`）、`packages/ui/src/`（新增 button/form/input/selection/badge/empty-state 六目录，各含实现 + `index.ts` + `.spec.ts` + `.example.vue`）、`packages/ui/{package.json,vitest.config.ts,tsconfig.json,pnpm-lock.yaml,pnpm-workspace.yaml}`（新增独立测试包）、`packages/ui/README.md`（新增 input/badge/empty-state 三行索引）、`packages/ui/docs/testing.md`（命令订正为 `pnpm test/check`）、`web/src/App.vue`（侧栏壳）+ 四视图换肤、`docs/dev-spec/01-workflow.md`（+6 行 Pre-approval 条款）。`e2e/`、`web/src/i18n/`、`web/src/views/CanvasView.vue` 本轮零 diff。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!`（exit 0） |
| V2 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 33 source files`（exit 0） |
| V3 | `make test`（全量） | 通过：`19 passed`（与 TEST-002 一致，无失败） |
| V4 | `make web-check` | 通过：`pnpm --dir web exec vue-tsc --noEmit` 无输出（exit 0） |
| V5 | `make web-test` | 通过：`2 files / 6 tests passed`（`dag.spec.ts` 3 + `mutator.spec.ts` 3，旧单测仍绿） |
| V6 | `make ui-test` | 通过：`6 files / 17 tests passed`（button 5 + field 3 + input 3 + select 2 + badge 2 + empty-state 2，happy-dom） |
| V7 | `make ui-check` | 通过：`pnpm --dir packages/ui check`（`vue-tsc -p tsconfig.json`，含 `.example.vue` 在内 exit 0） |
| V8 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（20 路由）`（exit 0，后端契约未被换肤波及） |
| V9 | `make web-build` | 通过：`✓ built in 1.08s`（产物含 LoginView/UsersView/ModelsView/WorkflowsView/CanvasView 各 chunk，无报错） |
| V10 | `pnpm -C e2e e2e -- --tags @smoke` | 通过：`2 scenarios (2 passed)`，`14 steps (14 passed)`（与 TEST-001/002 一致，全绿） |
| V11 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`2 scenarios (2 passed)`，`10 steps (10 passed)`（登录页 + 画布页 axe 零 critical/serious） |
| V12 | 锚点 grep（只读）：`rg getByRole/getByLabel/导航名/按钮文案/label` 于 `e2e/src` + `e2e/features`，对照 `git diff HEAD -- e2e/ web/src/i18n/` | `e2e/` 与 `web/src/i18n/` 均零 diff；步骤锚点（`主导航` + `流程/模型/用户`、`登录`、`邮箱/密码`、`名称/类型/地址`、`模型供应商/连通性检查`、`流程/新建流程/打开画布`、`config JSON/保存配置/保存版本/发布/输入 JSON/运行`）与 `zh-CN.json` 键值一一对应；`App.vue` 保留 `aria-label="主导航"`；表单 id（`email/password/np-name/np-type/np-url/nu-email/nu-role/nw-name`）换肤前后一字未动 |
| V13 | 源码阅读（只读） | `packages/ui/src/form/Field.vue:3`（`label :for=inputId`）+ 各视图 `Field input-id` 与 `TextInput/Select :id=inputId` 配对，label 关联链完整；`Button.vue:56-58` loading 仅阻断 emit（见 P3-1）；`web/vite.config.ts` 别名 `@/packages/ui → ../packages/ui/src` 且 `@` 仍指 `./src`，`fs.allow` 放行仓根；`web/src/styles.css:1-2` import 顺序（tailwind 在先）与相对路径注释一致；`packages/ui/styles.css:6` token `#f4f6fb`；`01-workflow.md:21-25` Pre-approval 三段（列清权限→一次批复→门禁追问例外） |

## 逐条验收结论 / AC Verdicts（PLAN-003 S1–S4 → REQ-003 AC1–AC4）

- S1 地基 → AC1（`web-build` 通过；旧单测仍绿）：**通过**（V9 构建成功 + V5 旧 6 项全绿；`tailwindcss@^4.3.3` + `@tailwindcss/vite` 见 `web/package.json:24,30`，别名/tsconfig/fs.allow 见 V13）。
- S2 基元 → AC2（六基元四件套齐，包内单测全绿，story 可渲染）：**通过**（六目录各含实现 + `index.ts` + `.spec.ts` + `.example.vue`，V6 17 项全绿；`.example.vue` 六份均经 V7 `vue-tsc` 类型覆盖；README 登记 input/badge/empty-state 三子路径，form/selection/button 为既有行；`input/` 内 TextInput + Textarea 共用一 spec，符合“TextInput/Textarea 同基元目录”口径）。
- S3 换肤 → AC3（四页 + App 壳落地；`vue-tsc` 绿；`@smoke` + `@a11y` 全绿；锚点零改动）：**通过**（V4/V10/V11 全绿 + V12 锚点 grep 零改动；App 侧栏品牌 + 导航 + 角色 Badge + 退出，登录居中卡片，用户行 Badge + 新增卡，模型供应商卡 + 连通结果红/绿，流程卡片网格 + 新建；tokens `bg-surface/rounded-xl/bg-indigo-600/focus-visible:ring` 见 V13 grep；画布页功能不动，`CanvasView.vue` 零 diff）。
- S4 收尾 → AC4（事前一次授权条款写入 `docs/dev-spec/01-workflow.md`）：**通过**（`01-workflow.md:21-25` 三段齐：开工前列清权限、批复后不为权限打断、门禁追问例外，落款 REQ-003 AC4）。
- PLAN-001/002 回归面 → **通过**（V1/V2/V3 后端门禁全绿 19 项 + V10/V11 `@smoke/@a11y` 全绿 + V8 openapi 20 路由新鲜，视为回归通过；未重做 TEST-001 全部实况探针，见 Gaps）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；V10/V11 全绿，锚点零改动）。
- P2：无。
- P3-1（正确性收口/可维护性）：登录提交按钮由原生 `disabled` 改为基元 `loading`，连点/回车存在二次提交窗口。
  - 文件行号：`web/src/views/LoginView.vue:25`（`:loading="submitting"`，旧 `:disabled` 已移除）+ `packages/ui/src/button/Button.vue:56-58`（loading 仅 `return` 阻断 emit，不 `preventDefault`）+ `web/src/views/LoginView.vue:53-66`（`onSubmit` 无 `submitting` 守卫）。
  - 复现/证据：只读审查 + V10/V11 全绿（未覆盖连点路径）。`type="submit"` 按钮的原生表单提交不受 Vue `@click` 守卫拦截，loading 期间再次点击/回车仍会触发 `form @submit` → `mutateAsync` 并发。
  - 影响面：当前功能正常（登录 POST 幂等，多发一次仅多一次请求，无数据破坏；`aria-disabled` 语义保留，a11y 门仍绿）。
  - 修复方向：二选一——`Button` 在 `loading` 且 `type="submit"` 时亦透传原生 `disabled`（需同步无障碍文案），或 `onSubmit` 首行加 `if (login.isPending.value) return` 守卫，并以 V10 回归验证（仅建议，不承揽）。
- P3-2（可维护性/依赖卫生）：`web/package.json` 新增的 `@vue/test-utils` + `happy-dom` 在 web 侧无消费者。
  - 文件行号：`web/package.json:26,28`（新增两 dev 依赖）vs `web/vitest.config.ts:8`（unit 工程仍 `environment: 'node'`，`web/src` 无 `mount(` 用例）。
  - 复现/证据：`rg "@vue/test-utils|happy-dom|mount(" web/src web/vitest.config.ts` 仅命中 `package.json` 两行；组件单测实际落在 `packages/ui` 独立包（V6/V7）。
  - 影响面：功能无影响（V5/V9 全绿）；仅依赖体积与“装而不用”的误导（后人误以为 web 侧可写组件单测）。
  - 修复方向：若 web 侧无组件测试计划则移除该两项（以 V5/V9 回归验证），否则在 `web/docs/test.md` 明确两处测试分工（仅建议，不承揽）。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. Dify 式视觉还原度（间距/字阶/品牌感）为主观判断，本次仅验证 token 与结构落点（底 `#F4F6FB`、卡片白 `rounded-xl`、主色 `#4F46E5` 系 indigo-600、焦点环可见）+ e2e/axe 门禁，未做逐像素设计稿比对。
2. story“可渲染”以 V7 `vue-tsc` 类型覆盖 + 六份 `.example.vue` 静态审查为据，未在浏览器/Storybook 内逐个渲染截图。
3. a11y 口径沿用既有门禁：仅登录页 + 画布页、仅拦截 `critical`/`serious`（见 TEST-002 V11）；换肤新增的四页卡片/表单未纳入 axe 扫描，`moderate`/`minor`（如靛蓝对比度边缘 case）无断言。
4. PLAN-001 回归为抽查口径：门禁全绿 + `@smoke/@a11y` 全绿 + openapi 新鲜即视为通过，未重跑 TEST-001 V11–V19 全部实况探针（infra ps/镜像/vector 版本/沙箱出网探测等）。
5. 后端集成测试按仓约束默认只在 CI 跑：本地仍仅执行 `api/tests` 单测域（19 项）；DB 迁移幂等/并发发布竞态等长尾路径无覆盖（沿用 TEST-001 G6 约束）。
6. `Textarea` 基元已实现并有单测覆盖，但本轮四页换肤无实际消费（各页仅用 TextInput + Select）；属 REQ-003 允许的“基元先行”，不记为问题。
