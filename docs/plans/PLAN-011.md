# PLAN-011 alembic 正式迁移

- 关联 REQ / Linked REQ：`docs/requirements/REQ-011.md`（AC1–AC8）。
- 范围 / Scope：`api/alembic.ini` + `api/alembic/`（env + versions）+ `api/src/main.py` lifespan + `api/scripts/check_migration_parity.py` + `docs/release.md`。不碰 models/seed/controllers/web/e2e/conftest；不新增 Makefile 目标与依赖。
- 架构 / Architecture：
  - env.py：`config.set_main_option("sqlalchemy.url", settings.database_url)`；`target_metadata=Base.metadata`（`import src.models` 注册）；`compare_type=True`；online/offline 双模式；`PYTHONPATH=api` 下 `uv run --project api alembic -c api/alembic.ini` 直调。
  - 基线 revision：autogenerate 生成后人工核 10 表/ENUM create_type/`Vector(32)` import/索引 UQ FK；`upgrade()` 首行 `op.execute("CREATE EXTENSION IF NOT EXISTS vector")`；`downgrade()` 逆向 drop（含 `ENUM(...).drop`，extension 保留）。
  - lifespan：`auto_migrate` 分支内 `Base.metadata.create_all` → 编程化 `command.upgrade(cfg, "head")`（Config 覆写 url），`CREATE EXTENSION` 语义由 revision 承接后 lifespan 内去重（仅 revision 负责，避免双写漂移）；seed 守门原样。
  - 校验脚本：建临时库 `app_migcheck`（upgrade head）vs 内存比对 `create_all`（同 PG 另一临时库或 inspector 对 metadata），diff 表/列类型/索引/UQ/FK/枚举；用后删库。
- 开发步骤 / Steps：
  - S1 脚手架。验收 AC1。验证：`PYTHONPATH=api uv run --project api alembic -c api/alembic.ini current/history`（空库无报错）。
  - S2 基线 revision + `--sql` 审稿。验收 AC2。验证：`upgrade head --sql` 审 SQL；空库 `upgrade head` 建表成功。
  - S3 lifespan 接入。验收 AC3。验证：空库 `make dev-api` 建表+seed；二次启动幂等；`auto_migrate=0` 不碰库。
  - S4 一致性校验脚本 + 本地跑绿。验收 AC5。验证：`uv run --project api python api/scripts/check_migration_parity.py`（需 `infra-up` 的 PG :5433）。
  - S5 回滚重放 + 现 dev 库 `stamp head` 实操。验收 AC4+AC6。验证：`downgrade base → upgrade head → S4`；dev 库 `current==head`。
  - S6 `docs/release.md` 发布前迁移步骤。验收 AC7。验证：文档 review。
  - S7 收尾：`make lint type-check test` + `openapi-check` + `@smoke` 全绿 + TEST-011 + 本地 commit。验收 AC8。
- 风险 / Risks：R1 autogenerate 漏 native ENUM → S2 人工核 + `--sql` 审稿兜底；R2 `Vector(32)` import 缺失 → S2 核 imports；R3 本机内存压力 e2e 登录抖动 → 失败集合漂移则重跑确认为环境问题（TEST-009/010 既定口径）。
- 验证命令 / Verification：`make lint type-check test` / `make openapi-check` / `pnpm -C e2e e2e:full -- --tags @smoke`。
