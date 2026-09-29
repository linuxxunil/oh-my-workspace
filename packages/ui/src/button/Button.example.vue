<template>
  <div class="flex flex-wrap items-center gap-3 bg-white p-5">
    <Button>次要默认</Button>
    <Button variant="primary">主要</Button>
    <Button variant="danger">危险</Button>
    <Button :loading="true">加载中</Button>
    <Button :disabled="true">禁用</Button>
    <Button size="sm" variant="primary">小尺寸</Button>
  </div>
</template>

<script setup lang="ts">
import { Button } from './index'
</script>
