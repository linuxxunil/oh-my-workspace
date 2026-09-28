import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tokenHolder } from '../service/auth-token'

// 全局身份唯一 owner（pinia）；token 只放内存。
export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const email = ref('')
  const role = ref('')

  function setSession(next: { token: string; email: string; role: string }) {
    token.value = next.token
    tokenHolder.token = next.token
    email.value = next.email
    role.value = next.role
  }
  function logout() {
    token.value = null
    tokenHolder.token = null
    email.value = ''
    role.value = ''
  }
  return { token, email, role, setSession, logout }
})
