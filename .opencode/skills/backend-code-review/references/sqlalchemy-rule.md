# Rule Catalog — SQLAlchemy / 会话与并发规则

## Rules / 规则

### Bound every transaction / 事务显式有界

- 写操作必须二选一：显式 `session.commit()` 提交，或用 `with session.begin():` 包裹以自动提交回滚；事务窗口保持短小，不在事务内做网络调用或重计算。
- Bad: 遗漏提交，或在事务内调用外部接口。Good: 先完成外部调用或把重计算移出，再开短事务写库。

### Scope by tenant / 读写携带租户谓词

- 共享表的读写条件必须包含 `tenant_id`，service 与仓储接口逐层透传租户标识。
- Bad: `select(Workflow).where(id==...)`。Good: 追加 `Workflow.tenant_id == tenant_id`。

### Prefer ORM expressions / 查询优先用 ORM 表达

- 能用 `select / update / delete` 表达式写清的查询，不写原生 SQL 字符串；仅在 ORM 表达能力确实不足时例外。
- Bad: `text("SELECT * FROM workflows...")`。Good: `select(Workflow).where(...)`。

### Guard concurrent writes / 写并发三选一

- 低竞争场景用乐观锁：`version` 字段做守卫，发现 `rowcount == 0` 即判为冲突重试或报错。
- 跨进程多步临界区用 Redis 分布式锁。
- 高竞争的同行序列化用 `SELECT ... FOR UPDATE`，并保持短事务。
- 以上方案一律携带 `tenant_id` 条件，并校验受影响行数。
