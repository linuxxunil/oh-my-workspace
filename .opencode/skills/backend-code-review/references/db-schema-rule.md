# Rule Catalog — DB Schema / 表结构规则

## Rules / 规则

### Keep properties pure / 计算属性不查库

- 模型上的计算属性不得开启新会话查询其他表，容易引入 N+1 与跨模型耦合。
- Bad: 在 `Conversation.app_name` 内新建 Session 再查应用表。Good: 属性只读已加载字段（如 `name or "Untitled"`），关联数据由 service 或仓储层批量装配。

### Require tenant column / 租户字段必备

- 租户业务表必须携带 `tenant_id`，联合唯一键与索引都要体现租户维度；纯全局元数据表例外，但需在注释中写明理由。
- Bad: 数据集表只有 `id/name`。Good: 补充 `tenant_id: Mapped[str] = mapped_column(StringUUID, index=True)`。

### Deduplicate indexes / 索引按前缀去重

- 按最左前缀原则检查冗余：已有 `(a,b,c)` 即覆盖 `(a,b)`，不再重复建。
- Bad: 同时创建 `(tenant_id,app_id)` 与 `(tenant_id,app_id,created_at)`。Good: 只保留宽索引，除非压测数据证明确有必要。

### Keep column types portable / 字段类型可移植

- 模型层不直接使用特定数据库专有类型（如 `JSONB`），统一收敛到 `models.types`（`AdjustedJSON / LongText / BinaryData`）；迁移脚本按 `conn.dialect.name` 做分支。
