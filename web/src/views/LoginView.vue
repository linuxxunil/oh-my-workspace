<template>
  <section aria-labelledby="login-title" class="mx-auto mt-16 w-full max-w-sm">
    <div class="rounded-xl bg-white p-6 ring-1 ring-inset ring-slate-200">
      <h1 id="login-title" class="mb-5 text-center text-lg font-semibold">{{ t('auth.login') }}</h1>
      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <Field input-id="email" :label="t('auth.email')">
          <template #default="{ inputId }">
            <TextInput :id="inputId" v-model="email" type="email" required autocomplete="username" />
          </template>
        </Field>
        <Field input-id="password" :label="t('auth.password')">
          <template #default="{ inputId }">
            <TextInput
              :id="inputId"
              v-model="password"
              type="password"
              required
              autocomplete="current-password"
            />
          </template>
        </Field>
        <p v-if="error" role="alert" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {{ t('auth.failed') }}
        </p>
        <Button type="submit" variant="primary" class="w-full" :loading="submitting">
          {{ t('auth.submit') }}
        </Button>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Button } from '@/packages/ui/button'
import { Field } from '@/packages/ui/form'
import { TextInput } from '@/packages/ui/input'
import { meAuthMeGet, useLoginAuthLoginPost } from '../service/generated/api'
import { tokenHolder } from '../service/auth-token'
import { useAuthStore } from '../stores/auth'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref(false)
const login = useLoginAuthLoginPost()
const submitting = computed(() => login.isPending.value === true)

async function onSubmit() {
  if (login.isPending.value) return // loading 窗口内连点/回车不再并发提交（TEST-003 P3-1）
  error.value = false
  try {
    const token = await login.mutateAsync({
      data: { email: email.value, password: password.value },
    })
    tokenHolder.token = token.access_token
    const me = await meAuthMeGet()
    auth.setSession({ token: token.access_token, email: me.email, role: String(me.role) })
    await router.push('/workflows')
  } catch {
    error.value = true
  }
}
</script>
