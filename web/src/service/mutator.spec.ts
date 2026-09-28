import { describe, expect, it, beforeEach } from 'vitest'
import type { AxiosRequestConfig, AxiosResponse } from 'axios'
import { apiInstance } from './mutator'
import { loginAuthLoginPost, listUsersUsersGet } from './generated/api'
import { tokenHolder } from './auth-token'

// 回归说明：曾经 orval baseUrl:'/api' 与 axios baseURL:'/api' 叠加，导致浏览器请求
// /api/api/auth/login（404），页面只显示通用红字。此测试锁死"生成物 url 与传输层前缀只有一份"。
// 增量证据：捕获 mutator 实际发出的 config.url，断言为单 /api 前缀且非 /api/api。
describe('api mutator URL 契约', () => {
  const captured: { url?: string; auth?: unknown }[] = []

  beforeEach(() => {
    captured.length = 0
    tokenHolder.token = null
    apiInstance.defaults.adapter = async (config: AxiosRequestConfig) => {
      // 有效 URL = baseURL + url（axios 在 adapter 前不合并，必须自行组合才能捕获双前缀）。
      const effective = `${config.baseURL ?? ''}${config.url ?? ''}`
      captured.push({
        url: effective,
        auth: (config.headers as Record<string, unknown> | undefined)?.Authorization,
      })
      return {
        data: {},
        status: 200,
        statusText: 'OK',
        headers: {},
        config,
      } as AxiosResponse
    }
  })

  it('登录请求是单 /api 前缀，不得 /api/api 双前缀', async () => {
    await loginAuthLoginPost({ email: 'root@example.com', password: 'Root12345' })
    expect(captured[0]?.url).toBe('/api/auth/login')
    expect(captured[0]?.url?.startsWith('/api/api')).toBe(false)
  })

  it('列表请求同样单前缀', async () => {
    await listUsersUsersGet()
    expect(captured[0]?.url).toBe('/api/users')
  })

  it('有 token 时自动带 Authorization 头', async () => {
    tokenHolder.token = 'tok-123'
    await listUsersUsersGet()
    expect(captured[0]?.auth).toBe('Bearer tok-123')
  })
})
