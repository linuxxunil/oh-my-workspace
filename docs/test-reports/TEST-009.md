# TEST-009 PLAN-009 全站 Layout 与导航 UX 优化核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-009.md`（S1/S2/S3/S4/S5，对应 `docs/requirements/REQ-009.md` AC1–AC5）
- 核验时间 / Date：2026-09-29（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`
- 本轮改动域（实测）：tracked 7 文件 +179/−62（`web/src/App.vue` +200 行域：sticky 顶栏 + 用户 DropdownMenu + 桌面可收窄侧栏 + 手机 Drawer + Account 移出侧栏；`zh-CN.json`/`en-US.json` 各 +12；`web/tsconfig.json` +1 overlay 映射；`password.steps.ts` ±10 改走用户菜单；`packages/ui/README.md`/`docs/overlays.md` 索引 +6）；untracked 11 文件共 638 行（`packages/ui/src/overlay/` 7 件：`DropdownMenu.vue` 158 + `Drawer.vue` 132 + `index.ts` 4 + 两 spec 63/77 + 两 example；`docs/dropdown-menu.md`/`drawer.md` 各 19；`e2e/src/steps/layout.steps.ts` 60 + `layout.smoke.feature` 40 + `layout.a11y.feature` 19）。`api/` 零 diff（V13）。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!`（exit 0） |
| V2 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 33 source files`（exit 0） |
| V3 | `make test`（全量） | 通过：`24 passed`（与 TEST-008 基线一致；本轮零后端改动，回归绿） |
| V4 | `make ui-test` | 通过：`8 files / 23 tests passed`（基线 6 文件 17 项 → 本轮 +`drawer.spec` 3 +`dropdown-menu.spec` 3，既有 17 项回归绿） |
| V5 | `make ui-check` | 通过：`vue-tsc --noEmit -p tsconfig.json` 无输出（exit 0，含两基元 `TriggerProps` 类型与 slot 类型） |
| V6 | `make web-check` | 通过：`pnpm --dir web exec vue-tsc --noEmit` 无输出（exit 0，含 `App.vue` 新增 `DropdownMenu/Drawer` 引入 + overlay 路径映射） |
| V7 | `make web-test` | 通过：`2 files / 6 tests passed`（回归绿） |
| V8 | `make web-build` | 通过：`✓ built in 1.36s`（`AccountView` chunk 2.26 kB 等全量构建绿，AC1/AC2 构建口径） |
| V9 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0，AC5 口径） |
| V10 | `pnpm -C e2e e2e -- --tags @smoke` | 通过（经重跑确认）：`12 scenarios (12 passed)`，`82 steps (82 passed)`（基线 8 场景 58 步 → 本轮 12 场景 82 步，新增 4 layout 场景全绿，旧 8 场景无回退；前两次运行各见 2–3 个 30s 登录超时失败且失败集合不一致，第三次全绿，判定为内存压力环境抖动，见 Gaps 第 1 条，非产品缺陷） |
| V11 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`4 scenarios (4 passed)`，`21 steps (21 passed)`（基线 2 场景 10 步 → 本轮 +用户菜单展开态 +手机抽屉展开态，零 critical/serious；另以 `--name "用户菜单展开态扫描通过"` 单跑复核：1 场景 5 步通过，确认新增展开态场景真实执行非跳过） |
| V12 | i18n 对照（只读）：`zh-CN.json` vs `en-US.json` 的 `nav` key 集 + 消费点 | `nav` key 集完全对称（9 键：`workflows/models/users/primary/userActions/collapseSidebar/expandSidebar/openNavigation/closeNavigation`，双方 `missing` 均为空）；`App.vue` 消费的 `account.change`（修改密码/Change password）与 `auth.logout`（退出/Sign out）两侧均存在；模板新增可访问名全部走 `t()`，无中文硬编码（`›/‹/☰/×/W` 单字符装饰均标 `aria-hidden="true"`） |
| V13 | 零后端审查（只读）：`git diff HEAD -- api/` + `git status --short -- api/` | 输出为空（0 行 diff，无 tracked/untracked 变动）；V9 21 路由新鲜佐证无 schema 漂移 |
| V14 | 旧锚点与旧步骤兼容性（只读 + V10/V11 实证）：`e2e/src/support/nav.ts` 的 `gotoSection`/`LINKS` vs `App.vue` 导航 | 保留项全部可用：桌面侧栏仍含 `/workflows→流程`、`/models→模型`、`/users→用户` 三项（`App.vue:161-165` `navItems`），`aside nav` 仍命名 `主导航`（`:119`），`a11y.steps.ts:21`、各 `*.steps.ts` 的 `gotoSection(/workflows|/models|/users)` 路径有效，V10/V11 全绿实证；`/account` 与 `logoutViaUI` 已无调用方（`rg logoutViaUI` 仅剩 `nav.ts` 定义行，`gotoSection(this,'/account')` 已被 `password.steps.ts:39-44` 新路径替代），属死代码残留，见 Gaps 第 2 条，非缺陷 |

## 逐条验收结论 / AC Verdicts（PLAN-009 S1/S2/S3/S4 → REQ-009 AC1–AC5）

- S1 DropdownMenu 基元 → AC4（触发/方向键/Home/End/Escape/外部关闭/焦点恢复；类型+实现+测试+示例+文档四件套）：**通过**（`DropdownMenu.vue:41-51` triggerProps 含 `aria-haspopup/expanded/controls` + 打开首项聚焦；`:88-122` ArrowDown/Up（含 trigger 上开：Down 首项/Up 末项）、Home/End、Escape（`close(true)` 回焦）、Tab 关闭放行、点击 menuitem 关闭；`:128-131` pointerdown 外部关闭；`:133-144` 开关时监听器挂载/卸载 + `onBeforeUnmount` 清理；`index.ts:1-4` 导出实现 + `DropdownMenuTriggerProps` 类型；`dropdown-menu.spec.ts` 3 用例覆盖打开聚焦+Arrow、Escape 回焦、Home/End + 外部关闭；`dropdown-menu.md` 与 `overlays.md:46` 索引齐备；V4/V5 绿）。
- S2 Drawer 基元 → AC4（受控 open/modal 语义/Escape/遮罩/Tab 循环/滚动锁/焦点恢复；初始 closed 不动 body；四件套）：**通过**（`Drawer.vue:6-11` 遮罩 `aria-hidden` + `section role=dialog aria-modal=true tabindex=-1`；`:78-99` Escape 关闭 + Tab 首尾循环（含零可聚焦回退 panel 聚焦）；`:65-68` 受控 `close` 只发 `update:open`；`:101-122` open 时锁 `body overflow=hidden` 并聚焦首个可聚焦元、close 时恢复旧值 + 回焦 trigger，`wasOpen` 守卫保证初始 closed 不碰 body；`drawer.spec.ts` 3 用例覆盖 modal+锁滚+Escape、Tab 循环、遮罩关闭+overflow 恢复；`drawer.md` + 索引齐备；V4/V5 绿）。
- S3 Layout → AC1（sticky 顶栏 + 用户菜单：改密→`/account`，登出→`/login`）：**通过**（`App.vue:4-7` sticky `top-0 z-40 h-16` 顶栏仅认证态渲染；`:69-109` 用户 Trigger 显示邮箱/角色 + 首字母头像，菜单含 `RouterLink /account role=menuitem`（`:92-99`，`@click=close()`）与登出按钮（`:100-107`，`@click=logout`）；`logout`（`:173-177`）执行 `auth.logout + mobileNavOpen=false + push('/login')`；V10 layout.smoke 用户菜单两场景 + V11 用户菜单展开态 a11y 全绿实证）。
- S3 Layout → AC2（桌面收窄/展开 + 收窄仍可访问 + 偏好持久化 + Account 移出侧栏）：**通过**（`:9-17` 收窄切换键 `md:inline-flex`，`aria-label` 在展开/收窄文案间切换，`aria-expanded=!collapsed`；`:114-139` aside `w-60/w-16` 切换，收窄时 RouterLink 以 `aria-label + title` 保留可访问名、短标识 `mark` 保留视觉语义；`COLLAPSED_KEY=workspace2.navigation.collapsed`（`:154`）仅存 `String(boolean)`（`:170`），初值仅读该键（`:158`），不碰认证态；`navItems` 仅三项、无 Account（`:161-165`）；V10 收窄场景断言 `aria-expanded=false` + 链接可访问 + localStorage 为 `'true'` 全绿）。
- S3+S4 → AC3（手机 Drawer：小视口触发、导航后关闭、Escape/遮罩、焦点契约）：**通过**（`:18-27` Drawer trigger `md:hidden`，aside `hidden md:flex`（`:116`），断点一致；抽屉内 RouterLink `@click=close(false)` 路由切换即关且不抢焦（`:55`），另有显式关闭键（`:39-46`）；基元层 Escape/遮罩/Tab/回焦由 S2 覆盖；V10 手机抽屉场景（开抽屉→进模型页→断言 dialog 计数 0）+ V11 抽屉展开态 a11y 全绿）。
- S4+S5 → AC5（中英对称 + e2e/`@a11y` + `api/` 零 diff + `openapi-check` 绿）：**通过**（V12 key 集对称；V10 12/82 + V11 4/21 全绿；V13 `api/` 零 diff + V9 21 路由新鲜；回归面 V1/V2/V3/V6/V7/V8 全绿视为通过）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据；V10/V11 全绿）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；V14 旧锚点逐项可用且浏览器实证全绿；V13/V9 后端零变更）。
- P2：无。
- P3：无（本次为 AC 口径核验，非全面审计，不展开轻微清理项；边际项见 Gaps，如实记录为非缺陷）。
- 结论：`No issues found`。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. `@smoke` 环境抖动记录：连续三次运行失败集合不一致（第 1 次 2 失败 / 第 2 次 3 失败，含 `provider.feature` 登录步 30s 超时与 `auth.steps.ts` 建用户步超时，均为任务书预告的内存压力抖动；第 3 次 12 场景 82 步全绿）。`password.feature`“成员自改密码”场景在第 2 次中报 `toHaveURL(/\/account$/)` 5s 未命中，第 3 次同代码全绿，故同样记为抖动而非回退；未做无证据推断。
2. 死代码残留（`e2e/src/support/nav.ts:9` 的 `'/account': '账号设置'` 表项、`30-35` 的 `logoutViaUI` 及其“侧栏退出按钮”注释）：已无调用方（`rg` 仅剩定义），其中 `logoutViaUI` 的 `getByRole('button',{name:'退出'})` 定位器在新版用户菜单（登出为 `role=menuitem`）下已失效；因无调用方，不影响任何场景（V10/V11 绿），仅记清理项。
3. `DropdownMenu.vue:39` 的 `let restoreFocus = true` 只写不读（`close(restore)` 直接用参数回焦，模块变量无读取点）；无行为影响，仅记清理项。
4. AC2“刷新后偏好保留”仅经 `localStorage` 值断言 + 初始化读取代码（`App.vue:158`）覆盖，e2e 未做 reload 后状态复测；旁路概率低（读写键一致，`toggleCollapsed:168-171` 对称）。
5. 用户菜单的浏览器级键盘操作（trigger 上 ArrowDown/Up 开菜单、菜单内方向键移动）仅由 `dropdown-menu.spec.ts` 单测覆盖，e2e 仅覆盖鼠标点击路径；`@a11y` 展开态扫描已覆盖开菜单后的可访问性。
6. Drawer“初始 closed 不碰 body overflow”仅由 `wasOpen` 守卫（`Drawer.vue:113`）静态覆盖，无 mounting-closed 断言；开→关恢复路径有单测实证（`drawer.spec.ts:57-76`）。
7. PLAN-001~008 回归为抽查口径：全量门禁 + `@smoke` + `@a11y` 全绿即视为通过，未重跑 TEST-001 全部实况探针。
8. 后端集成测试按仓约束默认只在 CI 跑：本地仅执行 `api/tests` 单测域（24 项）。
