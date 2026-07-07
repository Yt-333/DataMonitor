import type { DataService, Metrics, TrendPoint, AlarmItem, ChartData } from '../types'

/**
 * Real backend implementation of DataService.
 *
 * The backend is not connected yet, so every method throws. When the API is
 * ready, replace each `throw` with the commented request code below. Business
 * components and the store consume `DataService` and need no changes — only
 * `VITE_DATA_SOURCE=api` in the environment switches to this implementation.
 */
export class ApiService implements DataService {
  // private readonly baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

  async getMetrics(): Promise<Metrics> {
    // return fetch(`${this.baseURL}/metrics`).then((r) => r.json() as Promise<Metrics>)
    throw new Error('API not connected yet')
  }

  async getTrendData(): Promise<TrendPoint[]> {
    // return fetch(`${this.baseURL}/trend`).then((r) => r.json() as Promise<TrendPoint[]>)
    throw new Error('API not connected yet')
  }

  async getAlarmData(): Promise<AlarmItem[]> {
    // return fetch(`${this.baseURL}/alarms`).then((r) => r.json() as Promise<AlarmItem[]>)
    throw new Error('API not connected yet')
  }

  async getChartData(): Promise<ChartData> {
    // return fetch(`${this.baseURL}/charts`).then((r) => r.json() as Promise<ChartData>)
    throw new Error('API not connected yet')
  }
}

export const apiService = new ApiService()
