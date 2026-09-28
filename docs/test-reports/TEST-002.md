# TEST-002 PLAN-002 缺口闭环验收核验报告

- 关联 PLAN / Linked PLAN：`docs/plans/PLAN-002.md`（S1–S4，对应 `docs/requirements/REQ-002.md` AC1–AC3；收敛 TEST-001 G2/G4/G5）
- 核验时间 / Date：2026-09-28（UTC）
- 环境快照 / Env：infra（postgres/redis/nginx）已 Up；api 直跑 `:18081`（`API_AUTO_MIGRATE=1`）；web 直跑 `:5173`；sandbox 直跑 `:18091`；统一入口 `http://localhost:18080/`。未重起服务。
- 种子账号：`root@example.com` / `admin@example.com` / `member@example.com`（沿用 TEST-001 实测有效的三角色）
- 本轮改动域（`git status` 实测）：`Makefile`（openapi-check/spike 入口）、`api/scripts/`（新增 2 脚本）、`api/src/services/provider_service.py`（模块注释 +1 行）、`api/src/services/user_service.py` + `api/src/controllers/users.py`（删有资源用户 500→409）、`api/tests/conftest.py`（sqlite 外键强制）+ `api/tests/test_rbac.py`（新增 409 用例）、`docs/release.md`（命令分工）、`e2e/package.json` + `pnpm-lock.yaml`（axe pin）、`e2e/features/canvas.a11y.feature`（新增）、`e2e/src/steps/a11y.steps.ts`（新增）、`e2e/src/steps/models.steps.ts` + `workflows.steps.ts`（创建失败自清）。`e2e/src/support/nav.ts` 本轮无 diff（任务描述提及但实际未改动，不记为问题）。

## 验证命令与结果 / Verification

| # | 命令（仓根） | 结果 |
|---|---|---|
| V1 | `make openapi-check` | 通过：`OK: web/openapi.json 新鲜（20 路由）`（exit 0） |
| V2 | 篡改 `web/openapi.json`（`info.title` 改一处）后 `make openapi-check` | 变红：`FAIL: web/openapi.json 过期，先跑 make openapi 重生成` + unified diff 输出（make exit 2，非零）。恢复后重跑 `OK … 20 路由`（exit 0），`git status web/openapi.json` 无残留 |
| V3 | `make spike-opencode-go`（无凭证） | 通过：stdout `{"verdict":"downgrade","reason":"no-credentials","detail":"未提供 OPENCODE_GO_BASE_URL…维持 OpenAI-compatible 承载"}`（exit 0，无伪造验证） |
| V4 | `OPENCODE_GO_BASE_URL=http://127.0.0.1:9 make spike-opencode-go`（本地回环，不出外网） | 通过：`{"verdict":"downgrade","reason":"远端不可达，维持现状","probes":[…]}`，4 个端点（`/models` + 3 候选原生形态）均为 `ConnectError: [Errno 61] Connection refused`（exit 0） |
| V5 | `make test TARGET_TESTS=./api/tests/test_model_providers.py` | 通过：`2 passed`（既有降级单测仍过，AC1 约束满足） |
| V6 | `make lint` | 通过：`ruff check api` / `ruff check sandbox` 均为 `All checks passed!` |
| V7 | `make type-check` | 通过：`mypy api/src` → `Success: no issues found in 33 source files` |
| V8 | `make test`（全量） | 通过：`19 passed`（TEST-001 时 18 + 本轮新增 409 用例 1，无失败） |
| V9 | `pnpm --dir web exec vue-tsc --noEmit` | 通过：无输出（exit 0） |
| V10 | `pnpm --dir web exec vitest run --project unit` | 通过：`2 files / 6 tests passed` |
| V11 | `pnpm -C e2e e2e -- --tags @a11y` | 通过：`2 scenarios (2 passed)`，`10 steps (10 passed)`（登录页 + 画布页 axe 零 critical/serious） |
| V12 | `pnpm -C e2e e2e -- --tags @smoke`（回归） | 通过：`2 scenarios (2 passed)`，`14 steps (14 passed)`（与 TEST-001 V10 一致，全绿） |
| V13 | 源码阅读（只读） | `api/scripts/check_openapi.py:1-38`（重生成到内存后比对落盘，不一致即 exit 1）；`api/scripts/spike_opencode_go.py:1-87`（只读探测，`NATIVE_CANDIDATES:19` 三候选形态，无写库/改配置路径）；`provider_service.py:1-5` 模块注释同步降级结论；`docs/release.md:14-19` 说明 `openapi` 生成 / `openapi-check` 校验分工；`e2e/package.json:15` 含 `"axe-core": "4.10.2"`（已 pin） |

## 逐条验收结论 / AC Verdicts（PLAN-002 S1–S3 → REQ-002 AC1–AC3）

- S2 spike → AC1（spike 脚手架可运行、无凭证明示缺凭证、降级单测仍过）：**通过**（V3 无凭证分支 `no-credentials` + V4 不可达分支 `远端不可达`，exit 均为 0，结论均为 `downgrade` 维持现状；V5 降级单测 2 项通过；脚本 docstring `spike_opencode_go.py:1-10` 与 provider 注释 `provider_service.py:4` 互相引用一致）。
- S1 门禁 → AC2（一致时通过、改旧一处变红、文档说明分工）：**通过**（V1 绿 20 路由 → V2 篡改红 exit 2 → 恢复绿；`Makefile:27-29` 注释 + `docs/release.md:14-19` 均写明生成/校验分工）。
- S3 a11y → AC3（`@a11y` 通过、登录页+画布页零 critical/serious、依赖 pin）：**通过**（V11 2 场景 10 步全绿；`e2e/features/canvas.a11y.feature:1-20` 覆盖登录页与画布页；`e2e/src/steps/a11y.steps.ts:27-41` 只拦截 `critical`/`serious`；`e2e/package.json:15` axe-core pin `4.10.2`）。
- PLAN-001 回归抽查 → **通过**（门禁全绿 V6/V7/V8 + `@smoke` 全绿 V12，视为回归通过；未重做 TEST-001 全部 19 项实况探针，见 Gaps）。

## 发现 / Findings（P0>P1>P2>P3）

- P0：无（服务可用，未见安全泄露/数据丢失/整体不可用证据）。
- P1：无（未见越权、可见功能回退、公开契约错误、主流程中断证据；删有资源用户由 500 收敛为 409 且有单测锁定）。
- P2：无。
- P3-1（正确性收口/可维护性）：删用户兜底捕获过宽，非 FK 提交失败也会被报成 409。
  - 文件行号：`api/src/services/user_service.py:66-70`（`except Exception` 收敛为 `Conflict`）。
  - 复现/证据：只读审查 + V8 全绿；现有 `api/tests/test_rbac.py:71-102`（`test_delete_user_with_resources_returns_409_not_500`）仅覆盖 FK 残留路径，非 FK 提交异常（如连接中断）同样会走 409 分支，无反例单测。
  - 影响面：当前功能正常（409 语义正确，清理子资源后恢复 204 已断言）；异常场景下调用方可能收到误导性 409 而非 5xx，排查时需看服务端日志。
  - 修复方向：收窄为 `except IntegrityError`（SQLAlchemy），其余异常原样上抛由全局 500 处理，并以 V8 回归验证（仅建议，不承揽）。

## 验证缺口 / Gaps（非缺陷，如实记录）

1. 真实远端 opencode-go 联调仍缺：V3/V4 仅覆盖“无凭证”与“不可达”两个 downgrade 分支，原生协议可用分支（`native-candidate`）无远端可验；REQ-002 非目标已声明，维持降级结论有效。
2. a11y 仅扫登录页与画布页（REQ-002 目标原文如此），非全站 WCAG AA 审计；`moderate`/`minor` 级别违规未断言。
3. PLAN-001 回归为抽查口径：门禁全绿 + `@smoke` 全绿即视为通过，未重跑 TEST-001 V11–V19 全部实况探针（infra ps/镜像/vector 版本/沙箱出网探测等）。
4. 后端集成测试按仓约束默认只在 CI 跑：本地仍仅执行 `api/tests` 单测域（19 项）；DB 迁移幂等/并发发布竞态等长尾路径无覆盖（沿用 TEST-001 G6 约束）。
5. `e2e/src/support/nav.ts` 本轮无实际改动（`git status` 干净），与任务描述“S3 含 nav.ts”有一字之差；自清逻辑实际落在 `models.steps.ts:14-24` 与 `workflows.steps.ts:53-63`，功能层面已覆盖，不记为问题。
