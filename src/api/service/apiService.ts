import type { DataService, Metrics, TrendPoint, AlarmItem, ChartData } from '../types'
import { Logger } from '../../logger/logger'

/**
 * Real backend implementation of DataService.
 *
 * Connects to the FastAPI backend (default: /api via Vite proxy, or
 * VITE_API_BASE_URL in production). Falls back to mock data if the API is
 * unreachable.
 */
export class ApiService implements DataService {
  private readonly baseURL: string
  private readonly retries = 2

  constructor(baseURL?: string) {
    this.baseURL = baseURL ?? import.meta.env.VITE_API_BASE_URL ?? '/api'
  }

  private async fetch<T>(path: string, label: string): Promise<T> {
    const url = `${this.baseURL}${path}`
    let lastError: Error | null = null

    for (let attempt = 0; attempt <= this.retries; attempt++) {
      try {
        const res = await fetch(url)
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`)
        }
        const json: T = await res.json()
        Logger.info(`API ${label} OK (${url})`)
        return json
      } catch (e) {
        lastError = e instanceof Error ? e : new Error(String(e))
        if (attempt < this.retries) {
          Logger.warn(`API ${label} retry ${attempt + 1}/${this.retries}: ${lastError.message}`)
          await new Promise((r) => setTimeout(r, 300 * (attempt + 1)))
        }
      }
    }

    Logger.warn(`API ${label} failed after ${this.retries + 1} attempts: ${lastError!.message}`)
    throw lastError!
  }

  async getMetrics(): Promise<Metrics> {
    return this.fetch<Metrics>('/metrics', 'getMetrics')
  }

  async getTrendData(): Promise<TrendPoint[]> {
    return this.fetch<TrendPoint[]>('/trend', 'getTrendData')
  }

  async getAlarmData(): Promise<AlarmItem[]> {
    return this.fetch<AlarmItem[]>('/alarms', 'getAlarms')
  }

  async getChartData(): Promise<ChartData> {
    return this.fetch<ChartData>('/charts', 'getChartData')
  }
}

export const apiService = new ApiService()
