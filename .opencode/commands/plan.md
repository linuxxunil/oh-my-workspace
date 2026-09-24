---
description: 澄清需求并落盘 REQ 与 PLAN
agent: plan
subtask: true
---

接受模糊需求或已有 REQ（`$ARGUMENTS`）：先追问补齐目标、范围与验收口径并写入 `docs/requirements/REQ-xxx.md`，再输出架构、编号 Todo 步骤、验收标准与验证命令并写入 `docs/plans/PLAN-xxx.md`。验收口径缺失时停下追问（至少覆盖目标用户、范围边界、验收标准，不设轮次上限，不编造），追问不清不进 PLAN。全程只做规划落盘，不写业务实现，结束时返回两个文件路径。
