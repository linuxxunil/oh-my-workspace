# 03 Conventions / 通用约定

- 双语：标题用英文，正文用中文，关键术语保留英文（便于模型检索）。
- 后端分层：controller 保持薄、service 做编排、core 沉淀领域、`libs/` 不放业务。
- 租户：表结构带 `tenant_id`，读写带谓词约束，切换 workspace 即跨越数据边界（细节见 skill references）。
- 前端：生成客户端为权威来源，不手写 DTO；URL 身份归 vue-router；live 状态不进 localStorage（Vue 侧细节见 skills）。
- 提交信息：`<type>(<scope>): <subject>`，`type=feat/fix/docs/refactor/test/chore`。
