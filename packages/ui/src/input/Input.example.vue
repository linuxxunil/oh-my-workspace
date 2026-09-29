<template>
  <div class="flex flex-col gap-4 bg-white p-5">
    <TextInput placeholder="文本输入" />
    <TextInput placeholder="失败态" :invalid="true" model-value="错的" />
    <Textarea placeholder="多行输入" />
  </div>
</template>

<script setup lang="ts">
import { Textarea, TextInput } from './index'
</script>
