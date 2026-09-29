<template>
  <textarea
    :id="id"
    :value="modelValue"
    :placeholder="placeholder"
    :rows="rows"
    :required="required"
    :disabled="disabled"
    :aria-invalid="invalid ? 'true' : undefined"
    :aria-describedby="describedBy"
    :data-invalid="invalid ? '' : undefined"
    class="block w-full rounded-lg bg-white px-3 py-2 text-sm text-slate-800 ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40 disabled:bg-slate-50 disabled:text-slate-500 disabled:cursor-not-allowed"
    @input="onInput"
  />
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    id?: string
    modelValue?: string
    placeholder?: string
    rows?: number
    required?: boolean
    disabled?: boolean
    invalid?: boolean
    describedBy?: string
  }>(),
  { id: undefined, modelValue: '', placeholder: '', rows: 3, required: false, disabled: false, invalid: false, describedBy: undefined },
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLTextAreaElement).value)
}
</script>
