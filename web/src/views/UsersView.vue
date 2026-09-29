<template>
  <section aria-labelledby="users-title" class="flex flex-col gap-5">
    <h1 id="users-title" class="text-lg font-semibold">{{ t('users.title') }}</h1>
    <p v-if="usersQuery.isLoading.value" class="text-sm text-slate-500">…</p>
    <EmptyState v-else-if="!users.length" :title="t('users.empty')" />
    <ul v-else class="flex flex-col gap-2">
      <li
        v-for="u in users"
        :key="u.id"
        class="flex flex-col gap-2 rounded-xl bg-white px-4 py-3 ring-1 ring-inset ring-slate-200"
      >
        <div class="flex items-center gap-3">
          <p class="min-w-0 flex-1 truncate text-sm text-slate-800">{{ u.email }}</p>
          <Badge :tone="roleTone(u.role)">{{ u.role }}</Badge>
          <Button variant="secondary" size="sm" @click="toggleReset(u.id)">
            {{ resettingId === u.id ? t('models.cancel') : t('users.resetPassword') }}
          </Button>
          <Button variant="secondary" size="sm" @click="remove(u.id)">
            {{ t('users.delete') }}
          </Button>
        </div>
        <form
          v-if="resettingId === u.id"
          class="flex flex-col gap-3 border-t border-slate-100 pt-3"
          @submit.prevent="savePassword(u.id)"
        >
          <Field :input-id="`rp-pwd-${u.id}`" :label="t('users.newPassword')">
            <template #default="{ inputId }">
              <TextInput
                :id="inputId"
                v-model="newPassword"
                type="password"
                required
                minlength="8"
                autocomplete="new-password"
              />
            </template>
          </Field>
          <div>
            <Button type="submit" variant="primary" size="sm" :loading="saving">
              {{ t('models.save') }}
            </Button>
          </div>
          <p
            v-if="resetError"
            role="alert"
            class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
          >
            {{ resetError }}
          </p>
        </form>
      </li>
    </ul>
    <form
      class="flex flex-col gap-4 rounded-xl bg-white p-5 ring-1 ring-inset ring-slate-200"
      @submit.prevent="create"
    >
      <Field input-id="nu-email" :label="t('users.email')">
        <template #default="{ inputId }">
          <TextInput :id="inputId" v-model="email" type="email" required />
        </template>
      </Field>
      <Field input-id="nu-role" :label="t('users.role')">
        <template #default="{ inputId }">
          <Select :id="inputId" v-model="role" :options="roleOptions" />
        </template>
      </Field>
      <div>
        <Button type="submit" variant="primary">{{ t('users.create') }}</Button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQueryClient } from '@tanstack/vue-query'
import { Badge, type BadgeTone } from '@/packages/ui/badge'
import { Button } from '@/packages/ui/button'
import { EmptyState } from '@/packages/ui/empty-state'
import { Field } from '@/packages/ui/form'
import { TextInput } from '@/packages/ui/input'
import { Select } from '@/packages/ui/selection'
import {
  useCreateUserUsersPost,
  useDeleteUserUsersUserIdDelete,
  useListUsersUsersGet,
  useUpdateUserUsersUserIdPatch,
  type UserResponse,
} from '../service/generated/api'

const { t } = useI18n()
const qc = useQueryClient()
const usersQuery = useListUsersUsersGet()
const users = computed<UserResponse[]>(() => usersQuery.data.value ?? [])
const createMut = useCreateUserUsersPost()
const deleteMut = useDeleteUserUsersUserIdDelete()
const updateMut = useUpdateUserUsersUserIdPatch()
const email = ref('')
const role = ref<'member' | 'admin'>('member')
const resettingId = ref<string | null>(null)
const newPassword = ref('')
const resetError = ref('')
const saving = computed(() => updateMut.isPending.value === true)
const roleOptions = [
  { value: 'member', label: 'member' },
  { value: 'admin', label: 'admin' },
]

function roleTone(role: string): BadgeTone {
  if (role === 'super_admin') return 'indigo'
  if (role === 'admin') return 'sky'
  return 'gray'
}

async function create() {
  await createMut.mutateAsync({
    data: { email: email.value, password: 'User12345', role: role.value },
  })
  email.value = ''
  await qc.invalidateQueries()
}

async function remove(id: string) {
  await deleteMut.mutateAsync({ userId: id })
  await qc.invalidateQueries()
}

function toggleReset(id: string) {
  resettingId.value = resettingId.value === id ? null : id
  newPassword.value = ''
  resetError.value = ''
}

async function savePassword(id: string) {
  resetError.value = ''
  try {
    await updateMut.mutateAsync({ userId: id, data: { password: newPassword.value } })
  } catch (e) {
    // 失败保持表单展开并明示（如 admin 动 super_admin 的 403）。
    resetError.value = String(
      (e as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? e,
    )
    return
  }
  resettingId.value = null
  newPassword.value = ''
  await qc.invalidateQueries()
}
</script>
