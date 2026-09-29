# PLAN-004 模型字段 + 密码两步走

- 关联 REQ / Linked REQ：`docs/requirements/REQ-004.md`（AC1–AC4）。
- 范围 / Scope：`api/`（PATCH 供应商、自改密码端点、单测）、`web/`（模型表单/行内编辑、用户行重置、`/account` 页、i18n 中英）、`e2e/`（换 Key/重置/自改三场景）。不碰矩阵、画布、overlay 基元。
- 架构 / Architecture：
  - PATCH 供应商：`ProviderUpdateRequest`（controller 内 Request/Response 分开命名）→ `provider_service.update_provider`（name 冲突 Conflict、base_url 走 `assert_safe_url`、api_key 空=保持）→ 409/400/404 翻译沿用 create 映射；权限 `models:write`。
  - 自改密码：`POST /auth/password`（`PasswordChangeRequest{old_password,new_password≥8}`）→ `auth_service.change_password`（验旧 hash，不对抛 400 `旧密码不正确`）；controller 仅 `current_user`，无 `require(...)`。
  - 前端字段表：两通道首批同形（名称/地址/API Key 三栏静态渲染；`extra_headers` 二期再开）。
    注（TEST-004 P3-2 订正）：初版写了 `providerFields[type]` 按类型分发表，实际落地为静态单字段
    （两类型字段相同，仅类型值不同），以本句为准；`extra_headers` 按类型分发随二期补回。
- 开发步骤 / Steps：
  - S1 模型：后端 PATCH + 单测 + openapi 双重生成 + 前端三栏/行内编辑 + e2e 换 Key 场景。验收 AC1/AC4。
  - S2A 重置：用户页行内重置 + e2e（新密码 200/旧 401 + admin 动 super_admin 403 单测已覆盖只加 e2e）。验收 AC2。
  - S2B 自改：端点 + 单测 + `/account` 页 + 侧栏入口 + e2e。验收 AC3。
  - S3 收尾：全量门禁 + `@smoke/@a11y` + TEST-004 + 本地 commit。
- 风险 / Risks：R1 Key 留空语义误读→placeholder + 注释双写；R2 自改端点被当作越权面→authn-only + 旧密码校验 + 单测锁死；R3 表单加栏破坏旧 e2e→新增栏全可选/锚点不动。
- 验证命令 / Verification：`make test TARGET_TESTS=./api/tests/test_model_providers.py` / `test_auth...`（若有则定点，否则全量）/ `make openapi-check` / `vue-tsc` / `vitest` / `pnpm -C e2e e2e -- --tags @smoke`。
