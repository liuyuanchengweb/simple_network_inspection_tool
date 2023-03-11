import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { viteMockServe } from 'vite-plugin-mock'
import viteCompression from 'vite-plugin-compression'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    viteMockServe({
      mockPath: './mock/',
      logger: true,
      prodEnabled: true,
    }),
    viteCompression({
      verbose: true,
      disable: false,
      deleteOriginFile: false,
      // 对于大于1M的文件进行压缩
      // threshold: 1024000,
      algorithm: 'gzip',
      ext: '.gz',
    }),
  ],
  build:{
    base:'./',
    outDir:'dist',
    assetsDir:'static'
  },
  server: {
    port: 19999,
    open: false,
    host: '0.0.0.0',
    // https: {
    //   // 主要是下面两行的配置文件，不要忘记引入 fs 和 path 两个对象
    //   cert: fs.readFileSync(path.join(__dirname, './cert.crt')),
    //   key: fs.readFileSync(path.join(__dirname, './cert.key')),
    // },
    proxy: {
      '/api': {
        secure: false,
        changeOrigin: true,
        target: 'http://127.0.0.1:18888/API',
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
