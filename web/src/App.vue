<template>
  <div>
    <a class="skip-link" href="#main">{{ t('app.skip') }}</a>
    <header>
      <nav aria-label="主导航">
        <RouterLink to="/workflows">{{ t('nav.workflows') }}</RouterLink>
        <RouterLink to="/models">{{ t('nav.models') }}</RouterLink>
        <RouterLink to="/users">{{ t('nav.users') }}</RouterLink>
        <button type="button" @click="logout">{{ t('auth.logout') }}</button>
      </nav>
    </header>
    <main id="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  void router.push('/login')
}
</script>

<style>
.skip-link {
  position: absolute;
  left: -9999px;
}
.skip-link:focus {
  left: 0;
}
</style>
