# TEST-011 PLAN-011 alembic 正式迁移核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-011.md`（S1–S7，对应 `docs/requirements/REQ-011.md` AC1–AC8）
- 核验时间 / Date：2026-09-29（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`（已加载新 lifespan，未重起服务）；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。dev 库预置状态：`alembic_version=0001`（已 `stamp head`）、业务表不动、`users=3`。
- 本轮改动域（实测）：tracked 2 文件（`api/src/main.py` lifespan、`docs/release.md` DB 迁移节）+ untracked 4 项（`api/alembic.ini`、`api/alembic/`（env.py + script.py.mako + versions/0001_baseline.py）、`api/scripts/check_migration_parity.py`、`docs/plans/PLAN-011.md` + `docs/requirements/REQ-011.md`）。`api/src/models.py`、`api/controllers/`、`api/tests/`（含 conftest）、`web/`、`packages/`、`e2e/` 零 diff。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`All checks passed!`（api + sandbox，exit 0） |
| V2 | `make type-check` | 通过：`Success: no issues found in 33 source files`（exit 0） |
| V3 | `make test` | 通过：`24 passed in 6.46s`（exit 0，sqlite conftest 口径未动） |
| V4 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0，controller/schema 零改动佐证） |
| V5 | `alembic -c api/alembic.ini current/history/heads`（`PYTHONPATH=api`） | 通过：`current=0001 (head)`；`history=<base> -> 0001 (head), baseline`；`heads=0001 (head)`——单 head，无分叉 |
| V6 | `alembic -c api/alembic.ini check` | 通过：`No new upgrade operations detected`（metadata 与已迁移 dev 库零漂移） |
| V7 | `python api/scripts/check_migration_parity.py`（`PYTHONPATH=api`，本地重跑） | 通过：`parity OK: upgrade head == create_all (10 tables, enums, indexes)`（exit 0；两临时库 `app_parity_mig/app_parity_ddl` 用后自删） |
| V8 | `alembic upgrade head --sql`（offline 审稿） | 通过：首条 `CREATE EXTENSION IF NOT EXISTS vector`，随后 10 表全量 `CREATE TABLE`（exit 0） |
| V9 | `alembic downgrade head:base --sql`（offline 审稿，未碰 dev 数据） | 通过：逆向 drop 全 10 表 + `DROP TYPE role` + `DROP TYPE providertype`，无 `DROP EXTENSION`（extension 保留符合 AC2） |
| V10 | dev 库实况探针（只读 SQL） | 通过：11 表名 = 10 业务表 + `alembic_version`；`version_num=('0001',)`；`users=3`（stamp 保数据）；`vector` 扩展 present；`role/providertype` 双 ENUM present |
| V11 | `git diff HEAD -- api/src/models.py api/controllers api/tests/conftest.py api/tests e2e web packages` | 输出为空（exit 0，AC8 红线：models/controllers/conftest/e2e/web 零改动） |
| V12 | e2e reset 只读审查（`e2e/src/support/api.ts:93-120`） | 通过：`resetE2EResources` 纯生成式 oRPC 删除（流程→供应商→用户，先子后主，E2E 前缀过滤），无 SQL、无 `alembic_version` 触碰 |
| V13 | `pnpm -C e2e e2e:full -- --tags @smoke` | 通过（一次全绿，无需重跑）：`12 scenarios (12 passed)`，`82 steps (82 passed)`；reset 回执 `{"workflows":0,"providers":0,"users":0}`；本轮未触发任务书预告的 30s 登录超时抖动 |
| V14 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`4 scenarios (4 passed)`，`21 steps (21 passed)` |

## 逐条验收结论 / AC Verdicts（REQ-011 AC1–AC8）

- AC1（脚手架：ini + env.py，url 取 settings、`target_metadata=Base.metadata`、offline/online 双模式；current/history 无报错）：**通过**（`api/alembic.ini:2` `script_location=api/alembic`；`env.py:9-10` `import src.models` 注册 + `from src.db import Base`；`:13` `set_main_option("sqlalchemy.url", settings.database_url)`；`:18` `target_metadata=Base.metadata`；`:21-42` offline（`literal_binds`）/online 双函数 + `:26/:40` `compare_type=True`；V5 current/history/heads 全绿无报错）。
- AC2（基线 `0001_baseline`：upgrade 建全 10 表 + extension 首行 + 原生 ENUM + 索引/UQ/FK；downgrade 逆向全删 + enum drop、extension 保留；revision 不依赖 src.models）：**通过**（`0001_baseline.py:15-18` 单 head、`down_revision=None`；`:23` 首行 `CREATE EXTENSION IF NOT EXISTS vector`；`:25-127` 10 表与 `models.py` 10 个 `__tablename__` 一一对应，`Vector(32)` 直引 `:11/:83`，原生 `sa.Enum(..., name='role'/'providertype')`（`:47/:60/:70`），UQ `uq_providers_tenant_name/uq_users_tenant_email/uq_wf_tenant_name` + 全部 ix 索引 + FK；`:131-155` downgrade 逆向全删 +手工 `Enum.drop(checkfirst=True)` 双类型、`:153` 注释明示 extension 保留；文件 imports 仅 sqlalchemy/pgvector/alembic（`:8-13`），零 `src.models` 引用；V8/V9 offline SQL 双向审稿 + V7 parity 等价实证）。
- AC3（启动接入：`=1` 跑 `upgrade head` + 幂等 seed 零改；`=0` 不碰库；`main.py:12` 注释同步）：**通过**（`main.py:11-33` lifespan：`:18` `if settings.auto_migrate` 守门原样；`:29-33` `api_dir` 按文件位置解析 + `Config` 覆写 url 与 `script_location` 绝对路径 + `command.upgrade(cfg,"head")` 替代旧 `create_all` + 旧 `CREATE EXTENSION` 双写已删（交 revision 承接，无漂移）；`:34-38` seed 块逐行原样（`User.count()==0` 幂等守门）；`:12-15` docstring 同步 alembic 语义 + release 指向；现网 api（新 lifespan）对 `stamp head` 库服务正常，V13/V14 实证 schema 可用；`=0` 分支代码级确认为零 DB 触碰，见 Gaps-1）。
- AC4（旧库兼容：有表无 version 库一次 `stamp head` 后 upgrade 空操作，流程文档化）：**通过**（dev 库 V10：`version_num=0001` + `users=3` 数据完好 + V5 current=head；`release.md:36` stamp→upgrade 空操作流程落字；`main.py` lifespan 对已 stamp 库即空操作 upgrade，本轮 api 重启后服务正常即活证据）。
- AC5（一致性：空库 upgrade head ≡ create_all，校验脚本落地且可重跑）：**通过**（V7 本地重跑绿：表/列类型-nullable-default/PK/FK/UQ/索引/pg_enum 全量 snapshot diff 为空；`check_migration_parity.py:1-6` docstring 自带重跑命令，`:24-27/:75-89` 管理员引擎自建双临时库 + 进程内 url 改写（注释声明不影响 lifespan/CLI 真实配置）+ `:112-116` finally 自删；V6 `alembic check` 零新操作为第二证据）。
- AC6（回滚重放：`downgrade base → upgrade head` 可重放，之后 AC5 再绿）：**通过**（前轮 destructive 重放后状态 V5 `current=0001 (head)` + V10 数据/版本完好 + V7 parity 本轮重跑仍绿；V9 offline `downgrade head:base --sql` 逐行确认逆向完整性；本轮未在有数据的 dev 库上重做 destructive 重放，见 Gaps-2）。
- AC7（发布文档：启动前 `upgrade head` 步骤）：**通过**（`release.md:29-37` DB 迁移节：`:32` 生产 upgrade 命令（`API_DATABASE_URL=<生产库>` 占位）；`:35` 仓根 + lifespan 自动 upgrade + 发布镜像须显式跑的边界说明；`:36` 旧库 stamp 口径；`:37` 回滚口径 + `downgrade base` 生产禁用；`:51-53` 二期 backlog 已无 alembic 项）。
- AC8（红线：conftest 不动；lint/type/test 全绿；契约零改动 openapi 绿；@smoke 12 绿；reset 不受影响）：**通过**（V11 conftest/models/controllers/e2e/web 零 diff；V1–V3 门禁全绿；V4 21 路由新鲜；V13 12/82 + V14 4/21 全绿；V12 reset 纯 API 删除；V12 的 `e2e:full` reset 回执全 0 且 smoke 全绿，schema 等价无回归）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据；V10 users=3 完好，V13/V14 全绿）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；V4 21 路由新鲜 + V11 契约文件零改动）。
- P2：无。
- P3：无（本次为 AC 口径核验，非全面审计，不展开轻微清理项；边际项见 Gaps，如实记录为非缺陷）。
- 结论：`No issues found`。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. AC3 空库自举（`make dev-api` 建表+seed）、二次启动幂等、`auto_migrate=0` 不碰库三项未实测：服务不重启约束下仅做代码级确认（`main.py:18` 守门 + seed 块原样）与现网佐证（已 stamp 库上 lifespan-upgrade 后 V13/V14 全绿）。旁路概率低（upgrade 对已同步库即空操作，V5/V6 实证）。
2. AC6 destructive 重放（`downgrade base → upgrade head`）本轮未重做：dev 库持有业务数据（users=3）， tester 只读边界内以前轮实操终态（V5 current=head）+ V9 offline downgrade-SQL 全行审计 + V7 parity 本轮重跑绿为联合证据。
3. AC1“空库 current/history”未单独建空库跑：空库行为由 V7（双临时空库内 upgrade head 成功）覆盖，V5 在 dev 库上 current/history 无报错。
4. 环境抖动本轮未触发：`@smoke`/`@a11y` 各跑一次即全绿，无需重跑；任务书预告的内存压力 30s 登录超时本轮零出现，故无抖动归因项。若后续重跑出现失败集合漂移的超时，仍按任务书口径先重跑确认再定级。
5. PLAN-001~010 回归为抽查口径：全量门禁（V1–V4）+ `@smoke` + `@a11y` 全绿即视为通过，未重跑 TEST-001 全部实况探针。
6. 后端集成测试按仓约束默认只在 CI 跑：本地执行 `make test`（24 passed，sqlite 口径）+ e2e 门禁，未另起 PG 常驻集成套件（parity 脚本自建自删临时库除外）。
