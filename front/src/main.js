import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import 'bulma/css/bulma.min.css'
import '@mdi/font/css/materialdesignicons.min.css'

createApp(App).use(router).use(createPinia()).mount('#app')
