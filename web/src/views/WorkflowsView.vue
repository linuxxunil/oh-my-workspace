<template>
  <section aria-labelledby="flows-title">
    <h1 id="flows-title">{{ t('flows.title') }}</h1>
    <p v-if="flowsQuery.isLoading.value">…</p>
    <p v-else-if="!flows.length">{{ t('flows.empty') }}</p>
    <ul v-else>
      <li v-for="w in flows" :key="w.id">
        {{ w.name }}
        <RouterLink :to="`/workflows/${w.id}`">{{ t('flows.open') }}</RouterLink>
      </li>
    </ul>
    <form @submit.prevent="create">
      <label for="nw-name">{{ t('flows.title') }}</label>
      <input id="nw-name" v-model="name" required />
      <button type="submit">{{ t('flows.new') }}</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQueryClient } from '@tanstack/vue-query'
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
