import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { dataServiceKey } from './api/types'
import type { DataService } from './api/types'
import { mockService } from './api/mock/mockService'
import { apiService } from './api/service/apiService'
import { Logger } from './logger/logger'
import './styles/global.scss'

const source = import.meta.env.VITE_DATA_SOURCE ?? 'auto'

async function resolveDataService(): Promise<DataService> {
  if (source === 'mock') {
    Logger.info('Data source: mock (forced)')
    return mockService
  }

  if (source === 'api') {
    Logger.info('Data source: api (forced)')
    return apiService
  }

  // auto mode: try the real API first, fall back to mock
  Logger.info('Data source: auto (trying API...)')
  try {
    const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'
    const res = await fetch(`${baseURL}/health`, { signal: AbortSignal.timeout(3000) })
    if (res.ok) {
      const data = await res.json()
      Logger.info(`API health check OK — using apiService (${JSON.stringify(data)})`)
      return apiService
    }
    Logger.warn(`API health check returned ${res.status} — falling back to mock`)
  } catch (e) {
    Logger.warn(`API health check failed (${e}) — falling back to mock`)
  }

  Logger.info('Data source: mock (fallback)')
  return mockService
}

async function bootstrap() {
  const service = await resolveDataService()

  const app = createApp(App)

  app.config.errorHandler = (err, _instance, info) => {
    Logger.error(`Global error (${info})`, err)
  }

  app.use(createPinia())
  app.provide(dataServiceKey, service)
  app.mount('#app')
}

bootstrap()
