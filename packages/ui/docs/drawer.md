# Drawer / 抽屉

受控模态侧栏，用于小屏导航或需要临时侧向内容的场景。内容 Teleport 到 body；基元负责 modal 语义、焦点循环、Escape、遮罩关闭、body 滚动锁与触发器焦点恢复。

```vue
<Drawer v-model:open="open" label="Primary navigation" side="left">
  <template #trigger="{ triggerProps }">
    <button v-bind="triggerProps">Open navigation</button>
  </template>
  <template #default="{ close }">
    <button type="button" @click="close()">Close</button>
  </template>
</Drawer>
```

- `open` / `update:open` 由业务 owner 控制；`label` 为 dialog 可访问名称；`side` 默认为 `left`。
- Trigger slot 的 `triggerProps` 必须绑定到原生 button。
- 遮罩和 Escape 关闭时恢复触发器焦点；导航项使用 `close(false)` 避免路由切换时抢回焦点。
- 外层应用应按 `packages/ui/docs/overlays.md` 建立隔离层叠上下文。
