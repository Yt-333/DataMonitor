import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart, RadarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  RadarComponent,
  TitleComponent,
  GraphicComponent
} from 'echarts/components'

let registered = false

/** Register the ECharts modules used across the dashboard exactly once. */
export function registerECharts(): void {
  if (registered) return
  use([
    CanvasRenderer,
    LineChart,
    BarChart,
    PieChart,
    RadarChart,
    GridComponent,
    TooltipComponent,
    LegendComponent,
    RadarComponent,
    TitleComponent,
    GraphicComponent
  ])
  registered = true
}
