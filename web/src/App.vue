<template>
  <div class="min-h-screen bg-surface text-slate-800">
    <a class="skip-link" href="#main">{{ t('app.skip') }}</a>
    <div class="flex min-h-screen">
      <aside
        v-if="auth.token"
        class="flex w-60 shrink-0 flex-col gap-6 bg-white p-5 ring-1 ring-inset ring-slate-200"
      >
        <div class="flex items-center gap-2.5">
          <span
            aria-hidden="true"
            class="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white"
          >
            W
          </span>
          <span class="text-sm font-semibold text-slate-800">Workspace2</span>
        </div>
        <nav aria-label="主导航" class="flex flex-col gap-1">
          <RouterLink
            to="/workflows"
            active-class="bg-indigo-50 font-medium text-indigo-700"
            class="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            {{ t('nav.workflows') }}
          </RouterLink>
          <RouterLink
            to="/models"
            active-class="bg-indigo-50 font-medium text-indigo-700"
            class="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            {{ t('nav.models') }}
          </RouterLink>
          <RouterLink
            to="/users"
            active-class="bg-indigo-50 font-medium text-indigo-700"
            class="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            {{ t('nav.users') }}
          </RouterLink>
        </nav>
        <div class="mt-auto flex flex-col gap-3">
          <div class="flex items-center gap-2">
            <p class="min-w-0 flex-1 truncate text-xs text-slate-500">{{ auth.email }}</p>
            <Badge :tone="roleTone">{{ auth.role }}</Badge>
          </div>
          <Button variant="secondary" size="sm" class="w-full" @click="logout">
            {{ t('auth.logout') }}
          </Button>
        </div>
      </aside>
      <main id="main" class="mx-auto w-full max-w-5xl min-w-0 flex-1 p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Badge, type BadgeTone } from '@/packages/ui/badge'
import { Button } from '@/packages/ui/button'
import { useAuthStore } from './stores/auth'

const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()

const roleTone = computed<BadgeTone>(() => {
  if (auth.role === 'super_admin') return 'indigo'
  if (auth.role === 'admin') return 'sky'
  return 'gray'
})

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
