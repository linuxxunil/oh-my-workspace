# API Agent Guide / 后端指南

动手改后端代码之前，先通读周边模块、类、函数自带的 docstring 与关键注释，把它们当作本地契约（local contracts）来遵守；只有行为真正变化时才同步更新这些注释。

## Commands / 命令

以下命令都在仓根执行：

- 格式与 lint：`make lint`
- 类型检查：`make type-check`
- 单元测试：`make test`
- 定点测试：`make test TARGET_TESTS=./api/tests/<path>`

凡是直接运行 Python，一律用 `uv run --project api`。需要 Docker 的集成测试交给 CI，日常开发不启动常驻服务。

## Architecture And Boundaries / 架构与边界

- Controller 只负责解析请求与序列化返回，Service 负责编排，领域决策收敛到 `core/`。`libs/` 保持与业务无关，新增抽象前先复用已有 owner。
- 动 controller 的 schema、生成式 API 契约、`SystemFeatureModel` 之前，先读 `api/controllers/API_SCHEMA_GUIDE.md`。`/system-features` 是最小未鉴权启动白名单，不当通用配置中心用。
- 租户数据读写沿完整 owner 链携带 `tenant_id` 约束，穿过 payload 或异步边界后，以 DB 重建的可信引用为准。
- 写事务保持显式有界，事务内部不发起外部 IO，除非另有书面一致性约定。
- 配置、对象存储、出站 HTTP 各走仓内既定 owner：统一 config 入口、统一 storage 入口、出站统一走 SSRF-safe 通道。
- 请求与响应模型统一用 Pydantic v2；复用领域异常，在 controller 边界做翻译。
- 异步任务沿用既有 Celery task 与 queue 的 owner 划分；可重试任务的副作用必须幂等，并在日志中带上资源 ID。

## Typing / 类型

- `T | None` 按严格联合类型处理，每个分支讲清语义。
- 默认参数视同引入重载，每个默认值都要有真实用途，不得掩盖不安全状态。
