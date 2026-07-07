import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { dataServiceKey } from './api/types'
import type { DataService } from './api/types'
import { mockService } from './api/mock/mockService'
import { apiService } from './api/service/apiService'
import { Logger } from './logger/logger'
import './styles/global.scss'

const source = import.meta.env.VITE_DATA_SOURCE ?? 'mock'
const dataService: DataService = source === 'api' ? apiService : mockService
Logger.info(`Data source: ${source}`)

const app = createApp(App)

app.config.errorHandler = (err, _instance, info) => {
  Logger.error(`Global error (${info})`, err)
}

app.use(createPinia())
app.provide(dataServiceKey, dataService)
app.mount('#app')
