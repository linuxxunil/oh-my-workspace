<template>
  <Field input-id="ex-name" label="名称" hint="示例：我的流程" error="">
    <template #default="{ inputId, describedBy }">
      <TextInput :id="inputId" :aria-describedby="describedBy" placeholder="填点什么" />
    </template>
  </Field>
</template>

<script setup lang="ts">
import { Field } from './index'
import { TextInput } from '../input'
</script>
