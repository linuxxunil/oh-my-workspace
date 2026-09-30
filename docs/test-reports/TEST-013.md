# TEST-013 PLAN-013 pgvector 原生检索下推核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-013.md`（S1–S3，对应 `docs/requirements/REQ-013.md` AC1–AC6）
- 核验时间 / Date：2026-09-30（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up（`postgres :5433` healthy，pgvector/pg15）；dev 库 `alembic_version=0002(head)`；api 直跑未重启；e2e 统一入口经 `:18080/`。
- 本轮改动域（实测）：`git status` 显示 PLAN-013 域 = `M api/src/services/knowledge_service.py` + `?? api/tests/test_knowledge_search.py` + `?? api/scripts/check_vector_parity.py`；`api/controllers/`、`web/openapi.json`、`api/tests/conftest.py`、models 列类型、e2e 零 diff。工作树另有 PLAN-012 遗留未提交改动（`M api/src/config.py`、`M api/src/models.py` 1024→2048、`M api/src/services/provider_service.py`、`?? api/alembic/versions/0002_api_key_2048.py`、`?? api/src/libs/crypto.py`、`?? api/tests/test_crypto.py` 等），本报告只按 PLAN-013 AC1–AC6 verdict，PLAN-012 行为仅在 Gaps 注明归属。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`All checks passed!`（api + sandbox，exit 0） |
| V2 | `make type-check` | 通过：`Success: no issues found in 34 source files`（exit 0） |
| V3 | `make test TARGET_TESTS=./api/tests/test_knowledge_search.py` | 通过：`4 passed in 0.08s`（exit 0） |
| V4 | `make test TARGET_TESTS=./api/tests/test_workflow_engine.py` | 通过：`4 passed in 0.94s`（exit 0，含 retrieval 真实入库种子） |
| V5 | `make test`（全量） | 通过：`34 passed in 7.62s`（含 PLAN-012 遗留 `test_crypto 5` + `test_model_providers 6`，无阻塞；exit 0） |
| V6 | `PYTHONPATH=api uv run --project api alembic -c api/alembic.ini check` | 通过：`No new upgrade operations detected`（exit 0；首次不带 `PYTHONPATH` 因 `env.py:7 import src.models` 报 `ModuleNotFoundError`，属调用姿势问题非缺陷，加 `PYTHONPATH=api` 后绿） |
| V7 | `alembic heads/history` | 通过：`heads=0002 (head)`；`history=<base> -> 0001 -> 0002 (head)`——单 head 无分叉；本轮无新 revision（`git status` 无 `0003*`，AC4 佐证） |
| V8 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0，controller/schema 零改动佐证） |
| V9 | `uv run --project api python api/scripts/check_vector_parity.py`（需 PG :5433） | 通过（exit 0）：`[OK] q='退款' k=2` / `[OK] q='水果物流' k=3` / `[OK] q='关键词' k=1` / `[OK] q='不存在的词xyz' k=3` + `parity OK: _search_pg == _search_python on fixture set`；探针确认临时库 `app_vector_parity` 已删（`pg_database` 查无残留） |
| V10 | `pnpm -C e2e e2e:full -- --tags @smoke`（本轮重跑） | 通过：`12 scenarios (12 passed)`，`82 steps (82 passed)`，reset 回执全 0（exit 0） |
| V11 | `git diff HEAD -- api/src/services/knowledge_service.py` + 只读审查 | 通过：`_ranked` 抽取与旧 `search` 逐行等价（见 AC1）；`_search_pg` 含 `WHERE tenant_id` + `ORDER BY <=> ` + `LIMIT candidate`；`search()` 方言守卫在先，sqlite 永不求值 |
| V12 | `git diff HEAD --stat -- api/src/controllers/ web/openapi.json` / `git status \| grep conftest` | 通过：输出均为空——controllers/schema/openapi/conftest 零改动 |

## 逐条验收结论 / AC Verdicts（REQ-013 AC1–AC6）

- AC1（方言分发：`search()` 按 `db.bind.dialect.name` 分发；`postgresql` 走 `_search_pg`，其他走与现实现逐行等价的 `_search_python`）：**通过**（`knowledge_service.py:95-100`：`bind is not None and bind.dialect.name == "postgresql"` → `_search_pg`，否则 `_search_python`；`_search_python:69-74` 与旧 `search`（diff 前 `58-68`）逐行等价：`embed/query → tokens → filter(tenant).all() → _ranked`；`test_knowledge_search.py:61-68` 锁死 `sqlite` 下 `search == _search_python` 且断言 `dialect.name == "sqlite"`，R2 守卫有单测）。
- AC2（下推算子：`Chunk.embedding.cosine_distance(qv)` 即 `<=>`，`WHERE tenant_id` + `ORDER BY distance` + `LIMIT candidate`，`candidate = max(top_k*10, 50)`）：**通过**（`knowledge_service.py:84` `candidate = max(top_k * 10, 50)`；`:85-91` `filter(Chunk.tenant_id == tenant_id).order_by(Chunk.embedding.op("<=>")(qv)).limit(candidate).all()`——`WHERE + ORDER BY + LIMIT` 三件套齐；实现用 `.op("<=>")` 而非 PLAN 原文 `cosine_distance`，经核为等价且必要：`Chunk.embedding` 列类型是 `models.py:85-105` 自定义 `EmbeddingVector(TypeDecorator)`，其 comparator 无 `cosine_distance` 属性（本地复现 `AttributeError: 'TDComparator' object has no attribute 'cosine_distance'`），`.op("<=>")` 是穿透 TypeDecorator 发射 pgvector 余弦距离算子的正确写法；V9 infra PG 实测 4/4 `OK` 证明算子在 PG 生效）。
- AC3（混合公式复用：终排同一 `tokens()/cosine()`，权重 `0.7/0.3` 不变；候选集覆盖时与全量重排同 `top_k`）：**通过**（`_ranked:58-66` 公式 `0.7*kw + 0.3*cos` 复用 `tokens()`/`cosine()`，`_search_python:74` 与 `_search_pg:92` 同调同一 `_ranked`，语义单点；V3 单测 `test_hybrid_ranking_prefers_keyword_overlap` 锁混合语义（`退款政策` query 召回含 `退款` 行）；V9 同 fixture 对比 `_search_pg == _search_python` 4/4 全等，含 `不存在的词xyz` 空语义 case 与租户隔离断言 `all("隔离租户" not in h)` + t2 自查可用；病态分散数据差异本轮未构造，R1 covering 数已有注释，见 Gaps-2）。
- AC4（零迁移：无新 revision，`alembic check` 零漂移，单 head 不变）：**通过**（V7 单 head `0002` 无分叉、无 `0003*` 新文件；V6 `No new upgrade operations detected`；改动域 `git status` 确认 PLAN-013 未碰 `models.py` 列类型/`EMBED_DIM=32` 不动（`models.py:22`）；工作树 `0002` head 归属 PLAN-012 遗留，`alembic check` 绿即 dev 库 `0002=head`，符合任务书预期）。
- AC5（回归：`test_workflow_engine.py` 全绿含 retrieval 真实入库种子；`conftest.py` sqlite 口径不动）：**通过**（V4 4/4 绿，`test_full_loop_true_branch:59-64` 经 `/documents` 真实建 `退款政策` 文档后 run retrieval 断言 `ctx` 非空 list；V12 `conftest` 零 diff，`conftest.py:1` sqlite 内存库 + `StaticPool` + 外键 `PRAGMA` 口径原样；新增 `test_knowledge_search.py:13-24` 自建独立 sqlite 引擎，不碰 conftest/PG）。
- AC6（红线：controller/schema 零改 `openapi-check` 绿；`make lint/type-check/test` 全绿；`@smoke` 全绿）：**通过**（V12 controllers/openapi 零 diff + V8 21 路由新鲜；V1/V2/V5 门禁全绿；V10 `@smoke` 本轮重跑 `12/12` + `82/82` 全绿）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（无安全泄露/数据丢失/整体不可用证据；V5 34 全绿，V10 smoke 全绿，V9 parity 临时库自删无残留）。
- P1：无（无功能回退/越权/公开契约错误/主流程中断证据；V8 契约新鲜，V4 retrieval 主流程绿）。
- P2：无。
- P3：无（本次为 AC 口径核验，非全面审计，不展开轻微清理项）。
- 结论：`No issues found`。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. PLAN-012 归属：工作树 PLAN-012 遗留（crypto/config/models 2048/provider_service/0002 迁移/test_crypto/api.env.example/release 主密钥节）不在 TEST-013 口径内；V5 全量 34 绿证明其未阻塞本轮回归（含 `test_crypto 5 passed`），其自身 crypto 正确性待 TEST-012 独立 verdict，本报告不代证。
2. R1 病态 case：`candidate = max(top_k*10, 50)` 在 32 维小表全覆盖（V9 fixture 全等），大表近似召回与病态分散数据的允许差异未构造验证；实现注释与 REQ-013 假设已声明另起 REQ 换 embedding/索引，属已知接受风险。
3. PG 算子等价为实证口径：`.op("<=>")` 与 `cosine_distance` 的 SQL 等价性以 V9 infra PG 实测 4/4 全等为证据，未另做 compiled-SQL 文本 diff；sqlite 套件不代证 PG 算子已按 REQ 约束排除在口径外。
4. `alembic check` 调用姿势：裸 `alembic -c api/alembic.ini check`（无 `PYTHONPATH=api`）必现 `ModuleNotFoundError: No module named 'src'`（`env.py:7` 所致），加 `PYTHONPATH=api` 后绿；与既往 TEST-011 口径一致，非缺陷。
5. e2e 为单次重跑绿：V10 本轮重跑一次即 `12/12` 全绿，未观察任务书预告外的抖动；若后续重跑出现失败集合漂移，按既有口径先重跑确认再定级。
