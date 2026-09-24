# E2E Guide / 端到端指南

## Runtime And Commands / 运行与命令

- `scripts/run-cucumber.ts` 是唯一的运行时编排；`support/world.ts` 提供的 world 对象加每个场景独立的 `BrowserContext` 实现隔离；浏览器身份与 API 身份分开管理。
- 以下命令都在仓根执行：`pnpm -C e2e e2e`（环境已初始化时）、`pnpm -C e2e e2e:full`（重置加确定性全量）、`pnpm -C e2e e2e -- --tags @smoke`（子集）。同一时刻只跑一个本地 runner。
- Tags 含义：`@authenticated` 只表达意图，`@unauthenticated` 启用干净 context；`@axe/@wcag-a/@wcag-aa` 跑独立无障碍扫描；`@external-model/@external-tool` 默认排除；`@skip` 只做临时排除。
- 被测动作走浏览器完成，API 仅承担准备、轮询、清理；普通 JSON 调用走生成式 oRPC 客户端，不手写 URL，不镜像 DTO，不跨场景复用可变 client，不经过 TanStack 缓存。
- 资源命名统一经 `support/naming.ts` 加 `E2E` 前缀；上传物放在 `fixtures/test-materials/`；场景内自建资源逐个登记 cleanup（LIFO），先删子资源再删主资源。
- Cucumber exit status 即行为门禁；空 tag 选中集不得放行。
