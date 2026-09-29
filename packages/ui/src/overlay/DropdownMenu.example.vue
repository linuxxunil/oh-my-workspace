<template>
  <DropdownMenu label="Account actions">
    <template #trigger="{ triggerProps }">
      <button v-bind="triggerProps" class="rounded-lg px-3 py-2 ring-1 ring-slate-300">
        Account
      </button>
    </template>
    <template #default="{ close }">
      <RouterLink to="/account" role="menuitem" class="block rounded-md px-3 py-2" @click="close()">
        Account settings
      </RouterLink>
      <button role="menuitem" class="block w-full rounded-md px-3 py-2 text-left" @click="close()">
        Sign out
      </button>
    </template>
  </DropdownMenu>
</template>

<script setup lang="ts">
import { DropdownMenu } from './index'
</script>
