export type AlarmLevel = 'critical' | 'major' | 'minor' | 'notice'

export interface Metrics {
  deviceCount: number
  onlineRate: number
  dailyOutput: number
  alarmCount: number
}

export interface TrendPoint {
  time: string
  output: number
  efficiency: number
}

export interface AlarmItem {
  id: string
  time: string
  area: string
  level: AlarmLevel
  message: string
}

export interface NamedValue {
  name: string
  value: number
}

export interface RadarMetric {
  name: string
  value: number
  max: number
}

export interface ChartData {
  alarmCategories: NamedValue[]
  regionalRanking: NamedValue[]
  radar: RadarMetric[]
}

export interface DataService {
  getMetrics(): Promise<Metrics>
  getTrendData(): Promise<TrendPoint[]>
  getAlarmData(): Promise<AlarmItem[]>
  getChartData(): Promise<ChartData>
}

export const dataServiceKey = Symbol('NebulaScreenDataService')
