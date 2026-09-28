<template>
  <section aria-labelledby="users-title">
    <h1 id="users-title">{{ t('users.title') }}</h1>
    <p v-if="usersQuery.isLoading.value">…</p>
    <p v-else-if="!users.length">{{ t('users.empty') }}</p>
    <ul v-else>
      <li v-for="u in users" :key="u.id">
        {{ u.email }}（{{ u.role }}）
        <button type="button" @click="remove(u.id)">{{ t('users.delete') }}</button>
      </li>
    </ul>
    <form @submit.prevent="create">
      <label for="nu-email">{{ t('users.email') }}</label>
      <input id="nu-email" v-model="email" type="email" required />
      <label for="nu-role">{{ t('users.role') }}</label>
      <select id="nu-role" v-model="role">
        <option value="member">member</option>
        <option value="admin">admin</option>
      </select>
      <button type="submit">{{ t('users.create') }}</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQueryClient } from '@tanstack/vue-query'
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
