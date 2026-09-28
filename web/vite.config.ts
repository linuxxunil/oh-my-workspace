import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    // 本仓 api dev 端口 18081（8000 被旧仓占用，见 docker/nginx/default.conf 注）。
    // 生产/统一入口经 nginx:18080；此代理仅用于直连 5173 调试。
    proxy: {
      '/api': {
        target: 'http://localhost:18081',
        changeOrigin: true,
        // api 路由无 /api 前缀（nginx 用 proxy_pass 尾斜杠剥离）；vite 需显式 rewrite。
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
