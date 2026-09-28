# TEST-001 PLAN-001 首版验收核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-001.md`（S1–S7，对应 `docs/requirements/REQ-001.md` AC1–AC11）
- 核验时间 / Date：2026-09-28（UTC）
- 环境快照 / Env：infra（`docker/compose.infra.yml` postgres/redis/nginx）已 Up；api 直跑 `:18081`（`API_AUTO_MIGRATE=1`）；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`（登录实测均有效，见 AC3）

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!` |
| V2 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 33 source files` |
| V3 | `make test TARGET_TESTS=./api/tests/test_workflow_engine.py` | 通过：`4 passed`（AC1/AC5） |
| V4 | `make test TARGET_TESTS=./api/tests/test_model_providers.py` | 通过：`2 passed`，附 1 条 `DeprecationWarning: setex`（见 F1） |
| V5 | `make test TARGET_TESTS=./api/tests/test_rbac.py` | 通过：`6 passed`（AC3/AC4） |
| V6 | `make test TARGET_TESTS=./api/tests/test_sandbox.py` | 通过：`6 passed`（AC6） |
| V7 | `make test`（全量） | 通过：`18 passed, 1 warning`（同 F1，无失败） |
| V8 | `pnpm --dir web exec vue-tsc --noEmit` | 通过：无输出（退出 0） |
| V9 | `pnpm --dir web exec vitest run --project unit` | 通过：`2 files / 6 tests passed`（`dag.spec.ts` 3 + `mutator.spec.ts` 3） |
| V10 | `pnpm -C e2e e2e -- --tags @smoke` | 通过：`2 scenarios (2 passed)`，`14 steps (14 passed)`（`workflow.smoke.feature`：opencode_go 供应商配置+连通检查；画布 start→code→end 发布运行 `m=42`） |
| V11 | `docker compose -f docker/compose.infra.yml ps` | postgres `Up (healthy)`、redis `Up (healthy)`、nginx `Up`（无 `(healthy)` 后缀，见 F2）。镜像行：`pgvector/pgvector:pg15`、`redis:6-alpine`、`nginx:latest` |
| V12 | `docker images \| head` | 本地含 `pgvector/pgvector:pg15`、`redis:6-alpine`、`nginx:latest`、`python:3.11-slim`（AC11 所列 tag 均可查） |
| V13 | `docker compose exec postgres psql … SELECT … FROM pg_extension WHERE extname='vector'` | `vector 0.8.6` 已启用；`server_version 15.19` |
| V14 | `docker compose exec redis redis-cli ping / --scan` | `PONG`；存在 `models:<tenant>:<provider>` 缓存键（2 条，模型列表缓存命中可用） |
| V15 | `curl` 入口连通 | 直连 `GET :18081/health` 200；经 nginx `GET :18080/api/health` 200、`GET :18080/` 200（text/html）、`GET :18080/sandbox/health` 200（`{"ok":true}`） |
| V16 | `curl POST :18080/api/auth/login`（root/member）+ `GET :18080/api/users` 无 token + `POST :18080/api/models/providers`（member） | root 登录返回 `access_token`；无 token 调 `GET /api/users` 返回 `401 {"detail":"未登录"}`；member 建供应商返回 `403 {"detail":"缺少权限 models:write"}` |
| V17 | `curl POST :18091/execute`（正常/出网探测） | 正常 `{"result":42,"exit_code":0,"timed_out":false}`；`socket.create_connection(("8.8.8.8",53))` 探测以 `TimeoutError: timed out` 失败、`exit_code=1`（无外网通路，符合“无网络”预期；超时杀死由 V6 `test_local_timeout` 覆盖 `timed_out=True, exit_code=124`） |
| V18 | `grep -n "docker build" docs/release.md` + `find . -maxdepth 3 -name "Dockerfile*"` | `docker build` 仅出现在 `docs/release.md` 发布节（3 行，对应 `docker/Dockerfile.{api,web,sandbox}.release`）；开发期无应用 `Dockerfile.*` 构建步骤 |
| V19 | 源码阅读（只读） | `api/src/services/workflow_service.py:62-72` 画布保存只走“冻结旧版+新增一版”，无已发布版本原地改 DAG 路径；`web/src` 含 `views/CanvasView.vue`（VueFlow，节点 kinds `llm/code/if/retrieval/end`）、`i18n/zh-CN.json` + `en-US.json`、`service/generated/api.ts`（orval 生成式客户端）、`utils/dag.ts`（DAG JSON 往返，V9 覆盖） |

## 逐条验收结论 / AC Verdicts（S1–S7 → AC1–AC11）

- S1 Infra → AC9（nginx 唯一入口 `/api/` `/` `/sandbox/`）：**通过**（V11/V15 三路由均 200）。严格字面“`ps` 三 infra healthy”有一处体裁偏差见 F2，不影响连通性。
- S1 Infra → AC10（开发期本地直跑、仅发布含 build）：**通过**（V18；api/web/sandbox 均为直跑端口实测可用）。
- S1 Infra → AC11（仅引用本地已有 tag）：**通过**（V11/V12；`compose.infra.yml:10,27,40` 仅引用 `pgvector/pgvector:pg15` / `redis:6-alpine` / `nginx:latest`，`docker images` 均可查）。
- S2 → AC3（未登录 401；member 调用户管理/模型写入 403）：**通过**（V5 单测 6 项 + V16 实况 401/403 双证据）。
- S2 → AC4（三角色用户 CRUD 与权限矩阵）：**通过**（V5：admin 可建/删 member、不可授 super_admin、不可删 super_admin；super_admin 可读写角色权限；admin 写权限 403）。
- S3 → AC2（双通道 CRUD+连通检查+redis 缓存）：**通过**（V4：`openai_compatible` + `opencode_go` 双建、泄漏检查 `api_key` 不在返回体、member 建 403、mock 连通 `model_count=2`、上游故障后缓存仍命中；内网 `base_url` 400 拦截。实况 V14 确认 redis 缓存键存在）。
- S4 → AC1（含 llm/code/if/retrieval 的 DAG 编译执行）：**通过**（V3：true/false 双分支、mock llm+sandbox、retrieval 检出中文知识 `ctx` 非空、非法 DAG 422）。
- S4 → AC5（CRUD+版本/发布+运行历史，发布版本不可变）：**通过**（V3：发布 `is_published=True`、版本递增 `version_no=2`、运行历史 2 条、member 无 `workflows:write` 删 403、删流程级联后 versions/runs 404；V19 确认无原地改已发布版本路径）。
- S4 → AC8（postgres+pgvector 同库，redis 缓存）：**通过**（V13/V14）。
- S5 → AC6（Python 正常/异常/超时三用例，超时杀死、无网络）：**通过**（V6 六项：本地三用例 + client HTTP 路径 + 回环放行 + `169.254.169.254` SSRF 拦截；V17 实况复核正常执行与出网不可达）。
- S6 → AC7（VueFlow 拖拽连线存取 DAG JSON，生成式客户端为准，`vue-tsc` 通过）：**通过**（V8/V9 + V19：`CanvasView.vue` + `utils/dag.ts` + `service/generated/api.ts` 链路存在且类型/单测通过）。浏览器内拖拽手势本身由 V10 烟雾场景间接覆盖（画布连线 start→code→end 并保存新版本后运行成功）。
- S7 → AC9 全链（nginx 联调+E2E smoke）：**通过**（V10 2 场景 14 步全绿 + V15 入口三路由 200）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；401/403、SSRF 拦截、版本不可变均符合契约）。
- P2：无。
- P3-1（可维护性/未来兼容）：`redis.setex` 已废弃调用。
  - 文件行号：`api/src/services/cache.py:41`（`c.setex(key, ttl_s, raw)`）。
  - 复现/证据：V4/V7 每次运行均输出 `DeprecationWarning: Call to deprecated setex. (Use 'set' instead.) -- Deprecated since version 2.6.12`（`tests/test_model_providers.py::test_provider_crud_and_test_connection`）。
  - 影响面：当前功能正常（缓存命中 V4/V14 均通过）；未来 `redis-py` 移除旧 API 时模型列表缓存写入路径可能异常。
  - 修复方向：改用 `c.set(key, raw, ex=ttl_s)` 并以 V4 回归验证（仅建议，不承揽）。
- P3-2（AC 字面体裁/可观测性）：nginx 缺健康检查，`ps` 显示为 `Up` 而非 `(healthy)`。
  - 文件行号：`docker/compose.infra.yml:39-48`（`nginx` 段无 `healthcheck`；对比 `postgres:21-25`、`redis:33-37` 有）。
  - 复现/证据：V11 输出 `oh-my-workspace2-nginx-1 … Up 7 hours`（无 `(healthy)` 后缀），而 REQ-001 AC9 字面为“`docker compose ps` 三 infra healthy”。
  - 影响面：功能无影响（V15 三路由均 200）；仅 `ps` 观感与 AC 字面不一致，以及编排层面缺 nginx 就绪门。
  - 修复方向：为 `nginx` 补 `healthcheck`（如 `CMD-SHELL, curl -f http://localhost/api/health || exit 1`，注意容器内 `curl` 可用性或改用 `wget`），以 V11 复核三 `(healthy)`（仅建议，不承揽）。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. `GET /api/users/`（尾斜杠）经 nginx 返回 `307` 而非 `401`；属 FastAPI `redirect_slashes` 规范跳转，规范路径 `GET /api/users` 实测 `401` 正确（V16），不记为问题。浏览器/E2E 均走生成式客户端规范路径。
2. `opencode-go` 原生协议真实连通未验证：V4/V10 均以 mock/示例地址覆盖连通检查路径；REQ-001 假设“spike 失败降级 OpenAI-compatible”（PLAN-001 R1）依然有效，真实远端协议差异不在本次证据内。
3. 沙箱“进程级隔离”上限：内核级逃逸按 REQ-001 明确不在首版承诺内，本次仅验证超时杀死、无外网、异常捕获；未做逃逸/资源耗尽压测。
4. 前端手势级断言缺口：画布拖拽连线以 V9 单元（DAG 往返）+ V10 烟雾（连线保存发布运行）间接覆盖；无逐像素拖拽与无障碍（`@axe/@wcag`）专项运行。
5. `web/openapi.json` 新鲜度未做 diff 门禁：本次确认生成器链路存在（`Makefile:24-25 openapi` + `web/service/generated/api.ts` orval 产物）且 `app.openapi()` 实测 `20` 路由，但未逐字段比对落盘契约是否过期。
6. 后端集成测试按仓约束默认只在 CI 跑：本次本地仅执行 `api/tests` 单测域（18 项）+ 实况探针；DB 迁移幂等/并发发布竞态等长尾路径无覆盖。
