import { createApp } from 'vue'
import { createPinia } from 'pinia'
import "bootstrap/dist/css/bootstrap.css"
import "bootstrap-icons/font/bootstrap-icons.min.css"
import "bootstrap/dist/js/bootstrap.bundle.min.js"
import axios from 'axios'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

axios.defaults.baseURL = 'http://localhost:8000'
axios.defaults.withCredentials = true

app.use(pinia)
app.use(router)

app.mount('#app')
