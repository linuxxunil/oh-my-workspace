<template>
  <div class="min-h-screen bg-surface text-slate-800">
    <a class="skip-link" href="#main">{{ t('app.skip') }}</a>
    <header
      v-if="auth.token"
      class="sticky top-0 z-40 h-16 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur"
    >
      <div class="mx-auto flex h-full max-w-[100rem] items-center gap-3 px-4 sm:px-6">
        <Drawer v-model:open="mobileNavOpen" :label="t('nav.primary')" side="left">
          <template #trigger="{ triggerProps }">
            <button
              v-bind="triggerProps"
              :aria-label="t('nav.openNavigation')"
              class="inline-flex size-9 shrink-0 items-center justify-center rounded-lg text-slate-600 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40 md:hidden"
            >
              <span aria-hidden="true" class="text-lg leading-none">☰</span>
            </button>
          </template>
          <template #default="{ close }">
            <div class="flex items-center justify-between border-b border-slate-200 p-4">
              <div class="flex items-center gap-2.5">
                <span
                  aria-hidden="true"
                  class="flex size-9 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white"
                >
                  W
                </span>
                <span class="text-sm font-semibold">Workspace2</span>
              </div>
              <button
                type="button"
                class="inline-flex size-9 items-center justify-center rounded-lg text-slate-600 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
                :aria-label="t('nav.closeNavigation')"
                @click="close()"
              >
                <span aria-hidden="true" class="text-xl leading-none">×</span>
              </button>
            </div>
            <nav :aria-label="t('nav.primary')" class="flex flex-col gap-1 p-3">
              <RouterLink
                v-for="item in navItems"
                :key="item.to"
                :to="item.to"
                active-class="bg-indigo-50 font-medium text-indigo-700"
                class="rounded-lg px-3 py-2.5 text-sm text-slate-700 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
                @click="close(false)"
              >
                {{ t(item.label) }}
              </RouterLink>
            </nav>
          </template>
        </Drawer>
        <span
          aria-hidden="true"
          class="flex size-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white"
        >
          W
        </span>
        <span class="min-w-0 flex-1 truncate text-sm font-semibold text-slate-800">Workspace2</span>
        <DropdownMenu :label="t('nav.userActions')">
          <template #trigger="{ triggerProps }">
            <button
              v-bind="triggerProps"
              class="flex max-w-64 items-center gap-2 rounded-xl px-2 py-1.5 text-left hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40 sm:px-3"
            >
              <span
                aria-hidden="true"
                class="flex size-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-800"
              >
                {{ userInitial }}
              </span>
              <span class="hidden min-w-0 text-left sm:block">
                <span class="block truncate text-xs font-medium text-slate-800">{{ auth.email }}</span>
                <span class="block truncate text-[11px] text-slate-600">{{ auth.role }}</span>
              </span>
              <span class="block max-w-24 truncate text-[11px] text-slate-700 sm:hidden">
                {{ auth.email }}
              </span>
              <span aria-hidden="true" class="text-xs text-slate-500">⌄</span>
            </button>
          </template>
          <template #default="{ close }">
            <RouterLink
              to="/account"
              role="menuitem"
              class="block rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-100 focus-visible:bg-slate-100 focus-visible:outline-none"
              @click="close()"
            >
              {{ t('account.change') }}
            </RouterLink>
            <button
              type="button"
              role="menuitem"
              class="block w-full rounded-lg px-3 py-2 text-left text-sm text-red-700 hover:bg-red-50 focus-visible:bg-red-50 focus-visible:outline-none"
              @click="logout"
            >
              {{ t('auth.logout') }}
            </button>
          </template>
        </DropdownMenu>
      </div>
    </header>

    <div class="mx-auto flex min-h-[calc(100vh-4rem)] max-w-[100rem]">
      <aside
        v-if="auth.token"
        class="sticky top-16 hidden h-[calc(100vh-4rem)] shrink-0 flex-col border-r border-slate-200 bg-white p-3 transition-[width] duration-200 md:flex"
        :class="collapsed ? 'w-16' : 'w-60'"
      >
        <nav :aria-label="t('nav.primary')" class="flex flex-col gap-1">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            active-class="bg-indigo-50 font-medium text-indigo-700"
            class="flex min-h-10 items-center rounded-lg text-sm text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
            :class="collapsed ? 'justify-center px-1' : 'gap-3 px-3'"
            :aria-label="collapsed ? t(item.label) : undefined"
            :title="collapsed ? t(item.label) : undefined"
          >
            <span
              aria-hidden="true"
              class="flex size-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-xs font-bold text-slate-700"
            >
              {{ item.mark }}
            </span>
            <span v-if="!collapsed" class="truncate">{{ t(item.label) }}</span>
          </RouterLink>
        </nav>
        <div class="mt-auto pt-3">
          <button
            type="button"
            class="flex min-h-10 w-full items-center rounded-lg text-sm text-slate-600 hover:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
            :class="collapsed ? 'justify-center px-1' : 'gap-3 px-3'"
            :aria-label="t(collapsed ? 'nav.expandSidebar' : 'nav.collapseSidebar')"
            :aria-expanded="!collapsed"
            @click="toggleCollapsed"
          >
            <span aria-hidden="true" class="text-lg leading-none">{{ collapsed ? '›' : '‹' }}</span>
            <span v-if="!collapsed" class="truncate">{{ t('nav.collapseSidebar') }}</span>
          </button>
        </div>
      </aside>
      <main id="main" class="mx-auto w-full min-w-0 flex-1 p-4 sm:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { DropdownMenu, Drawer } from '@/packages/ui/overlay'
import { useAuthStore } from './stores/auth'

const COLLAPSED_KEY = 'workspace2.navigation.collapsed'
const { t } = useI18n()
const router = useRouter()
const auth = useAuthStore()
const collapsed = ref(localStorage.getItem(COLLAPSED_KEY) === 'true')
const mobileNavOpen = ref(false)

const navItems = [
  { to: '/workflows', label: 'nav.workflows', mark: 'W' },
  { to: '/models', label: 'nav.models', mark: 'M' },
  { to: '/users', label: 'nav.users', mark: 'U' },
] as const

const userInitial = computed(() => auth.email.trim().charAt(0).toUpperCase() || '?')
function toggleCollapsed() {
  collapsed.value = !collapsed.value
  localStorage.setItem(COLLAPSED_KEY, String(collapsed.value))
}

function logout() {
  auth.logout()
  mobileNavOpen.value = false
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
  z-index: 70;
}
</style>
