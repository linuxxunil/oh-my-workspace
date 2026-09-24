# Rule Catalog — Repositories / 仓储抽象规则

## Rules / 规则

### Reuse existing repository / 优先使用现有仓储

- 动手前先检索 `api/repositories`、`api/core/repositories`、`api/extensions/*/repositories/`；已有抽象必须经过它访问数据，缺方法则补充方法，不另起手写查询。
- Bad: 在 service 内直接 `session.execute(select(App)...)`。Good: 调用 `self.app_repo.get_by_id(...)` 读取、`save()` 落盘。

### Introduce only when justified / 新建仓储需充分理由

- 尚无抽象时，仅在以下情形之一成立才新建：超大表的访问收敛、复杂查询在多处复用、需要支撑多种存储策略；且保持依赖方向为 service / core 依赖抽象、基础设施层提供实现。
- 例：`Conversation.list_recent_for_app` 的过滤、关联与分页在多处复制时，抽出 `ConversationRepository(Protocol)` 接口与 `SqlAlchemyConversationRepository` 实现。
