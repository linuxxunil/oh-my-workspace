<template>
  <section aria-labelledby="models-title" class="flex flex-col gap-5">
    <h1 id="models-title" class="text-lg font-semibold">{{ t('models.title') }}</h1>
    <p v-if="providersQuery.isLoading.value" class="text-sm text-slate-500">…</p>
    <EmptyState v-else-if="!providers.length" :title="t('models.empty')" />
    <ul v-else class="flex flex-col gap-2">
      <li
        v-for="p in providers"
        :key="p.id"
        class="flex flex-col gap-2 rounded-xl bg-white px-4 py-3 ring-1 ring-inset ring-slate-200"
      >
        <div class="flex flex-wrap items-center gap-x-3 gap-y-2">
          <p class="min-w-0 flex-1 text-sm font-medium text-slate-800">{{ p.name }}</p>
          <Badge :tone="p.type === 'opencode_go' ? 'indigo' : 'sky'">{{ p.type }}</Badge>
          <Button variant="secondary" size="sm" @click="toggleEdit(p.id)">
            {{ editingId === p.id ? t('models.cancel') : t('models.edit') }}
          </Button>
          <Button variant="secondary" size="sm" @click="test(p.id)">{{ t('models.test') }}</Button>
          <Button variant="secondary" size="sm" @click="remove(p.id, p.name)">
            {{ t('models.delete') }}
          </Button>
          <span
            v-if="results[p.id]"
            class="text-xs font-medium"
            :class="results[p.id]?.startsWith('ok') ? 'text-green-700' : 'text-red-700'"
          >
            {{ results[p.id] }}
          </span>
        </div>
        <p class="truncate text-xs text-slate-500">{{ p.base_url }}</p>
        <p
          v-if="rowErrors[p.id]"
          role="alert"
          class="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700"
        >
          {{ rowErrors[p.id] }}
        </p>
        <form
          v-if="editingId === p.id"
          class="flex flex-col gap-3 border-t border-slate-100 pt-3"
          @submit.prevent="save(p.id)"
        >
          <Field :input-id="`ep-name-${p.id}`" :label="t('models.name')">
            <template #default="{ inputId }">
              <TextInput :id="inputId" v-model="editName" required />
            </template>
          </Field>
          <Field :input-id="`ep-url-${p.id}`" :label="t('models.baseUrl')">
            <template #default="{ inputId }">
              <TextInput :id="inputId" v-model="editUrl" type="url" required />
            </template>
          </Field>
          <Field
            :input-id="`ep-key-${p.id}`"
            :label="t('models.apiKey')"
            :hint="t('models.apiKeyHint')"
          >
            <template #default="{ inputId }">
              <TextInput
                :id="inputId"
                v-model="editKey"
                type="password"
                autocomplete="new-password"
                placeholder="••••••••"
              />
            </template>
          </Field>
          <div>
            <Button type="submit" variant="primary" size="sm" :loading="saving">
              {{ t('models.save') }}
            </Button>
          </div>
        </form>
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
      <Field input-id="np-key" :label="t('models.apiKey')" :hint="t('models.apiKeyHint')">
        <template #default="{ inputId }">
          <TextInput
            :id="inputId"
            v-model="apiKey"
            type="password"
            autocomplete="new-password"
            placeholder="sk-…"
          />
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
  useDeleteProviderModelsProvidersProviderIdDelete,
  useListProvidersModelsProvidersGet,
  useUpdateProviderModelsProvidersProviderIdPatch,
  type ProviderResponse,
} from '../service/generated/api'

const { t } = useI18n()
const qc = useQueryClient()
const providersQuery = useListProvidersModelsProvidersGet()
const providers = computed<ProviderResponse[]>(() => providersQuery.data.value ?? [])
const createMut = useCreateProviderModelsProvidersPost()
const updateMut = useUpdateProviderModelsProvidersProviderIdPatch()
const deleteMut = useDeleteProviderModelsProvidersProviderIdDelete()
const name = ref('')
const ptype = ref<'openai_compatible' | 'opencode_go'>('openai_compatible')
const typeOptions = [
  { value: 'openai_compatible', label: 'openai_compatible' },
  { value: 'opencode_go', label: 'opencode_go' },
]
// 按类型出字段表（首批两通道同形：名称/地址/API Key；extra_headers 二期再开）。
const baseUrl = ref('')
const apiKey = ref('')
const results = reactive<Record<string, string>>({})
const rowErrors = reactive<Record<string, string>>({})
const editingId = ref<string | null>(null)
const editName = ref('')
const editUrl = ref('')
const editKey = ref('')
const saving = computed(() => updateMut.isPending.value === true)

async function create() {
  await createMut.mutateAsync({
    data: { type: ptype.value, name: name.value, base_url: baseUrl.value, api_key: apiKey.value },
  })
  name.value = ''
  baseUrl.value = ''
  apiKey.value = ''
  await qc.invalidateQueries()
}

async function test(id: string) {
  const r = await testConnectionModelsProvidersProviderIdTestPost(id)
  results[id] = r.ok ? `ok(${String(r.model_count)})` : 'fail'
}

async function remove(id: string, name: string) {
  // 原生二次确认（无 dialog 基元）；取消即返回。
  if (!window.confirm(t('models.confirmDelete', { name }))) return
  delete rowErrors[id]
  try {
    await deleteMut.mutateAsync({ providerId: id })
  } catch (e) {
    // 被流程引用时 409，行内明示引用名，行保留。
    rowErrors[id] = String(
      (e as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? e,
    )
    return
  }
  await qc.invalidateQueries()
}

function toggleEdit(id: string) {
  if (editingId.value === id) {
    editingId.value = null
    return
  }
  const p = providers.value.find((x) => x.id === id)
  editingId.value = id
  editName.value = p?.name ?? ''
  editUrl.value = p?.base_url ?? ''
  editKey.value = ''
}

async function save(id: string) {
  await updateMut.mutateAsync({
    providerId: id,
    data: { name: editName.value, base_url: editUrl.value, api_key: editKey.value },
  })
  editingId.value = null
  await qc.invalidateQueries()
}
</script>
