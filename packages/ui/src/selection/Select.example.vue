<template>
  <div class="bg-white p-5">
    <Select :options="options" model-value="openai_compatible" />
  </div>
</template>

<script setup lang="ts">
import { Select } from './index'

const options = [
  { value: 'openai_compatible', label: 'openai_compatible' },
  { value: 'opencode_go', label: 'opencode_go' },
]
</script>
