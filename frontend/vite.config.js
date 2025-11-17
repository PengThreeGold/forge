import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:1110',
        changeOrigin: true,
        // 重要：不要重写路径，保持原始路径
        // rewrite: (path) => path.replace(/^\/api/, '/api'),
        // 确保所有请求头都被正确转发
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 转发所有原始请求头，包括 Authorization
            const originalHeaders = req.headers;
            for (const [key, value] of Object.entries(originalHeaders)) {
              if (value !== undefined) {
                proxyReq.setHeader(key, value);
              }
            }
            console.log(`[Proxy] ${req.method} ${req.url} -> ${proxyReq.path}`);
            console.log(`[Proxy] Headers:`, originalHeaders);
          });
          
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log(`[Proxy Response] ${proxyRes.statusCode} from ${req.url}`);
          });
          
          proxy.on('error', (err, req, res) => {
            console.error(`[Proxy Error] ${err.message} for ${req.url}`);
          });
        }
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'vue-vendor': ['vue', 'vue-router', 'pinia']
        }
      }
    }
  }
})
