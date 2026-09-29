<template>
  <input
    :id="id"
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :required="required"
    :disabled="disabled"
    :aria-invalid="invalid ? 'true' : undefined"
    :aria-describedby="describedBy"
    :data-invalid="invalid ? '' : undefined"
    :class="classes"
    @input="onInput"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    id?: string
    type?: string
    modelValue?: string
    placeholder?: string
    required?: boolean
    disabled?: boolean
    /** 校验失败态（拥有方判定，基元只表达）。 */
    invalid?: boolean
    describedBy?: string
  }>(),
  { id: undefined, type: 'text', modelValue: '', placeholder: '', required: false, disabled: false, invalid: false, describedBy: undefined },
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const classes = computed(() => [
  'block w-full rounded-lg bg-white px-3 py-2 text-sm text-slate-800',
  'ring-1 ring-inset placeholder:text-slate-400',
  'focus-visible:outline-none focus-visible:ring-2',
  'disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed',
  props.invalid
    ? 'ring-red-500 focus-visible:ring-red-500/40'
    : 'ring-slate-300 focus-visible:ring-indigo-500/40',
])

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>
