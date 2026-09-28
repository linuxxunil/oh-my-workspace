import axios, { type AxiosRequestConfig } from 'axios'

let token: string | null = null

/** API 身份（准备/清理用），与浏览器身份分开管理。 */
export function setApiToken(t: string | null): void {
  token = t
}

// 注意：生成物 url 已含 /api 前缀（orval baseUrl），baseURL 只放 origin，
// 不得再加 /api，否则变成 /api/api/...（见 web 侧同类事故）。
const instance = axios.create({ baseURL: process.env.E2E_BASE ?? 'http://localhost:18080' })
instance.interceptors.request.use((config) => {
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function apiMutator<T>(config: AxiosRequestConfig): Promise<T> {
  return instance(config).then((res) => res.data as T)
}
