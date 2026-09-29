<template>
  <section aria-labelledby="flows-title" class="flex flex-col gap-5">
    <h1 id="flows-title" class="text-lg font-semibold">{{ t('flows.title') }}</h1>
    <p v-if="flowsQuery.isLoading.value" class="text-sm text-slate-500">…</p>
    <EmptyState v-else-if="!flows.length" :title="t('flows.empty')" />
    <ul v-else class="grid grid-cols-1 gap-3 md:grid-cols-2">
      <li
        v-for="w in flows"
        :key="w.id"
        class="flex items-center gap-3 rounded-xl bg-white px-4 py-3 ring-1 ring-inset ring-slate-200"
      >
        <p class="min-w-0 flex-1 truncate text-sm font-medium text-slate-800">{{ w.name }}</p>
        <RouterLink
          :to="`/workflows/${w.id}`"
          class="inline-flex h-8 items-center rounded-lg bg-white px-3 text-sm font-medium text-indigo-700 ring-1 ring-inset ring-indigo-200 hover:bg-indigo-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
        >
          {{ t('flows.open') }}
        </RouterLink>
      </li>
    </ul>
    <form
      class="flex flex-col gap-4 rounded-xl bg-white p-5 ring-1 ring-inset ring-slate-200"
      @submit.prevent="create"
    >
      <Field input-id="nw-name" :label="t('flows.title')">
        <template #default="{ inputId }">
          <TextInput :id="inputId" v-model="name" required />
        </template>
      </Field>
      <div>
        <Button type="submit" variant="primary">{{ t('flows.new') }}</Button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQueryClient } from '@tanstack/vue-query'
import { Button } from '@/packages/ui/button'
import { EmptyState } from '@/packages/ui/empty-state'
import { Field } from '@/packages/ui/form'
import { TextInput } from '@/packages/ui/input'
import {
  createWorkflowWorkflowsPost,
  useListWorkflowsWorkflowsGet,
  type WorkflowResponse,
} from '../service/generated/api'
import { blankDag } from '../utils/dag'

const { t } = useI18n()
const qc = useQueryClient()
const flowsQuery = useListWorkflowsWorkflowsGet()
const flows = computed<WorkflowResponse[]>(() => flowsQuery.data.value ?? [])
const name = ref('')

async function create() {
  await createWorkflowWorkflowsPost({ name: name.value, description: '', dag: blankDag() })
  name.value = ''
  await qc.invalidateQueries()
}
</script>
