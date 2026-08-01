import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import '@fortawesome/fontawesome-free/css/all.min.css'

import App from './App.vue'
import router from './router'
import i18n from './locales/i18n'
import { useBusinessStore } from '@/stores/business'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(i18n)

app.config.globalProperties.$storeLink = (path) => useBusinessStore().link(path)

app.mount('#app')
