# 01 Workflow / 开发流程（强制）

本流程只使用 opencode 原生能力（`.opencode/agents + commands`），不另建 `.claude/.agents` 兼容层。

## State Machine / 状态机（内置 plan 一步到位）

1. **规划**：`/plan <模糊需求或REQ号>` → 内置 `plan` 主 agent 先澄清追问并落盘 `docs/requirements/REQ-xxx.md`（含验收标准），再落盘 `docs/plans/PLAN-xxx.md`（架构加步骤加验证命令），该阶段不写业务码。你在 plan 模式下 Review。
2. **开发**：你切换到 build 模式 → `/build-step PLAN-xxx.md:步骤` 逐步推进，每步跟一次验证（`make lint/test`、`vp test --project unit`、`vue-tsc`）。
3. **测试**：`/test PLAN-xxx.md` → `@tester` 输出 `docs/test-reports/TEST-xxx.md`（P0-P3），不碰业务源码；缺陷退回 build，复检后闭环。
4. **交付进版**：TEST 无 P0/P1 且你 Review 通过视为一次完整交付，必须仅本地 commit（一 PLAN 一 commit，不 push），信息格式 `<type>(scope): PLAN-xxx <事>`。

## Gates / 门禁

- 需求不清必须用 `question` 追问到可写验收标准为止，不设轮次上限，禁猜测推进；无验收标准的 REQ 视为未完成，不进 PLAN。
- PLAN 必须含编号 Todo 表（每步：改动+验收+验证命令）；build 只能按 Todo 号执行，不跳步不加戏，违者 tester 按 P2 打回。
- PLAN 没有落盘不视为完成；没有 `PLAN-xxx.md` 不进入 build；没有 `TEST-xxx.md` 不视为交付完成；无 TEST 不 commit 进版本。
- plan 主 agent 只允许写入 `docs/requirements/**` 与 `docs/plans/**`，写出该范围 tester 按 P2 打回。
- 禁 `--no-verify` 绕过检查。
- 用户显式指令优先于 workflow 默认。

## Pre-approval / 事前一次授权（REQ-003 AC4 落款）

- build 开工前，执行方必须把本轮所需的全部权限一次性列清（服务起停、依赖安装与下载、测试数据增删、本地 commit、是否需要外部网络/凭证），经用户一次批复后执行。
- 批复后中途不得再为权限类事项打断用户；Todo 必须一次性全部做完再交付，不分段汇报。
- 例外：需求不清、缺验收标准等门禁类追问不受此限，仍必须问（见 Gates 第一条）。
