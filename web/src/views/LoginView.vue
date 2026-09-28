<template>
  <section aria-labelledby="login-title">
    <h1 id="login-title">{{ t('auth.login') }}</h1>
    <form @submit.prevent="onSubmit">
      <div>
        <label for="email">{{ t('auth.email') }}</label>
        <input id="email" v-model="email" type="email" required autocomplete="username" />
      </div>
      <div>
        <label for="password">{{ t('auth.password') }}</label>
        <input
          id="password"
          v-model="password"
          type="password"
          required
          autocomplete="current-password"
        />
      </div>
      <p v-if="error" role="alert">{{ t('auth.failed') }}</p>
      <button type="submit" :disabled="submitting">{{ t('auth.submit') }}</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
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
