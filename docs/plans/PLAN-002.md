# PLAN-002 TEST-001 缺口闭环

- 关联 REQ / Linked REQ：`docs/requirements/REQ-002.md`（AC1–AC3）。
- 范围 / Scope：`Makefile`（openapi-check/spike 入口）、`api/`（spike 脚本 + 降级决策注释）、`e2e/`（@a11y 场景）、`docs/`（命令分工说明）。不碰业务语义、不改 RBAC/计费/隔离。
- 架构 / Architecture：
  - S1 门禁：`make openapi-check` = 重生成到临时文件后 `diff` 落盘 `web/openapi.json`，不一致即非零退出。
  - S2 spike：`api/scripts/spike_opencode_go.py`（`uv run --project api` 运行）依次探测候选原生端点形态（文档/版本/模型列表），全部不可达或无凭证时输出 `downgrade: keep OpenAI-compatible` 结论 + 原因；结论同步为 `provider_service.py` 模块注释。
  - S3 a11y：`e2e/features/canvas.a11y.feature`（`@a11y`）+ axe 注入式扫描（登录页、画布页），critical/serious 为零；违规先修产品 markup（缺语义先修产品再补测试）。
- 开发步骤 / Steps：
  - S1 openapi 门禁：加 `Makefile:openapi-check` + `docs/release.md`（或 dev-spec）一笔分工；验收 AC2；验证 `make openapi-check`（绿）+ 人为改旧一处（红）+ 恢复（绿）。
  - S2 spike：加脚本 + 运行 + 结论落盘；验收 AC1；验证 `make spike-opencode-go`（或直跑命令）输出结论 + `make test TARGET_TESTS=./api/tests/test_model_providers.py` 仍过。
  - S3 a11y：加依赖（pin）+ feature/steps + 运行修绿；验收 AC3；验证 `pnpm -C e2e e2e -- --tags @a11y` + 回归 ` --tags @smoke`。
  - S4 收尾：全量门禁 + `@tester` 出 `TEST-002` + 修 P0/P1 + 本地 commit（一 PLAN 一 commit，不 push）。
- 风险 / Risks：R1 无远端凭证→spike 只给“不可判定/维持降级”结论，不伪造（REQ-002 非目标已声明）；R2 axe 误报→只修 critical/serious 且以产品语义为准；R3 画布时序抖动→复用 S7 的选中重试/显式断言模式。
- 验证命令 / Verification：`make openapi-check` / `make spike-opencode-go`（待 S2 定名）/ `pnpm -C e2e e2e -- --tags @a11y` / 全量 `make lint/type-check/test + web-check/web-test` / `@smoke` 回归。
