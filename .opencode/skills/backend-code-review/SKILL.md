---
name: backend-code-review
description: 用户显式要求 review/audit api/后端代码时用。支持 pending-change、文件级、粘贴 diff 三种。不用于纯实现、无 review 意图的诊断、前端代码、api/ 之外后端。
---

# Backend Code Review / 后端评审

只报告可复现的缺陷。包内的事实与命令以最近的 `AGENTS.md` 为准；本 skill 负责评审流程，并按需指向规则文件。

## Evidence First / 先取证后判断

1. 先确定范围，阅读差异或目标文件全文。
2. 再读改动行、行为归属方、邻近测试、注释与文档字符串中的约定。
3. 仅当判断正确性确有需要时，才继续追踪调用方、持久化逻辑、鉴权路径、生成式 schema 与外部 IO。
4. 只报告可观察到的失败、明确违反的约定、安全边界问题、数据完整性风险、已有证据的维护隐患。

## Rule Routing / 按需加载规则

- 模型与迁移相关：`references/db-schema-rule.md`
- controller / service / core / libs 分层与依赖方向：`references/architecture-rule.md`
- 绕过仓储抽象直接访问数据表：`references/repositories-rule.md`
- 会话、查询、事务、并发、原生 SQL：`references/sqlalchemy-rule.md`

没有命中的规则文件时，直接评审正确性、安全性、行为变更与测试证据；本地约定无法澄清时再查官方文档。

## Severity And Output / 分级与输出

- **P0**：安全或隐私泄露、数据丢失、整站不可用。
- **P1**：用户可见回退、鉴权或租户隔离失效、公开约定错误、主流程中断。
- **P2**：大概率引发故障的正确性、性能、可维护性或测试问题。
- **P3**：轻微清理，仅全面审计时报告。

按级别从高到低排序，每条给出文件行号、违反的约定或复现路径、影响、修复建议。无问题则写 `No issues found` 并说明验证盲区。措辞克制，不做无证据推断，不主动承揽实现。
