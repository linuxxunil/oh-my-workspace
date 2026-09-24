---
description: 按 PLAN 验收标准测试并分级报告
agent: tester
subtask: true
---

按 `docs/plans/$ARGUMENTS` 中的验收标准逐条验证，并产出 `docs/test-reports/TEST-xxx.md`（含 P0-P3 定级）。只输出测试结论，不修改业务源码。P0/P1 清零且用户确认才可交付进版（仅本地 commit）；P2/P3 由用户豁免。
