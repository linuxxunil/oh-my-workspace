<template>
  <button
    :type="type"
    :disabled="disabled"
    :aria-disabled="loading ? 'true' : undefined"
    :data-variant="variant"
    :data-size="size"
    :data-loading="loading ? '' : undefined"
    :class="classes"
    @click="onClick"
  >
    <span v-if="loading" aria-hidden="true" class="ui-btn-spinner" />
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export type ButtonVariant = 'primary' | 'secondary' | 'danger'
export type ButtonSize = 'sm' | 'md'

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariant
    size?: ButtonSize
    type?: 'button' | 'submit'
    loading?: boolean
    disabled?: boolean
  }>(),
  { variant: 'secondary', size: 'md', type: 'button', loading: false, disabled: false },
)

const emit = defineEmits<{ click: [event: MouseEvent] }>()

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-indigo-600 text-white hover:bg-indigo-700',
  secondary: 'bg-white text-slate-700 ring-1 ring-inset ring-slate-300 hover:bg-slate-50',
  danger: 'bg-red-600 text-white hover:bg-red-700',
}
const sizes: Record<ButtonSize, string> = {
  // 内容间距归基元（sm gap 3px≈gap-1，md gap 8px=gap-2），调用方不加 gap。
  sm: 'h-8 gap-1 px-3 text-sm',
  md: 'h-10 gap-2 px-4 text-sm',
}

const classes = computed(() => [
  'inline-flex items-center justify-center rounded-lg font-medium transition-colors',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40',
  'disabled:cursor-not-allowed disabled:opacity-50',
  variants[props.variant],
  sizes[props.size],
])

function onClick(event: MouseEvent) {
  // loading 阻断激活但保留焦点（见 docs/button.md），不靠 disabled 移出 Tab 序。
  if (props.loading) return
  emit('click', event)
}
</script>

<style scoped>
.ui-btn-spinner {
  width: 1em;
  height: 1em;
  border-radius: 9999px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  animation: ui-btn-spin 0.8s linear infinite;
}
@keyframes ui-btn-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
