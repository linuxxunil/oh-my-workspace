---
name: frontend-code-review-vue
description: 用户显式要求review/audit web/或packages/ui/的Vue代码时用。不用于纯实现、无review意图的诊断、纯后端代码。
---

# Frontend Code Review (Vue) / 前端评审

只报告能观察到的失败、契约违反、安全边界问题、已被证实的风险。团队书面约定视为契约：先明确范围与例外，不虚构用户影响。

## Evidence First / 先定证据

1. 确定范围（文件 / 差异）。
2. 阅读改动行、行为归属方、最近的 scoped `AGENTS.md`。
3. 只有当判断正确性确实需要时，才继续追查公共消费者、生成契约、基元接口、运行时配置。

## Rule Routing / 按需路由

按命中主题只读对应文件，不全量加载：

- 语义 / 焦点 / 键盘 / 表单 / 禁用态：`references/accessibility-ui.md`
- 界面基元 / 浮层 / 视觉记号：`references/ui-primitives.md`
- 组件归属 / 属性 / 状态 / 组合函数 / 路由 / 模块边界：`references/component-architecture.md`
- 生成客户端 / 查询 / 变更 / 鉴权 / 地址 / 持久化：`references/data-query-contracts.md`
- 测试缺口：`references/testing.md`
- 包体积 / 瀑布请求 / 渲染 / 订阅开销（须有证据）：`references/performance.md`
- 语言与样式通用质量：`references/code-quality.md`

生成契约出错时，先修正后端结构定义再重新生成，不关闭校验，不追加兜底结构。

## Severity And Output / 分级与输出

- P0：安全 / 隐私 / 数据丢失 / 崩溃 / 关键流程不可达。
- P1：可见回归 / 鉴权错误 / 服务端渲染直出不一致（仅 SSR 生效） / 主交互中断。
- P2：已证实的可维护性 / 性能 / 测试 / 无障碍问题，或违反书面约定。
- P3：细微清理，只在 thorough 评审中报告。

按等级排序，给出行号、失败路径或规则、修复方向。无问题时给出简述与验证缺口。不写恭维话。
