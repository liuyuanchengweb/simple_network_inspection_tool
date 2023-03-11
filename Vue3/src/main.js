import { createApp } from 'vue'

import 'element-plus/dist/index.css'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import './styles/style.css'
import App from './App.vue'

import router from './router/index'
import store from './store/index'

createApp(App)
  .use(router)
  .use(store)
  .use(ElementPlus, {
    locale: zhCn,
  })
  .mount('#app')
