import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DataService, Metrics, TrendPoint, AlarmItem, ChartData } from '../api/types'
import { useDataService } from '../composables/useDataService'
import { Logger } from '../logger/logger'

export const useScreenStore = defineStore('screen', () => {
  const metrics = ref<Metrics | null>(null)
  const trendData = ref<TrendPoint[]>([])
  const alarmList = ref<AlarmItem[]>([])
  const chartData = ref<ChartData | null>(null)
  const loading = ref(false)
  const hasLoadedOnce = ref(false)

  /** Concurrently fetch every dataset and update state. Failures are logged. */
  async function fetchAllData(dataService: DataService): Promise<void> {
    if (!hasLoadedOnce.value) loading.value = true
    try {
      const [m, t, a, c] = await Promise.all([
        dataService.getMetrics(),
        dataService.getTrendData(),
        dataService.getAlarmData(),
        dataService.getChartData()
      ])
      metrics.value = m
      trendData.value = t
      alarmList.value = a
      chartData.value = c
      hasLoadedOnce.value = true
      Logger.info('Screen data refreshed')
    } catch (err) {
      Logger.error('Failed to fetch screen data', err)
    } finally {
      loading.value = false
    }
  }

  /** Refresh using the injected DataService — call from within setup(). */
  function refreshData(): Promise<void> {
    const service = useDataService()
    return fetchAllData(service)
  }

  return {
    metrics,
    trendData,
    alarmList,
    chartData,
    loading,
    hasLoadedOnce,
    fetchAllData,
    refreshData
  }
})
