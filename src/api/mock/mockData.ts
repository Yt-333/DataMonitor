import type {
  Metrics,
  TrendPoint,
  AlarmItem,
  ChartData,
  AlarmLevel,
  NamedValue,
  RadarMetric
} from '../types'

/** Return `base` with a random ±`pct` fractional wobble applied. */
function wobble(base: number, pct: number): number {
  return base * (1 + (Math.random() * 2 - 1) * pct)
}

function pick<T>(list: readonly T[]): T {
  return list[Math.floor(Math.random() * list.length)]
}

export function generateMetrics(): Metrics {
  return {
    deviceCount: 1280 + Math.floor(Math.random() * 20 - 10),
    onlineRate: Number((99.2 + (Math.random() * 0.6 - 0.3)).toFixed(2)),
    dailyOutput: 8745 + Math.floor(Math.random() * 200 - 100),
    alarmCount: Math.floor(Math.random() * 15)
  }
}

export function generateTrendData(): TrendPoint[] {
  const points: TrendPoint[] = []
  for (let hour = 0; hour < 24; hour++) {
    // Production follows a daytime bell curve peaking around midday.
    const shape = Math.sin((hour / 23) * Math.PI)
    const baseOutput = 180 + shape * 420
    points.push({
      time: `${String(hour).padStart(2, '0')}:00`,
      output: Math.round(wobble(baseOutput, 0.05)),
      efficiency: Number(wobble(72 + shape * 20, 0.05).toFixed(1))
    })
  }
  return points
}

const AREAS = ['一号车间', '二号车间', '三号车间', '装配中心', '质检区', '仓储区', '动力站']
const LEVELS: AlarmLevel[] = ['critical', 'major', 'minor', 'notice']
const MESSAGES: Record<AlarmLevel, string[]> = {
  critical: ['主轴温度超限，已触发急停', '电压骤降至安全阈值以下', '气压系统压力异常'],
  major: ['产线节拍偏离目标值', '机械臂定位偏差超标', '冷却液流量不足'],
  minor: ['传感器信号轻微抖动', '待料时间高于均值', '刀具磨损接近阈值'],
  notice: ['计划维护提醒', '批次切换完成', '班次交接已确认']
}

export function generateAlarmData(): AlarmItem[] {
  const now = Date.now()
  return Array.from({ length: 10 }, (_, i) => {
    const level = pick(LEVELS)
    const t = new Date(now - i * 1000 * 60 * pick([2, 3, 5, 7, 11]))
    return {
      id: `ALM-${(now - i * 137).toString(36).toUpperCase()}`,
      time: `${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}:${String(t.getSeconds()).padStart(2, '0')}`,
      area: pick(AREAS),
      level,
      message: pick(MESSAGES[level])
    }
  })
}

export function generateChartData(): ChartData {
  const alarmCategories: NamedValue[] = [
    { name: '设备故障', value: Math.round(wobble(38, 0.1)) },
    { name: '工艺偏差', value: Math.round(wobble(26, 0.1)) },
    { name: '环境异常', value: Math.round(wobble(18, 0.1)) },
    { name: '网络中断', value: Math.round(wobble(11, 0.1)) },
    { name: '其他', value: Math.round(wobble(7, 0.1)) }
  ]

  const regionalRanking: NamedValue[] = AREAS.slice(0, 6)
    .map((name) => ({ name, value: Math.round(wobble(1400, 0.08)) }))
    .sort((a, b) => b.value - a.value)

  const radar: RadarMetric[] = [
    { name: '产能', value: Number(wobble(88, 0.05).toFixed(1)), max: 100 },
    { name: '质量', value: Number(wobble(92, 0.05).toFixed(1)), max: 100 },
    { name: '能效', value: Number(wobble(79, 0.05).toFixed(1)), max: 100 },
    { name: '稳定性', value: Number(wobble(85, 0.05).toFixed(1)), max: 100 },
    { name: '安全', value: Number(wobble(94, 0.05).toFixed(1)), max: 100 },
    { name: '交付', value: Number(wobble(81, 0.05).toFixed(1)), max: 100 }
  ]

  return { alarmCategories, regionalRanking, radar }
}
