<template>
  <div
    :data-nodetype="nodeType"
    :class="[
      'flex w-40 items-center gap-2 rounded-lg bg-white px-3 py-2 shadow-sm ring-1 ring-inset ring-slate-200',
      selected ? 'ring-2 ring-indigo-500' : '',
    ]"
  >
    <Handle type="target" :position="Position.Left" />
    <span aria-hidden="true" :class="['h-2.5 w-2.5 shrink-0 rounded-full', dot]" />
    <span class="min-w-0 flex-1 truncate text-xs font-semibold text-slate-700">{{ nodeType }}</span>
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position, type NodeProps } from '@vue-flow/core'

// 按 NodeProps 声明（nodeTypes 要求完整签名；窄数据经 data 内断言取）。
const props = defineProps<NodeProps>()

const nodeType = computed(() => String((props.data as { nodeType?: string })?.nodeType ?? ''))

const dots: Record<string, string> = {
  start: 'bg-slate-400',
  llm: 'bg-violet-600',
  code: 'bg-emerald-600',
  if: 'bg-amber-500',
  retrieval: 'bg-sky-600',
  end: 'bg-slate-800',
}
const dot = computed(() => dots[nodeType.value] ?? 'bg-slate-300')
</script>
