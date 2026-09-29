<template>
  <section aria-labelledby="users-title" class="flex flex-col gap-5">
    <h1 id="users-title" class="text-lg font-semibold">{{ t('users.title') }}</h1>
    <p v-if="usersQuery.isLoading.value" class="text-sm text-slate-500">…</p>
    <EmptyState v-else-if="!users.length" :title="t('users.empty')" />
    <ul v-else class="flex flex-col gap-2">
      <li
        v-for="u in users"
        :key="u.id"
        class="flex items-center gap-3 rounded-xl bg-white px-4 py-3 ring-1 ring-inset ring-slate-200"
      >
        <p class="min-w-0 flex-1 truncate text-sm text-slate-800">{{ u.email }}</p>
        <Badge :tone="roleTone(u.role)">{{ u.role }}</Badge>
        <Button variant="secondary" size="sm" @click="remove(u.id)">
          {{ t('users.delete') }}
        </Button>
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
  type UserResponse,
} from '../service/generated/api'

const { t } = useI18n()
const qc = useQueryClient()
const usersQuery = useListUsersUsersGet()
const users = computed<UserResponse[]>(() => usersQuery.data.value ?? [])
const createMut = useCreateUserUsersPost()
const deleteMut = useDeleteUserUsersUserIdDelete()
const email = ref('')
const role = ref<'member' | 'admin'>('member')
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
</script>
