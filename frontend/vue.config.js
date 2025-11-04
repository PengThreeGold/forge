const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api',
        },
      },
    },
  },
  // 生产环境配置
  // 部署应用包时的基本URL
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  // 输出文件目录
  outputDir: 'dist',
  // 静态资源目录
  assetsDir: 'static',
  // 生产环境是否生成 sourceMap 文件
  productionSourceMap: false,
  // 配置webpack
  configureWebpack: {
    // 性能提示
    performance: {
      hints: false,
    },
    // 优化
    optimization: {
      splitChunks: {
        chunks: 'all',
      },
    },
    resolve: {
      alias: {
        // 解决字体资源加载问题
        'fonts': '@/assets/fonts'
      }
    }
  },
  // CSS相关配置
  css: {
    // 是否将组件中的CSS提取到独立的CSS文件中
    extract: process.env.NODE_ENV === 'production',
    // 是否为CSS开启source map
    sourceMap: false,
  },
  // 链式webpack配置
  chainWebpack: config => {
    // 优化字体资源加载
    config.module
      .rule('fonts')
      .test(/\.(woff2?|eot|ttf|otf)$/)
      .use('url-loader')
      .loader('url-loader')
      .options({
        limit: 10000,
        name: 'fonts/[name].[hash:7].[ext]'
      })
      .end()
  }
})
