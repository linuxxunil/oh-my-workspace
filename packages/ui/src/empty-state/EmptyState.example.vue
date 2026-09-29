<template>
  <div class="bg-slate-100 p-5">
    <EmptyState title="暂无供应商" description="先在下方表单添加第一个">
      <button type="button">去添加</button>
    </EmptyState>
  </div>
</template>

<script setup lang="ts">
import { EmptyState } from './index'
</script>
