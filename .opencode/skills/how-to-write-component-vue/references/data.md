# Data And Queries (Vue) / 数据与查询

数据形状以生成契约为准，组件只消费不重定义。

- 生成契约为权威：后端结构定义拥有数据形状，前端按 `{ params, query?, body? }` 调用；形状错误先修后端再重新生成。不手写数据传输对象镜像，不放宽字段或枚举，不改生成产物。
- 生成器 pin 死：`orval@^7` 产出 `@tanstack/vue-query@^5` 钩子（`vue-router@^4 + pinia@^2` 配套）；不用 hand-rolled client，不用实验性默认配置 API。
- 查询（Vue）：`@tanstack/vue-query` 的 `useQuery` 直接消费生成器的 `queryOptions(...)`，响应式入参包 `computed`；缺必填入参整个分支 `skipToken`，独立执行条件才加 `enabled`；不用占位载荷，不把标识转为空串。
- 变更（Vue）：直接使用生成的 `mutationOptions()`；优先 `mutate`；共享失效、重试、缓存放查询工具默认配置，局部回调只做提示、关闭、导航。
- 预取从触发器或菜单打开事件发起，不挂隐藏订阅者暖缓存；`staleTime: 0` 视为已过期，有限数值接受时间窗口，无限期只到失效为止。
- 切换工作区即租户边界：丢弃旧租户状态或按工作区隔离查询键；鉴权、配额、租户相关的请求判断放在路由守卫或运行时边界，不用启动默认值做产品决策。
