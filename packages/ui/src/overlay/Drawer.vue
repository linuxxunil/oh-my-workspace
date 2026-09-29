<template>
  <slot name="trigger" :trigger-props="triggerProps" :open="open" />
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-slate-950/40" aria-hidden="true" @click="close(true)" />
      <section
        :id="drawerId"
        ref="panel"
        role="dialog"
        aria-modal="true"
        :aria-label="label"
        tabindex="-1"
        :class="[
          'absolute inset-y-0 flex w-80 max-w-[calc(100vw-2rem)] flex-col bg-white shadow-xl outline-none',
          side === 'left' ? 'left-0' : 'right-0',
        ]"
        @keydown="onKeydown"
      >
        <slot :close="close" />
      </section>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, useId, watch, type VNodeRef } from 'vue'

export interface DrawerTriggerProps {
  type: 'button'
  'aria-haspopup': 'dialog'
  'aria-expanded': 'true' | 'false'
  'aria-controls': string
  ref: VNodeRef
  onClick: () => void
}

const props = withDefaults(
  defineProps<{
    open: boolean
    label: string
    side?: 'left' | 'right'
  }>(),
  { side: 'left' },
)
const emit = defineEmits<{ 'update:open': [open: boolean] }>()
const trigger = ref<HTMLElement | null>(null)
const panel = ref<HTMLElement | null>(null)
const drawerId = `ui-drawer-${useId()}`
let previousOverflow = ''
let restoreFocusOnClose = true
let bodyLocked = false
let wasOpen = false

const triggerProps = computed<DrawerTriggerProps>(() => ({
  type: 'button',
  'aria-haspopup': 'dialog',
  'aria-expanded': props.open ? 'true' : 'false',
  'aria-controls': drawerId,
  ref: (element) => {
    trigger.value = element instanceof HTMLElement ? element : null
  },
  onClick: () => emit('update:open', !props.open),
}))

function close(restoreFocus = true) {
  restoreFocusOnClose = restoreFocus
  emit('update:open', false)
}

function focusables(): HTMLElement[] {
  return Array.from(
    panel.value?.querySelectorAll<HTMLElement>(
      'a[href], button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])',
    ) ?? [],
  ).filter((element) => !element.hasAttribute('aria-hidden'))
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    event.preventDefault()
    close(true)
    return
  }
  if (event.key !== 'Tab') return

  const list = focusables()
  const first = list[0]
  const last = list[list.length - 1]
  if (!first || !last) {
    event.preventDefault()
    panel.value?.focus()
  } else if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      wasOpen = true
      previousOverflow = document.body.style.overflow
      document.body.style.overflow = 'hidden'
      bodyLocked = true
      await nextTick()
      const first = focusables()[0]
      ;(first ?? panel.value)?.focus()
    } else {
      if (!wasOpen) return
      if (bodyLocked) {
        document.body.style.overflow = previousOverflow
        bodyLocked = false
      }
      if (restoreFocusOnClose) await nextTick(() => trigger.value?.focus())
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  if (bodyLocked) document.body.style.overflow = previousOverflow
})

defineSlots<{
  trigger(props: { triggerProps: DrawerTriggerProps; open: boolean }): unknown
  default(props: { close: (restoreFocus?: boolean) => void }): unknown
}>()
</script>
