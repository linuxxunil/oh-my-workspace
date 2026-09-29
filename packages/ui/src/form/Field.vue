<template>
  <div>
    <label :for="inputId" class="mb-1 block text-sm font-medium text-slate-700">
      {{ label }}
      <span v-if="required" aria-hidden="true" class="text-red-600">*</span>
    </label>
    <slot :input-id="inputId" :invalid="hasError" :described-by="describedBy" />
    <p v-if="hint && !hasError" :id="`${inputId}-hint`" class="mt-1 text-xs text-slate-500">
      {{ hint }}
    </p>
    <p
      v-if="hasError"
      :id="`${inputId}-error`"
      role="alert"
      class="mt-1 text-xs text-red-600"
    >
      {{ error }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    /** 调用方拥有的 input id（e2e 与 label 关联共用，确定性优先）。 */
    inputId: string
    label: string
    hint?: string
    error?: string
    required?: boolean
  }>(),
  { hint: '', error: '', required: false },
)

const hasError = computed(() => props.error !== '')
const describedBy = computed(() =>
  hasError.value ? `${props.inputId}-error` : props.hint ? `${props.inputId}-hint` : undefined,
)
</script>
