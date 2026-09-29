<template>
  <select
    :id="id"
    :value="modelValue"
    :required="required"
    :disabled="disabled"
    :aria-describedby="describedBy"
    class="block w-full rounded-lg bg-white px-3 py-2 text-sm text-slate-800 ring-1 ring-inset ring-slate-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40 disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
    @change="onChange"
  >
    <option v-for="opt in options" :key="String(opt.value)" :value="opt.value">
      {{ opt.label }}
    </option>
  </select>
</template>

<script setup lang="ts">
export interface SelectOption {
  value: string
  label: string
}

withDefaults(
  defineProps<{
    id?: string
    /** 值保留调用方领域类型（本轮为 string；放宽按 selection.md 走）。 */
    modelValue?: string
    options?: SelectOption[]
    required?: boolean
    disabled?: boolean
    describedBy?: string
  }>(),
  { id: undefined, modelValue: '', options: () => [], required: false, disabled: false, describedBy: undefined },
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

function onChange(event: Event) {
  emit('update:modelValue', (event.target as HTMLSelectElement).value)
}
</script>
