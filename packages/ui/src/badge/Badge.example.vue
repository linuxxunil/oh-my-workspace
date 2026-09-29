<template>
  <div class="flex flex-col gap-4 bg-white p-5">
    <Badge>默认灰</Badge>
    <Badge tone="indigo">super_admin</Badge>
    <Badge tone="sky">admin</Badge>
    <Badge tone="green">ok(2)</Badge>
    <Badge tone="red">fail</Badge>
  </div>
</template>

<script setup lang="ts">
import { Badge } from '../badge'
</script>
