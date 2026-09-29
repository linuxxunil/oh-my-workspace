# PLAN-006 供应商删除补齐 + 绑定拒绝

- 关联 REQ / Linked REQ：`docs/requirements/REQ-006.md`（AC1–AC4）。
- 范围 / Scope：`api/`（delete 引用检查 + 409 映射 + 单测）、`web/`（删除键 + confirm + alert + i18n）、`e2e/`（两新场景 + 引用流程准备 helper）。不碰矩阵、画布、基元。
- 架构 / Architecture：
  - 检查：`provider_service.delete_provider` 内扫 `Workflow(tenant)` → 各取 `latest_version` → `Dag.model_validate(ver.dag)` 找 `type=='llm'` 且 `config.provider_id==id` → 有则 `Conflict("已被以下流程引用：n1、n2")`；controller delete 补 `Conflict→409`。
  - 前端：行内删除键（`models.delete`）→ `confirm(t('models.confirmDelete', {name}))` → `deleteMut` → 失败 `detail` 进 `rowError[id]` alert；成功清 state。
  - e2e：`createWorkflowWithLlm(name, providerId)`（support/api，经生成式客户端）供“被引用拒绝”场景准备。
- 开发步骤 / Steps：
  - S1 后端检查 + 单测（409/204/403）。验收 AC1。
  - S2 前端删除 + confirm + alert + i18n。验收 AC2。
  - S3 e2e 两场景。验收 AC3。
  - S4 收尾：全量门禁 + TEST-006 + 本地 commit。
- 风险 / Risks：R1 DAG 解析异常版本→跳过脏版本（只认合法 llm 节点，不炸删除）；R2 原生 confirm 被浏览器拦截→e2e  transcripts 显示其行为（Playwright 默认 accept，无需监听）；R3 409 文案含流程名泄露→同租户内可见，无跨租户。
- 验证命令 / Verification：`make test TARGET_TESTS=./api/tests/test_model_providers.py` / `vue-tsc` / `pnpm -C e2e e2e -- --tags @smoke`。
