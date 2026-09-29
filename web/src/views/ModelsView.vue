<template>
  <section aria-labelledby="models-title" class="flex flex-col gap-5">
    <h1 id="models-title" class="text-lg font-semibold">{{ t('models.title') }}</h1>
    <p v-if="providersQuery.isLoading.value" class="text-sm text-slate-500">…</p>
    <EmptyState v-else-if="!providers.length" :title="t('models.empty')" />
    <ul v-else class="flex flex-col gap-2">
      <li
        v-for="p in providers"
        :key="p.id"
        class="flex flex-wrap items-center gap-x-3 gap-y-2 rounded-xl bg-white px-4 py-3 ring-1 ring-inset ring-slate-200"
      >
        <p class="min-w-0 flex-1 text-sm font-medium text-slate-800">{{ p.name }}</p>
        <Badge :tone="p.type === 'opencode_go' ? 'indigo' : 'sky'">{{ p.type }}</Badge>
        <p class="w-full truncate text-xs text-slate-500">{{ p.base_url }}</p>
        <Button variant="secondary" size="sm" @click="test(p.id)">{{ t('models.test') }}</Button>
        <span v-if="results[p.id]" class="text-xs font-medium" :class="results[p.id]?.startsWith('ok') ? 'text-green-700' : 'text-red-700'">
          {{ results[p.id] }}
        </span>
      </li>
    </ul>
    <form
      class="flex flex-col gap-4 rounded-xl bg-white p-5 ring-1 ring-inset ring-slate-200"
      @submit.prevent="create"
    >
      <Field input-id="np-name" :label="t('models.name')">
        <template #default="{ inputId }">
          <TextInput :id="inputId" v-model="name" required />
        </template>
      </Field>
      <Field input-id="np-type" :label="t('models.type')">
        <template #default="{ inputId }">
          <Select :id="inputId" v-model="ptype" :options="typeOptions" />
        </template>
      </Field>
      <Field input-id="np-url" :label="t('models.baseUrl')">
        <template #default="{ inputId }">
          <TextInput :id="inputId" v-model="baseUrl" type="url" required placeholder="https://…" />
        </template>
      </Field>
      <div>
        <Button type="submit" variant="primary">{{ t('models.title') }}</Button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQueryClient } from '@tanstack/vue-query'
import { Badge } from '@/packages/ui/badge'
import { Button } from '@/packages/ui/button'
import { EmptyState } from '@/packages/ui/empty-state'
import { Field } from '@/packages/ui/form'
import { TextInput } from '@/packages/ui/input'
import { Select } from '@/packages/ui/selection'
import {
  testConnectionModelsProvidersProviderIdTestPost,
  useCreateProviderModelsProvidersPost,
  useListProvidersModelsProvidersGet,
  type ProviderResponse,
} from '../service/generated/api'

const { t } = useI18n()
const qc = useQueryClient()
const providersQuery = useListProvidersModelsProvidersGet()
const providers = computed<ProviderResponse[]>(() => providersQuery.data.value ?? [])
const createMut = useCreateProviderModelsProvidersPost()
const name = ref('')
const ptype = ref<'openai_compatible' | 'opencode_go'>('openai_compatible')
const typeOptions = [
  { value: 'openai_compatible', label: 'openai_compatible' },
  { value: 'opencode_go', label: 'opencode_go' },
]
const baseUrl = ref('')
const results = reactive<Record<string, string>>({})

async function create() {
  await createMut.mutateAsync({
    data: { type: ptype.value, name: name.value, base_url: baseUrl.value },
  })
  name.value = ''
  baseUrl.value = ''
  await qc.invalidateQueries()
}

async function test(id: string) {
  const r = await testConnectionModelsProvidersProviderIdTestPost(id)
  results[id] = r.ok ? `ok(${String(r.model_count)})` : 'fail'
}
</script>
