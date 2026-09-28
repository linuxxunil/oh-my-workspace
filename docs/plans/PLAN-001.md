# PLAN-001 Dify 同级平台首版实现

- 关联 REQ / Linked REQ：`docs/requirements/REQ-001.md`（AC1–AC11）。
- 范围 / Scope：`api/`（auth/rbac/users/models/workflows/sandbox-client/knowledge 最小）、`web/`（登录/用户/模型/workflow 画布）、`docker/`（infra compose + nginx conf + env 示例）、`e2e/`（smoke）。owner：controller 薄层、service 编排、`core/` 领域（LangGraph 编译/RBAC 判定）、SSRF-safe 出站 owner。边界：不碰 `packages/ui` 基元实现（只复用）；不引入 React；开发期不新增应用 `Dockerfile.*`。
- 架构 / Architecture：
  - 入口：`nginx:latest` 反代 `/api/→api:8000`、`/`→web:5173、` /sandbox/→sandbox:8080`。
  - 数据：`pgvector/pgvector:pg15` 同库（业务表 `tenant_id` + `pgvector` 向量表），`redis:6-alpine`（模型列表/会话缓存 + Celery broker 预留）。
  - 后端：FastAPI + SQLAlchemy2 + Pydantic v2 + LangGraph；`ModelProvider(type=openai_compatible|opencode_go)` 抽象；DAG JSON（start/llm/code/if/retrieval/end）→ LangGraph 编译；code 节点经 SSRF-safe 调 sandbox；版本发布不可变 + 运行历史。
  - 前端：VueFlow 自研画布 ↔ DAG JSON ↔ 生成式客户端（orval）；pinia/vue-router/Vue Query；i18n 中英。
  - 沙箱：以本地 `python:3.11-slim` 为底自建，仅 Python，无网络，超时+内存限。
- 开发步骤 / Steps：
  - S1 Infra：新建 `docker/compose.infra.yml`（postgres/redis/nginx 三服务，均用本地 tag）+ `docker/nginx/default.conf` + `docker/envs/*.env.example` + 仓根 `Makefile`（lint/type-check/test 透传）。验收：AC9/AC10/AC11。验证：`docker compose -f docker/compose.infra.yml ps`、`docker images | rg 'pgvector|redis|nginx|python'`。
  - S2 Auth+RBAC+用户：`api/` 脚手架（pyproject、config owner、models、alembic）+ JWT 登录 + 三角色权限矩阵 + 用户 CRUD/权限 API。验收：AC3/AC4。验证：`make lint`、`make test TARGET_TESTS=./api/tests/test_rbac.py`。
  - S3 模型双通道：Provider CRUD + 连通性检查 + redis 缓存 + opencode-go spike（失败则降级）。验收：AC2。验证：`make test TARGET_TESTS=./api/tests/test_model_providers.py`。
  - S4 Workflow+RAG最小：DAG schema + LangGraph 编译 + 版本/发布/运行历史 + 文档分块/embedding/pgvector 检索。验收：AC1/AC5。验证：`make test TARGET_TESTS=./api/tests/test_workflow_engine.py`。
  - S5 沙箱：`sandbox/` 服务（FastAPI 或最小 HTTP，直跑）+ 限时限内存无网 + 后端 client。验收：AC6。验证：`make test TARGET_TESTS=./api/tests/test_sandbox.py`。
  - S6 前端：web 脚手架 + 生成客户端 + 登录/用户/模型/workflow(VueFlow)页 + i18n。验收：AC7。验证：`vue-tsc --noEmit`（web/ 下）、`vp test run --project unit`。
  - S7 入口+E2E+发布：nginx 联调 + `e2e/features/workflow.smoke.feature` + 发布时 Dockerfile 说明。验收：AC9 全链。验证：`pnpm -C e2e e2e -- --tags @smoke`。
- 风险 / Risks：R1 opencode-go 协议未知→spike 降级；R2 沙箱仅进程级隔离；R3 空仓脚手架量大→S1 先立 Makefile/compose 约束后续；R4 LangGraph 版本 pin（`langgraph>=0.2,<0.3` 待 S4 锁定）。
- 验证命令 / Verification：`make lint` / `make type-check` / `make test` / `make test TARGET_TESTS=./api/tests/<path>` / `vp check web`+`vue-tsc --noEmit`（web/ 下）/ `vp test run --project unit` / `pnpm -C e2e e2e -- --tags @smoke`。
