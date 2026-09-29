# PLAN-007 extra_headers 端到端暴露

- 关联 REQ / Linked REQ：`docs/requirements/REQ-007.md`（AC1–AC4）。
- 范围 / Scope：`api/`（校验 helper + create/update 接入 + 单测）、`web/`（KV 编辑器 ×2 表单 + i18n）、`e2e/`（一新场景 + 填头步骤）。不碰 Response schema、画布、基元库、缓存。
- 架构 / Architecture：
  - 校验：`provider_service._check_extra_headers(headers)`（键非空、`^[A-Za-z0-9-]+$`、禁 `authorization` 大小写不敏感、值 ≤1024、≤20 条），非法 `ValueError` → controller 现有 `→400` 通道；create 先验后存，update 仅 `is not None` 时验并替换。
  - 前端：ModelsView 内联 KV 行编辑器（新建 `headers` + 编辑 `editHeaders`，`{k,v}[]`；空行忽略；提交时空数组→字段省略（编辑=保持，新建=不带），非空→`Object.fromEntries`）；hint 明示替换语义。
  - e2e：`provider.feature` 加场景“建供应商填自定义头→保存→连通性 ok”；headers 经生成式客户端 create（API 准备层），浏览器只断言列表与检查结果。
- 开发步骤 / Steps：
  - S1 后端校验 + 单测（400×4 种 + 透传断言 + 替换语义）。验收 AC1。
  - S2 前端 KV ×2 表单 + i18n。验收 AC2。
  - S3 e2e 新场景。验收 AC3。
  - S4 收尾：全量门禁 + TEST-007 + 本地 commit。
- 风险 / Risks：R1 替换语义误删旧头→hint 写清 + 留空=保持；R2 键规则误伤定制鉴权头（如 `X-API-Key`）→仅禁 authorization，其余放行；R3 Response 零变更→`openapi-check` 应绿，红了即动错地方。
- 验证命令 / Verification：`make test TARGET_TESTS=./api/tests/test_model_providers.py` / `vue-tsc` / `pnpm -C e2e e2e -- --tags @smoke`。
