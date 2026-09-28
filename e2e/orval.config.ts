import { defineConfig } from 'orval'

// e2e 生成式客户端：普通 axios（非 vue-query），url 已含 /api 前缀（baseUrl），
// 传输层见 src/support/http.ts（baseURL 只放 origin，不叠加 /api）。
export default defineConfig({
  api: {
    input: '../web/openapi.json',
    output: {
      target: './src/generated/api.ts',
      client: 'axios',
      baseUrl: '/api',
      override: {
        mutator: { path: './src/support/http.ts', name: 'apiMutator' },
      },
    },
  },
})
