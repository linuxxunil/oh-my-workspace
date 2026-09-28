import axios, { type AxiosRequestConfig } from 'axios'
import { tokenHolder } from './auth-token'

// 注意：生成物 url 已含 /api 前缀（orval baseUrl: '/api'，见 orval.config.ts）。
// 因此这里**不得**再设 baseURL，否则会变成 /api/api/... 404。
const instance = axios.create()
instance.interceptors.request.use((config) => {
  const token = tokenHolder.token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function apiMutator<T>(config: AxiosRequestConfig): Promise<T> {
  return instance(config).then((res) => res.data as T)
}
export { instance as apiInstance }
