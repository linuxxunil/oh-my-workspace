<template>
  <slot name="trigger" :trigger-props="triggerProps" :open="open" />
  <Teleport to="body">
    <div
      v-if="open"
      :id="menuId"
      ref="content"
      role="menu"
      :aria-label="label"
      :style="menuStyle"
      class="z-50 min-w-48 rounded-xl bg-white p-1.5 shadow-lg ring-1 ring-slate-200"
      @keydown="onMenuKeydown"
      @click="onMenuClick"
    >
      <slot :close="close" />
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, useId, watch, type VNodeRef } from 'vue'

export interface DropdownMenuTriggerProps {
  type: 'button'
  'aria-haspopup': 'menu'
  'aria-expanded': 'true' | 'false'
  'aria-controls': string
  ref: VNodeRef
  onClick: () => void
  onKeydown: (event: KeyboardEvent) => void
}

const props = defineProps<{ label: string }>()
const open = ref(false)
const trigger = ref<HTMLElement | null>(null)
const content = ref<HTMLElement | null>(null)
const menuId = `ui-menu-${useId()}`
const menuStyle = ref({ top: '0px', right: '8px', position: 'fixed' as const })
let restoreFocus = true

const triggerProps = computed<DropdownMenuTriggerProps>(() => ({
  type: 'button',
  'aria-haspopup': 'menu',
  'aria-expanded': open.value ? 'true' : 'false',
  'aria-controls': menuId,
  ref: (element) => {
    trigger.value = element instanceof HTMLElement ? element : null
  },
  onClick: () => setOpen(!open.value),
  onKeydown: onTriggerKeydown,
}))

function setOpen(value: boolean, focusLast = false) {
  open.value = value
  if (value) void nextTick(() => focusMenuItem(focusLast ? -1 : 0))
}

function close(restore = false) {
  restoreFocus = restore
  open.value = false
  if (restore) void nextTick(() => trigger.value?.focus())
}

function items(): HTMLElement[] {
  return Array.from(
    content.value?.querySelectorAll<HTMLElement>(
      '[role="menuitem"]:not([aria-disabled="true"]):not(:disabled)',
    ) ?? [],
  )
}

function focusMenuItem(index: number) {
  const list = items()
  if (list.length === 0) content.value?.focus()
  else list[(index + list.length) % list.length]?.focus()
}

function updatePosition() {
  const rect = trigger.value?.getBoundingClientRect()
  if (!rect) return
  menuStyle.value = {
    top: `${Math.min(rect.bottom + 8, window.innerHeight - 120)}px`,
    right: `${Math.max(8, window.innerWidth - rect.right)}px`,
    position: 'fixed',
  }
}

function onTriggerKeydown(event: KeyboardEvent) {
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    setOpen(true)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    setOpen(true, true)
  } else if (event.key === 'Escape' && open.value) {
    event.preventDefault()
    close(true)
  }
}

function onMenuKeydown(event: KeyboardEvent) {
  const list = items()
  const current = list.indexOf(document.activeElement as HTMLElement)
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    focusMenuItem(current + 1)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    focusMenuItem(current <= 0 ? list.length - 1 : current - 1)
  } else if (event.key === 'Home') {
    event.preventDefault()
    focusMenuItem(0)
  } else if (event.key === 'End') {
    event.preventDefault()
    focusMenuItem(-1)
  } else if (event.key === 'Escape') {
    event.preventDefault()
    close(true)
  } else if (event.key === 'Tab') {
    close(false)
  }
}

function onMenuClick(event: MouseEvent) {
  if ((event.target as HTMLElement).closest('[role="menuitem"]')) close(false)
}

function onPointerDown(event: PointerEvent) {
  const target = event.target as Node
  if (!trigger.value?.contains(target) && !content.value?.contains(target)) close(false)
}

watch(open, (isOpen) => {
  if (isOpen) {
    void nextTick(updatePosition)
    document.addEventListener('pointerdown', onPointerDown)
    window.addEventListener('resize', updatePosition)
    window.addEventListener('scroll', updatePosition, true)
  } else {
    document.removeEventListener('pointerdown', onPointerDown)
    window.removeEventListener('resize', updatePosition)
    window.removeEventListener('scroll', updatePosition, true)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', onPointerDown)
  window.removeEventListener('resize', updatePosition)
  window.removeEventListener('scroll', updatePosition, true)
})

defineSlots<{
  trigger(props: { triggerProps: DropdownMenuTriggerProps; open: boolean }): unknown
  default(props: { close: (restoreFocus?: boolean) => void }): unknown
}>()

defineExpose({ close })
</script>
