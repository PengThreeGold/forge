import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  // 根据当前模式加载对应的环境变量
  const env = loadEnv(mode, process.cwd(), '')

  // 解析允许的主机列表
  const allowedHosts = env.VITE_ALLOWED_HOSTS ? env.VITE_ALLOWED_HOSTS.split(',') : []

  // 判断是否为生产环境
  const isProduction = mode === 'production'

  // 代理配置
  const proxyConfig = {
    '/api': {
      target: env.VITE_API_TARGET || 'http://localhost:1110',
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

  return {
    plugins: [vue()],
    base: isProduction ? './' : '/', // 生产环境用相对路径，兼容 preview
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src')
      }
    },
    server: {
      port: env.VITE_PORT ? parseInt(env.VITE_PORT, 10) : 1112,  // 端口号
      host: env.VITE_HOST || '0.0.0.0', // 主机号，允许外部访问
      cors: true, // 启用CORS
      allowedHosts, // 允许的主机名列表
      proxy: proxyConfig
    },
    preview: {
      port: 4173,
      host: env.VITE_HOST || '0.0.0.0',
      proxy: proxyConfig
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      rollupOptions: {
        output: {
          manualChunks(id) {
            // 将 node_modules 中的包分组到 vendor chunk
            if (id.includes('node_modules')) {
              // Element Plus 单独打包
              if (id.includes('element-plus')) {
                return 'element-plus'
              }
              // Vue 生态系统单独打包
              if (id.includes('vue') || id.includes('pinia') || id.includes('@vue')) {
                return 'vue-vendor'
              }
              // 其他第三方库打包到 vendor
              return 'vendor'
            }
          }
        }
      },
      // 确保资源路径正确
      assetsInlineLimit: 4096,
      sourcemap: false
    }
  }
})
