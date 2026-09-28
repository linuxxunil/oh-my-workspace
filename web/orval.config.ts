import { defineConfig } from 'orval'

export default defineConfig({
  api: {
    input: './openapi.json',
    output: {
      target: './src/service/generated/api.ts',
      client: 'vue-query',
      httpClient: 'axios',
      baseUrl: '/api',
      override: {
        mutator: { path: './src/service/mutator.ts', name: 'apiMutator' },
      },
    },
  },
})
