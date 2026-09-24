# AGENTS.md

> 双语说明 / Bilingual note: 标题用英文，方便模型与工具检索；正文用中文，关键术语保留英文。
> Title in English for model/tool retrieval; body in Chinese with key terms kept in English.

本仓是 LLM 应用平台（Monorepo）。后端在 `api/`、前端在 `web/`（Vue3）、共享 UI 在 `packages/ui/`、部署在 `docker/`、端到端在 `e2e/`。

## Ground Rules / 铁律

1. 就近优先最近的 scoped `AGENTS.md`（Follow the nearest scoped `AGENTS.md`）。根文件只画地图，具体命令与边界以各包文件为准。
2. 用户显式指令优先于 workflow 默认（Explicit user instructions take precedence over workflow defaults）。
3. 没有 `docs/plans/PLAN-xxx.md` 不进入 build；没有验收标准不自行定义完成。
4. 结论必须附依据（验收条目或契约引用），缺依据（无验收/无契约引用）的结论按 P2 打回。
5. 后端命令统一 `uv run --project api`；后端集成测试默认只在 CI 跑，本地不强制拉起。
6. 前端统一 Vue3 + Vite，不引入 React/Next；状态、路由、查询分别归 Pinia / vue-router / TanStack Query for Vue。
7. 无落盘 Todo 不开工，不按 Todo 不合入。
8. 一次完整交付必进版本（仅本地 commit，无 TEST 不合入版本）。

## Repo Map / 仓地图

- `api/AGENTS.md`：Python/FastAPI 后端的现状与命令。
- `web/AGENTS.md`：Vue3 前端的现状与命令。
- `packages/ui/AGENTS.md`：共享 Vue 基元库的契约。
- `e2e/AGENTS.md`：Cucumber + Playwright 套件的契约。
- `.opencode/agents/`：`tester` 专职 subagent；规划由内置 `plan` 主 agent 落盘（需求澄清加规划）。
- `.opencode/skills/`：code-review 与组件写作技能，按需加载。
- `docs/dev-spec/`：开发规范 Single Source of Truth。
