<template>
  <Drawer v-model:open="open" label="Primary navigation">
    <template #trigger="{ triggerProps }">
      <button v-bind="triggerProps" class="rounded-lg px-3 py-2 ring-1 ring-slate-300">
        Open navigation
      </button>
    </template>
    <template #default="{ close }">
      <header class="flex items-center justify-between border-b p-4">
        <h2 class="font-semibold">Navigation</h2>
        <button type="button" aria-label="Close navigation" @click="close()">×</button>
      </header>
      <nav class="flex flex-col gap-2 p-4">
        <a href="/workflows" @click="close(false)">Workflows</a>
        <a href="/models" @click="close(false)">Models</a>
      </nav>
    </template>
  </Drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Drawer } from './index'

const open = ref(false)
</script>
