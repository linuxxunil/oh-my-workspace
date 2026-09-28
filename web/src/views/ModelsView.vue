<template>
  <section aria-labelledby="models-title">
    <h1 id="models-title">{{ t('models.title') }}</h1>
    <p v-if="providersQuery.isLoading.value">…</p>
    <p v-else-if="!providers.length">{{ t('models.empty') }}</p>
    <ul v-else>
      <li v-for="p in providers" :key="p.id">
        {{ p.name }}（{{ p.type }}）{{ p.base_url }}
        <button type="button" @click="test(p.id)">{{ t('models.test') }}</button>
        <span v-if="results[p.id]">{{ results[p.id] }}</span>
      </li>
    </ul>
    <form @submit.prevent="create">
      <label for="np-name">{{ t('models.name') }}</label>
      <input id="np-name" v-model="name" required />
      <label for="np-type">{{ t('models.type') }}</label>
      <select id="np-type" v-model="ptype">
        <option value="openai_compatible">openai_compatible</option>
        <option value="opencode_go">opencode_go</option>
      </select>
      <label for="np-url">{{ t('models.baseUrl') }}</label>
      <input id="np-url" v-model="baseUrl" type="url" required placeholder="https://…" />
      <button type="submit">{{ t('models.title') }}</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQueryClient } from '@tanstack/vue-query'
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
