<template>
  <span
    :data-tone="tone"
    :class="[
      'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset',
      tones[tone],
    ]"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
export type BadgeTone = 'gray' | 'indigo' | 'sky' | 'green' | 'red'

withDefaults(defineProps<{ tone?: BadgeTone }>(), { tone: 'gray' })

const tones: Record<BadgeTone, string> = {
  gray: 'bg-slate-100 text-slate-600 ring-slate-500/20',
  indigo: 'bg-indigo-50 text-indigo-700 ring-indigo-600/20',
  sky: 'bg-sky-50 text-sky-700 ring-sky-600/20',
  green: 'bg-green-50 text-green-700 ring-green-600/20',
  red: 'bg-red-50 text-red-700 ring-red-600/20',
}
</script>
