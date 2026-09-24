# Frontend Lint Guide (Vue) / 静态检查指南

在 `web/` 下执行：

```bash
vp check web        # eslint-plugin-vue + oxlint
vue-tsc --noEmit    # 类型
```

## Lint Rules / 检查规则

- `eslint.config.mjs + oxlint` 为交付门禁；suppression 必须写清理由与过期条件。
- 生成目录（`src/service/generated/*`）不允许手改，lint 报错先回查后端 schema。
- Tailwind 只用 canonical v4 写法；`common.ts` 桶文件与跨 feature 深链 import 由 lint 与 Review 联合拦截。
