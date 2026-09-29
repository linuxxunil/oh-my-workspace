# TEST-005 PLAN-005 画布美化二期验收核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-005.md`（S1/S2/S3/S4，对应 `docs/requirements/REQ-005.md` AC1–AC4）
- 核验时间 / Date：2026-09-29（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`
- 本轮改动域（`git status` + `git diff --stat HEAD` 实测）：`web/package.json`（`@vue-flow/minimap@^1.5.4` + `@vue-flow/controls@^1.1.3` + `@vue-flow/background@^1.3.2` 三运行时依赖）+ `web/pnpm-lock.yaml`（+44 行）+ `web/src/main.ts`（+2 行：controls/minimap css）+ `web/src/views/CanvasView.vue`（chrome + 类型表单 + draft/applyConfig + 边样式 + UiButton）+ `web/src/components/CanvasNode.vue`（新增 untracked 文件，自定义节点）+ `web/src/i18n/zh-CN.json` + `en-US.json`（各 +18 行，`canvas.*` 16 键）+ `e2e/src/steps/workflows.steps.ts`（画布步骤改填代码/输出键，±7 行）。`api/`、`web/openapi.json`、`packages/ui/` 零 diff。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!`（exit 0） |
| V2 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 33 source files`（exit 0） |
| V3 | `make test`（全量） | 通过：`22 passed`（与 TEST-004 一致，无失败；后端零改动下的回归基线） |
| V4 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0） |
| V5 | `git diff --stat HEAD -- api/ web/openapi.json` | 空输出（后端零改动，AC4 文件口径） |
| V6 | `make web-check` | 通过：`pnpm --dir web exec vue-tsc --noEmit` 无输出（exit 0，含新增 `CanvasNode.vue` + 表单模板） |
| V7 | `make web-test` | 通过：`2 files / 6 tests passed`（`dag.spec.ts` 3 + `mutator.spec.ts` 3，往返转换单测仍绿） |
| V8 | `make ui-test` | 通过：`6 files / 17 tests passed`（`packages/ui` 本轮零改动，回归绿） |
| V9 | `make ui-check` | 通过：`pnpm --dir packages/ui check`（exit 0） |
| V10 | `make web-build` | 通过：`✓ built in 1.20s`（`CanvasView` chunk 229.41 kB 含 minimap/controls，AC1 构建口径） |
| V11 | `pnpm -C e2e e2e -- --tags @smoke` | 通过：`5 scenarios (5 passed)`，`34 steps (34 passed)`（画布场景经新类型表单配出 `m=42` 全绿） |
| V12 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`2 scenarios (2 passed)`，`10 steps (10 passed)`（登录页 + 画布页零 critical/serious，Controls 新增控件已具可访问名） |
| V13 | 键名对照（只读）：`CanvasView.vue:268-284 applyConfig` vs `api/src/core/graph.py:43-86` | 一致：llm（`provider_id/model/prompt/output_key` ↔ graph.py:43-51）/ code（`code/output_key` ↔ :55-62）/ retrieval（`query/top_k/output_key`，`Number>0 否则 3` ↔ :66-74 `int(cfg.get("top_k", 3))`）/ if（`var/equals` ↔ :81-85） |
| V14 | i18n 对照（只读）：`zh-CN.json:55-72` vs `en-US.json:55-72` | `canvas.*` 16 键（code/outputKey/prompt/model/provider/query/topK/varName/equals/noConfig/selectProvider/loadingProviders/zoomIn/zoomOut/fitView/toggleInteractive）中英 key 集合完全一致 |
| V15 | 旧锚点审查（只读）：`rg "config JSON" web/src` + `git diff HEAD -- e2e/` | `web/src` 内零命中（裸 `config JSON` textarea 已移除）；`e2e` 仅 `workflows.steps.ts` 一处改写（代码/输出键两栏 + 保存配置，旧定位器删除为预期内），其余 feature/steps 零 diff |

## 逐条验收结论 / AC Verdicts（PLAN-005 S1/S2/S3 → REQ-005 AC1–AC4）

- S1 chrome → AC1（Minimap + Controls + 点阵背景 + 边样式落地，`web-build` 通过）：**通过**（V10 构建成功；`CanvasView.vue:22-24` Background/MiniMap/Controls 三件套 + `:332-354` 边样式 slate 默认/indigo 选中；`web/package.json:16-19` 三依赖 `^1` 对齐 core 1.42；`main.ts:10-13` 四份 css 引入；V12 画布页 axe 绿）。
- S2 自定义节点 → AC2（六类型配色 + 选中环，点击/选中/连线行为不变）：**通过**（`CanvasNode.vue:25-32` 六类型配色点 start 石墨/llm 紫/code 翡翠/if 琥珀/retrieval 天蓝/end 深 slate + `:4-7` selected 环；`CanvasView.vue:193` nodeTypes 注册 + `:214,226` addNode/load 统一 `type:'flowNode'`；V11 画布场景绿：selectNode 重试 + `selected` 类断言 + 双边拖拽连线 + 删 e1 直连硬断言全过）。
- S3 类型表单 → AC3（code 场景经表单配出 `m=42`；裸 JSON 移除；中英同步）：**通过**（V11 画布场景：填“代码”`result = data["n"] * 2` + “输出键”`m` → 保存配置 `ok` → 保存版本 → 发布运行，见 `workflows.steps.ts:94-99,119-127`；V15 裸 `config JSON` 零残留；V14 16 键中英同构；llm 供应商下拉数据源自 `useListProvidersModelsProvidersGet`，见 `CanvasView.vue:203-207`）。
- S4 收尾 → AC4（`openapi-check` 绿且后端零 diff；PLAN-001~004 回归面）：**通过**（V4 21 路由新鲜 + V5 `api/ + web/openapi.json` diff 为空；V1/V2/V3 后端门禁全绿 22 项 + V6/V7/V8/V9/V10 前端门禁全绿 + V11/V12 `@smoke/@a11y` 全绿，视为回归通过）。
- PLAN-001~004 回归面 → **通过**（同上；未重做 TEST-001 全部实况探针，见 Gaps）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据；后端零改动）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；V11/V12 全绿，键名对照 V13 逐键一致）。
- P2：无。
- P3-1（i18n 卫生）：`canvas.selectProvider` 中英各一键无消费者。
  - 文件行号：`web/src/i18n/zh-CN.json:66` + `web/src/i18n/en-US.json:66` vs 全仓 `rg selectProvider` 仅命中上述两行（`CanvasView.vue` 模板内无引用，llm 供应商栏直用 `canvas.provider`，见 `CanvasView.vue:39-48`）。
  - 复现/证据：只读 grep；AC3“中英同步”不受影响（两边对称多出一键，V14 集合仍一致）。
  - 影响面：功能无影响；后人误以为供应商下拉有独立占位文案。
  - 修复方向：若无占位需求则删除该键（中英同删），或在 Select 加 `placeholder=t('canvas.selectProvider')` 后保留；以 V6/V11 回归验证（仅建议，不承揽）。
- P3-2（PLAN措辞漂移/可维护性）：两处实现与 PLAN-005 架构段字面不完全一致，功能等价。
  - 文件行号：a) `docs/plans/PLAN-005.md:7`（`label 保留 ${type}:${id}`）vs `web/src/views/CanvasView.vue:228`（`label: kind`，本轮 diff 上下文行，沿用旧值）+ `web/src/utils/dag.ts:11`（`toVueFlow` 置 `${n.type}:${n.id}`）+ `dag.ts:31-36`（`fromVueFlow` 只读 `id/data/position`，不读 label）；b) `PLAN-005.md:6`（Background“用 core 自带”）vs `CanvasView.vue:136`（`from '@vue-flow/background'` 独立包导入）。
  - 复现/证据：只读审查 + V7（dag 往返单测绿，label 不参与往返）+ V10（独立包构建成功）+ V11（保存版本/运行绿，label 差不透出后端）。
  - 影响面：功能零影响（自定义节点渲染 `data.nodeType` 文本，不读 label；background 包即 v1 官方插件，`web/package.json:16` 已声明 `^1.3.2`）。
  - 修复方向：订正 PLAN-005 架构段为“addNode label 沿用 kind（fromVueFlow 不消费 label）”与“Background 取自 `@vue-flow/background` 官方包”；或保持现状（仅建议，不承揽）。
- P3-3（表单完整性/体验收口）：start/end 无配置节点仍展示提交按钮，点击后以空配置覆盖并报 `ok`。
  - 文件行号：`web/src/views/CanvasView.vue:35-37`（`noConfig` 说明）+ `:107-109`（提交按钮无 kind 条件）+ `:268-284`（start/end 落入 `config = {}` 默认分支）。
  - 复现/证据：只读审查；选中 start 节点→点“保存配置”→`notice='ok'` 且 `data.config` 被置 `{}`（原值若有则丢失）。
  - 影响面：当前无功能损害（start/end 为 passthrough，后端忽略 config；blankDag 两节点 config 本就 `{}`）；属误导性可点按钮。
  - 修复方向：start/end 时隐藏提交按钮（仅保留 `noConfig` 说明），以 V11 回归验证（仅建议，不承揽）。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. llm/retrieval/if 三类表单仅静态键名对照（V13）+ 类型检查（V6），无浏览器端到端用例（`@smoke` 画布场景只走 code `$m=42$` 路径；llm 需外部模型、`@external-model` 默认排除，故 retrieval/if 同理无在线场景）。
2. 六类型配色点的视觉断言（色值/左色条/选中环像素）无浏览器截图比对；V11 仅断言 `.vue-flow__node.selected` 类（VueFlow 核心语义）+ 连线/保存/运行行为。
3. Minimap 缩放/平移交互与 Controls 四按钮点击行为无功能断言；V12 仅覆盖 axe `button-name`（经 `onMounted:178-189` 补 aria-label 后绿）。
4. PLAN-001 回归为抽查口径：全量门禁 + `@smoke` + `@a11y` 全绿即视为通过，未重跑 TEST-001 V11–V19 全部实况探针。
5. 后端集成测试按仓约束默认只在 CI 跑：本地仅执行 `api/tests` 单测域（22 项）。
6. `web/src/components/` 为本轮新增 untracked 目录（`CanvasNode.vue`），`git diff --stat` 正文不含其行数，改动域描述以 `git status` 补齐。
