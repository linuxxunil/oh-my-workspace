# Playwright Best Practices / 定位与断言实践

## 要点

1. 场景隔离：各场景互不依赖执行顺序，状态放在场景私有的 context 中，不使用模块级全局变量；登录态与会话通过显式 fixture 注入。
2. 定位器面向用户契约：可交互控件用 role 加名称；表单优先用 label 关联（仅当 label 缺失且占位文本长期稳定时才用占位符）；非交互内容用可见文本；没有语义边界才用 testid。不为通过定位而加虚假 role；出现 `.first() / .nth()` 时视为评审关注点。
3. 断言用 Web-first 风格：`toHaveURL / toBeVisible / toBeHidden / toBeEnabled / toHaveText`；不写 `expect(await isVisible()).toBe(true)`、不手写轮询、不拿 `waitForTimeout` 做同步；非 DOM 真值改用 `expect.poll`。Cucumber 步骤、hook、定位操作、断言三方的超时配置各自独立。
4. 动作自带可操作性等待，不叠加多余的前置等待；不用 `force:true` 绕过遮挡或禁用态造成真实失败；一次性的弹窗、下载、请求监听先建等待再触发动作；不用 `networkidle` 充当就绪断言。
5. 诊断能力挂在 Cucumber hooks 上统一处理（截图与 trace），不逐场景重复装配；trace 通过 `browserContext.tracing` 开关。
