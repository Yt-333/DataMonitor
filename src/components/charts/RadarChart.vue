<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import BaseChart from './BaseChart.vue'
import { chartBase, PALETTE } from './chartTheme'
import type { RadarMetric } from '../../api/types'

const props = defineProps<{ data: RadarMetric[] }>()

const option = computed<EChartsOption>(() => ({
  ...chartBase,
  tooltip: { ...chartBase.tooltip },
  radar: {
    center: ['50%', '54%'],
    radius: '66%',
    indicator: props.data.map((d) => ({ name: d.name, max: d.max })),
    axisName: { color: PALETTE.text, fontSize: 12 },
    splitLine: { lineStyle: { color: PALETTE.grid } },
    splitArea: { areaStyle: { color: ['rgba(0,240,255,0.03)', 'rgba(168,85,247,0.03)'] } },
    axisLine: { lineStyle: { color: PALETTE.grid } }
  },
  series: [
    {
      type: 'radar',
      data: [
        {
          value: props.data.map((d) => d.value),
          name: '综合评分',
          symbolSize: 5,
          lineStyle: { color: PALETTE.cyan, width: 2 },
          itemStyle: { color: PALETTE.cyan },
          areaStyle: { color: 'rgba(0,240,255,0.22)' }
        }
      ]
    }
  ]
}))
</script>

<template>
  <BaseChart :option="option" />
</template>
