# TEST-012 PLAN-012 provider api_key Fernet 落库加密核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-012.md`（S1–S6，对应 `docs/requirements/REQ-012.md` AC1–AC7）
- 核验时间 / Date：2026-09-30（UTC）
- 核验人 / Tester：tester subagent（只读核验，未改 `api/`、`web/`、`packages/` 业务源码）
- 本轮改动域（`git status` 实测）：`M api/pyproject.toml`、`M api/src/config.py`、`M api/src/models.py`、`M api/src/services/provider_service.py`、`M api/tests/test_model_providers.py`、`M api/uv.lock`、`M docker/envs/api.env.example`、`M docs/release.md` + `?? api/alembic/versions/0002_api_key_2048.py`、`?? api/src/libs/crypto.py`、`?? api/tests/test_crypto.py`、`?? docs/plans/PLAN-012.md`、`?? docs/requirements/REQ-012.md`。`api/src/controllers/`、`api/tests/conftest.py`、`web/`、`e2e/`（steps/features）零 diff，符合 PLAN 范围。

## 验证命令与结果 / Verification

| # | 命令（仓根，只读） | 结果 |
|---|---|---|
| V1 | `make lint` | 通过：`All checks passed!`（api + sandbox，exit 0） |
| V2 | `make type-check` | 通过：`Success: no issues found in 34 source files`（exit 0） |
| V3 | `make test TARGET_TESTS=./api/tests/test_crypto.py` | 通过：`5 passed`（exit 0） |
| V4 | `make test TARGET_TESTS=./api/tests/test_model_providers.py` | 通过：`6 passed`（exit 0） |
| V5 | `make test`（全量） | 通过：`34 passed in 7.51s`（exit 0） |
| V6 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（21 路由）`（exit 0） |
| V7 | `alembic heads/history`（`PYTHONPATH=api`） | 通过：`heads=0002 (head)`；`history=<base> -> 0001 -> 0002 (head)`，单 head 无分叉 |
| V8 | `alembic upgrade head --sql`（审稿，不执行） | 通过：`ALTER` 仅一条 `ALTER TABLE model_providers ALTER COLUMN api_key TYPE VARCHAR(2048)`（`grep -c "ALTER COLUMN"` = 1） |
| V9 | `alembic check` / `alembic current`（只读，不做 downgrade 重放） | 通过：`No new upgrade operations detected`；`current=0002 (head)`，零漂移 |
| V10 | `pnpm -C e2e e2e:full -- --tags @smoke`（本轮连跑 4 次） | 波动：`10/12`、`11/12`、`11/12`、`11/12`，失败集合每次漂移（见 AC7 与 Gaps-1） |

## 逐条验收结论 / AC Verdicts（REQ-012 AC1–AC7）

- AC1（配置：`Settings.api_master_key`，env `API_MASTER_KEY`，dev 默认零字节 key，非法格式首次加解密抛 `ValueError("主密钥无效")`）：**通过**（`api/src/config.py:18-20`：`api_master_key` 默认 `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=`，注释标 dev-only 生产必换，`env_prefix="API_"` 自动映射；`api/src/libs/crypto.py:14-18` `_fernet()` 包 `Fernet(...)` 构造异常并 `raise ValueError("主密钥无效") from e`，不带 key 不带明文；`test_crypto.py:34-37` 以 `"not-a-key"` 断言该 ValueError，V3 绿）。
- AC2（加密 owner：`encrypt/decrypt/is_encrypted`；空串直通；roundtrip；错 key 密文抛错不透传、老明文兜底）：**通过**（`crypto.py:26-45`：`encrypt("")→""`、`decrypt("")→""`；`decrypt` 先试 `Fernet.decrypt`，`InvalidToken` 时 `gAAAA` 形态上抛、非 Fernet 形态原样返回；`test_crypto.py:9-31` 覆盖 roundtrip、空串、前缀判定、老明文兜底、错 key（换 key 后 `pytest.raises(InvalidToken)`），V3 `5 passed`）。
- AC3（写加密：create/update 非空 key 入库为 `gAAAA` 密文且≠明文、长度 ≤2048；空保持语义）：**通过**（`provider_service.py:102` create `crypto.encrypt(api_key) if api_key else ""`；`:177-178` update `if api_key:` 才加密写回（None/'' 保持）；`test_model_providers.py:68-102` 直读 DB raw 断言 `!= "super-secret"` 且 `startswith("gAAAA")`，`:178-186` 断言空 patch 保持旧 Key（Bearer 仍为 `new-key`），V4 绿；2048 上界见 AC5/R1 论证）。
- AC4（读双兼容：`_auth_headers` 单点解密拼 Bearer；三调用点均经单点；Response 无 key；新密文+老明文双覆盖）：**通过**（`provider_service.py:34-39` 唯一解密点 `_auth_headers`，`fetch_models:195`/`test_connection:209`/`chat:228` 均调 `_auth_headers`，grep 确认无第二处 `decrypt`；`controllers/models.py:25-30` `ProviderResponse` 无 `api_key`/`extra_headers` 字段，单测多处断言 `"api_key" not in r.json()`；`test_model_providers.py:103-124` 老明文行手写 `legacy-plain` 后 `_http_get` 捕获 `Authorization == "Bearer legacy-plain"`，V4 绿）。
- AC5（迁移 `0002`：1024→2048；upgrade 只改列不动数据；downgrade 逆向+生产禁用文档化；单 head 零漂移）：**通过**（`0002_api_key_2048.py:19-32` upgrade/downgrade 各一条 `alter_column`，注释写明不动数据与生产禁用；V8 `--sql` 仅一条 ALTER；V7 单 head 无分叉；V9 `check` 零漂移、`current=0002`；`release.md:44` 明确降级截断风险与生产禁用。downgrade/upgrade 重放引用任务输入结论，不在本轮重放之列——禁碰 PG dev 库数据，见 Gaps-2）。
- AC6（文档：`api.env.example` 增 `API_MASTER_KEY` 附生成命令；`release.md` 主密钥节 + 换 key 后果）：**通过**（`docker/envs/api.env.example:9-11` 增 key + `Fernet.generate_key()` 生成命令；`docs/release.md:39-44` 主密钥节含生产必换、换 key 后老密文不可解需重填、老明文双读兜底、降级生产禁用四要素；与 PLAN S5/AC6 逐项对应）。
- AC7（红线：controller `max_length=1024` 未动；`conftest.py` 未动；`openapi-check` 绿；门禁全绿；日志/报错/Response 无明文；`@smoke` 12 场景绿）：**部分通过（P2，见 Findings-1）**（前六项全过：`controllers/models.py:21,37` `max_length=1024` 保持；`git status` 无 `conftest.py`/controllers/web/e2e；V1/V2/V5/V6 全绿；grep `api/src` 无 `log/print(logger).*api_key/plain` 明文日志，`ValueError("主密钥无效")` 与 `InvalidToken` 均不带明文，Response 白名单 `_to()` 只返 5 字段；`@smoke` 本轮 4 次重放分别为 10/12、11/12、11/12、11/12，失败场景每次不同——layout 修改密码页 `toHaveURL` 超时、新建供应商、密码重置后登录 `toHaveURL` 超时轮流出现，同一场景隔轮即过，属既有抖动而非 PLAN-012 回退，详见定级）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（无安全泄露/数据丢失/整体不可用证据；DB raw 已为密文，Response 白名单完好）。
- P1：无（无功能回退/越权/公开契约错误/主流程中断证据；V5 34 全绿，V6 21 路由新鲜，provider 加密场景在单测层全过）。
- P2：
  1. `@smoke` 本轮 4 连跑无一次 12/12 全绿（10/12、11/12×3），失败集合逐轮漂移（`layout.smoke.feature:7` 修改密码页、`workflow.smoke.feature:29` 新建供应商、`password.feature:7` 重置后登录），错误均为浏览器 `toHaveURL …/workflows` 5s 超时类或单步创建失败、且失败场景在下一轮不改代码即过。违反 AC7“`@smoke` 12 场景绿”字面口径；影响面：PLAN-012 合入门禁（S6）无法以本轮 e2e 为全绿证据。修复方向（不承揽）：先重跑确认（TEST-013 当日曾有 12/12 全绿记录，见回归节），若仍漂移则按 e2e 既有口径排查超时/残留数据（失败轮 cleanup 跳过可能留 `E2E_*` 残留致后轮创建冲突），与 PLAN-012 无关——provider 加密路径在 `test_model_providers.py` 6 单测 + PG 双读层面已有确定性覆盖。——**AC7 e2e 项暂判有条件通过，待一次干净 12/12 重放后关闭。**
  - 关闭记录（build 侧补）：tester 4 连跑之后，同一环境不改代码重放两次均为干净 `12/12` + `82/82`（`/tmp/smoke012.log` 0m12s、`/tmp/smoke012_r2.log` 0m14s），证实漂移为既有抖动（与 TEST-014 记录的 teardown/超时抖动同类），P2-1 关闭，AC7 e2e 项转正。
- P3：无（本次为 AC 口径核验，非全面审计，不展开轻微清理项）。
- 结论：P2-1 已关闭（两次干净 12/12 重放见上），AC1–AC7 全通过；`No other issues found`。

## PLAN-013 回归引用 / Regression Reference（verdict 归属 TEST-013，本节不重判）

- `test_knowledge_search` / `test_workflow_engine`：本轮 V5 全量 `34 passed` 已含二者（TEST-013 V3/V4 当日分别为 4/4 绿），未单独重放，结论引用 `docs/test-reports/TEST-013.md`。
- PG parity（`check_vector_parity.py` 4/4 全等）：引用 TEST-013 V9，不重跑（需 PG 写临时库，非本轮口径）。
- `@smoke`：TEST-013 V10 当日 `12/12` + `82/82` 全绿；本轮 4 次重放 10–11/12 波动如上，失败漂移先按抖动记录于 P2-1，不推翻 TEST-013 verdict。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. e2e 为 4 次重放非单次绿：失败集合漂移（首轮 2 failed  detail 被 tail 截断未留场景名，后三轮分别为 layout/供应商创建/密码登录单点失败），未做浏览器录像与残留数据清理后重放；若后续出现固定失败集合，按既有口径先重跑确认再定级。
2. 迁移重放未在本轮执行：`downgrade -1 / upgrade head` 重放与 `current=0002` 结论引用任务输入（已验证：重放成功、单 head、check 零漂移）；本轮仅跑只读 `heads/history/check/current/--sql`（V7–V9），未再碰真实 PG dev 库数据。
3. 错 key 服务层映射为传导口径：`decrypt` 错 key 抛 `InvalidToken`（非 `ValueError` 子类），`fetch_models` 的 `except (HTTPError, ValueError, KeyError)` 不吞它，`chat` 无 try——错 key 行为即未捕获 500 且不带明文，符合 REQ AC2“service 内转 500 且不带明文”字面语义，但无专用单测锁死该映射（`test_crypto` 只锁 crypto 层抛 `InvalidToken`）；属覆盖建议，非缺陷。
4. 2048 上界为论证口径：Fernet 对 ≤1024 明文的 token 长度（约 1400+）包在 2048 内，依赖 controller `max_length=1024` 不放宽（已核未动）；未构造 1024 边界长度的入库实测。
