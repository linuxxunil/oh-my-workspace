# PLAN-013 pgvector 原生检索下推

- 关联 REQ / Linked REQ：`docs/requirements/REQ-013.md`（AC1–AC6）。
- 范围 / Scope：`api/src/services/knowledge_service.py`（方言分发 + `_search_pg` + 共享打分抽取）+ 新增 `api/tests/test_knowledge_search.py` + 可选 `api/scripts/check_vector_parity.py`（PG 临时库 parity，自建自删）。不碰 models/列类型/controllers/seed/lifespan/conftest/web/packages/ui/e2e；无新 revision；无新依赖。
- 架构 / Architecture：
  - `search()` 按 `db.bind.dialect.name` 分发：`postgresql` → `_search_pg`，其他 → `_search_python`（现有 58–68 行逻辑原样下沉）。
  - 共享 `_ranked(qv, qt, rows)`：抽取现有 `kw/cos` 公式（`0.7*kw + 0.3*cos`，复用 `tokens()`/`cosine()`），两路径终排共用。
  - `_search_pg`：`db.query(Chunk).filter(tenant).order_by(Chunk.embedding.cosine_distance(qv)).limit(candidate)`（`candidate=max(top_k*10,50)`）取回后 `_ranked` 重排取 `top_k`；sqlite 下该算子永不求值（守卫在先）。
- 开发步骤 / Steps：
  | Todo | 改动 | 验收 | 验证命令 |
  |---|---|---|---|
  | S1 | 分发 + `_ranked` 抽取 + `_search_python` 下沉（零语义差）+ 新增 `test_knowledge_search.py`（混合公式/空库/top_k 截断/tenant 隔离） | AC1+AC3+AC5 | `make lint type-check` + `make test TARGET_TESTS=./api/tests/test_knowledge_search.py` + `make test TARGET_TESTS=./api/tests/test_workflow_engine.py` |
  | S2 | `_search_pg` + infra PG 临时库 parity（同 fixture 对比全量重排 top_k，临时库自建自删） | AC2+AC3 | `uv run --project api python api/scripts/check_vector_parity.py`（需 `infra-up` 的 PG :5433）+ `alembic check`（AC4） |
  | S3 | 收尾：全门禁 + TEST-013 + 本地 commit | AC6 | `make lint type-check test` + `make openapi-check` + `pnpm -C e2e e2e:full -- --tags @smoke` |
- 风险 / Risks：R1 候选集未覆盖致排序漂移 → covering 数 `max(top_k*10,50)` + TEST 注明病态 case；R2 pgvector 算子在 sqlite 误求值 → dialect 守卫 + 单测锁死（PG 分支在 sqlite 下不可达）；R3 32 维占位向量区分度低 → 本轮只做下推，不换 embedding 模型（另起 REQ）。
- 验证命令 / Verification：`make lint type-check test` / `make test TARGET_TESTS=./api/tests/test_knowledge_search.py` / `make test TARGET_TESTS=./api/tests/test_workflow_engine.py` / `alembic check` / `make openapi-check` / `pnpm -C e2e e2e:full -- --tags @smoke`。
