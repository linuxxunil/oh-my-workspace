---
name: e2e-cucumber-playwright
description: 在 e2e/ 下写 / 改 / 评审 Cucumber + Playwright 测试（feature、steps、support、tags、locators、断言）时用。不用于 Vitest / VTU、后端测试、套件外自动化。
---

# E2E Cucumber And Playwright / 端到端测试写法

`e2e/AGENTS.md` 负责套件架构、生命周期、命令、标签约定、生成式客户端边界、fixture 与清理约定；某 feature 目录下的 `AGENTS.md` 若存在则优先。本 skill 只负责测试写法与评审方法。

Cucumber 负责场景组织、hook 执行与报告；Playwright 只负责浏览器自动化（context / page / locator / action / assertion / request / tracing）。超时配置按各自归属分离；`@playwright/test` 自带的 runner 配置不适用于本套件。

## Topic Routing / 按需加载

- 定位器、断言、隔离、等待策略：`references/playwright-best-practices.md`
- 场景措辞、步骤粒度、World、hook、tag：`references/cucumber-best-practices.md`

本地约定无法确定框架用法时，再查 Playwright 与 Cucumber 官方文档。

## Workflow / 工作流程

1. 只为跨边界的关键用户旅程补充端到端覆盖，归属方单测已能证明的不重复补。
2. 从真实产品默认值与扮演角色出发组织场景；允许准备必要的前置数据，不为迁就断言而反向篡改状态。
3. 措辞与行为一致的旧步骤优先复用；确无可用步骤时再新增一个语义完整的场景或步骤。
4. 浏览器侧的动作与断言放在用户边界层；数据准备、种子写入、轮询等待、资源清理放在归属明确的包内。
5. 改动后运行 `e2e/AGENTS.md` 规定的最小 tag 场景与包检查；只有共享 hook、tag、support 变更时才扩大验证面。

评审只报告可复现的正确性失败、不稳定来源、架构漂移，并写清已验证行为与外部依赖、浏览器、环境方面的验证缺口。
