# Data Query Contracts (Vue) / 数据查询契约

评审数据形状、查询条件、变更路径是否遵守生成契约与租户边界。

- 生成契约为权威：后端结构定义拥有数据形状，前端用生成工具产出 `{ params, query?, body? }` 调用；形状错误先修后端再重新生成。不手写数据传输对象镜像，不放宽字段或枚举，不改生成产物，不另起平行状态层。
- 生成器 pin 死：`orval@^7` 产出 `@tanstack/vue-query@^5` 钩子；`vue-router@^4 + pinia@^2` 配套；不用手写客户端与实验性默认 API。
- 查询（Vue）：`@tanstack/vue-query` 的 `useQuery` 直接消费生成器的 `queryOptions(...)`，响应式入参包 `computed`；缺必填入参整个分支 `skipToken`，独立执行条件才加 `enabled`；不把 `skipToken` 塞进占位载荷，不把标识强制转为空串。
- 变更（Vue）：直接使用生成的 `mutationOptions()`；优先 `mutate`，需组合 Promise 且处理异常才用 `mutateAsync`；共享失效、重试、缓存放查询工具默认配置，局部回调只做提示、关闭、导航并保留共享行为；无归属约定的乐观更新不做。
- 空值：`null`、`undefined`、`''` 保留到最终边界；不用 `value || undefined` 洗掉有意的清空操作。
- 租户：切换工作区即租户边界，丢弃旧租户状态；查询键须携带工作区身份，除非整页重载已经隔离；`workspace_id` 与 `tenant_id` 不混用，使用前先查后端契约。
- 地址：可分享的筛选、标签页、分页、搜索放在 `vue-router query`；一次性导航信号与瞬态界面状态不进入持久订阅。
