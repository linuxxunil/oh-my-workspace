import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    // '@/packages/ui/*' 命中基元源码 packages/ui/src/*（子路径见 packages/ui/README.md），'@/*' 仍指 web/src。
    alias: [
      { find: '@/packages/ui', replacement: fileURLToPath(new URL('../packages/ui/src', import.meta.url)) },
      { find: '@', replacement: fileURLToPath(new URL('./src', import.meta.url)) },
    ],
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    // ui 基元源码在仓根 packages/（root 之外），dev 与 vitest 均需放行。
    fs: { allow: [fileURLToPath(new URL('..', import.meta.url))] },
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
