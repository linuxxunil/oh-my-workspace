# 02 Tech Stack / 技术栈（已定）

- 后端 `api/`：Python 3.12 + FastAPI + SQLAlchemy 2 + Pydantic v2 + Celery + uv（统一 `uv run --project api`）。
- 前端 `web/`：Vue 3 + Vite + vue-router + Pinia + TanStack Query for Vue + Vue I18n + Tailwind v4。不引入 React/Next。
- 基元 `packages/ui/`：Vue3 SFC 自研组件库。
- E2E `e2e/`：Cucumber + Playwright，浏览器执行被测动作、API 负责准备与清理的分工。
- 部署 `docker/`：Compose 启动最小 `.env.example`，可选配置收敛到 `docker/envs/*.env.example`。
