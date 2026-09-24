# Rule Catalog — Architecture / 架构分层规则

## Scope / 适用范围

controller / service / 核心领域 / libs / model 之间的职责划分与依赖方向。

## Rules / 规则

### Keep business logic out of controllers / 控制器保持轻薄

- Category: maintainability
- 控制器只做三件事：解析输入、调用 service、返回序列化结果。条件分支与状态流转下沉到 service 或核心领域层。
- Bad: 控制器内读取 `role` 后直接改 `status` 并写库。Good: 控制器先用 `PublishRequest.model_validate(...)` 校验，再调用 `app_service.publish_app(...)`。

### Preserve layer dependency direction / 依赖单向流动

- 允许方向为 controllers → services → core / domain；核心层不得反向引入控制器或 web 层。
- Bad: 核心策略模块引入控制器层的请求上下文。Good: 策略函数只接收 `role: str` 这类纯参数，由 service 层完成适配。

### Keep libs business-agnostic / 通用库不写业务

- `api/libs/` 只放与领域无关的通用 helper，不表达业务规则，不做流程编排，不引入 service、controller 或领域模块。
- Bad: 通用过滤 helper 直接调用 `ConversationService.has_paid_plan`。Good: 通用库只保留 `older_than_days()` 这类纯函数，阈值判断交回 service。
