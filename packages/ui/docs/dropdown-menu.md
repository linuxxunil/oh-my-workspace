# DropdownMenu / 下拉菜单

按钮触发的动作列表。此基元拥有 open 状态、Teleport、定位、焦点及键盘行为；业务通过 trigger 与 default slot 提供真实触发按钮和 `role="menuitem"` 项。

```vue
<DropdownMenu label="Account actions">
  <template #trigger="{ triggerProps }">
    <button v-bind="triggerProps">Account</button>
  </template>
  <template #default="{ close }">
    <RouterLink to="/account" role="menuitem" @click="close()">Account</RouterLink>
  </template>
</DropdownMenu>
```

- `label` 为菜单可访问名称。
- Trigger slot 收到 `triggerProps` 和 `open`；必须将 props 绑定到原生 button。
- 菜单项使用 `role="menuitem"`。基元处理 ArrowUp/Down、Home/End、Escape、Tab、外部点击和激活后关闭。
- `close(restoreFocus)` 默认不抢回焦点；Escape 时恢复触发按钮焦点，路由动作使用默认关闭即可。
