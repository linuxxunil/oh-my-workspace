<template>
  <div class="flex flex-col items-center gap-2 rounded-xl bg-white px-6 py-10 text-center">
    <p class="text-sm font-medium text-slate-700">{{ title }}</p>
    <p v-if="description" class="max-w-sm text-sm text-slate-500">{{ description }}</p>
    <div v-if="$slots.default" class="mt-2">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ title: string; description?: string }>(), { description: '' })
</script>
