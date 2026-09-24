# Cucumber Best Practices / 场景写作实践

- 场景描述用户可见行为，一步只表达一个意图；步骤按业务能力归类组织，`common/` 目录只放真正跨能力的通用步骤。
- World 中的状态使用类型化定义（如 `AppWorld`），多角色场景各自使用独立的 `BrowserContext`；需要读取 World 的步骤用 `function` 声明，不用箭头函数，以便框架绑定上下文。
- Hook 只处理共享登录初始化、生命周期管理与诊断采集；tag 本身就是约定（如 `@smoke / @prepared / @external-model`，详见 `e2e/AGENTS.md`），不混用含义，不静默跳过。
- 种子数据统一加 `E2E` 前缀；场景内新建的资源必须注册清理（类型化队列加 `registerCleanup`，按后进先出顺序，先删子资源再删主资源）。
