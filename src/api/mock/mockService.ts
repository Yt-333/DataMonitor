import type { DataService, Metrics, TrendPoint, AlarmItem, ChartData } from '../types'
import {
  generateMetrics,
  generateTrendData,
  generateAlarmData,
  generateChartData
} from './mockData'
import { Logger } from '../../logger/logger'

const MIN_DELAY = 300
const MAX_DELAY = 800
const FAILURE_RATE = 0.05

/** Resolve `value` after a random 300–800ms delay, or reject ~5% of the time. */
function withLatency<T>(value: () => T, label: string): Promise<T> {
  const delay = MIN_DELAY + Math.random() * (MAX_DELAY - MIN_DELAY)
  return new Promise<T>((resolve, reject) => {
    setTimeout(() => {
      if (Math.random() < FAILURE_RATE) {
        Logger.warn(`Mock request failed: ${label}`)
        reject(new Error('Mock request failed'))
        return
      }
      resolve(value())
    }, delay)
  })
}

/** DataService backed entirely by locally generated mock data. */
export class MockService implements DataService {
  getMetrics(): Promise<Metrics> {
    return withLatency(generateMetrics, 'getMetrics')
  }

  getTrendData(): Promise<TrendPoint[]> {
    return withLatency(generateTrendData, 'getTrendData')
  }

  getAlarmData(): Promise<AlarmItem[]> {
    return withLatency(generateAlarmData, 'getAlarmData')
  }

  getChartData(): Promise<ChartData> {
    return withLatency(generateChartData, 'getChartData')
  }
}

export const mockService = new MockService()
