<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import { graphic } from 'echarts/core'
import BaseChart from './BaseChart.vue'
import { chartBase, PALETTE } from './chartTheme'
import type { TrendPoint } from '../../api/types'

const props = defineProps<{ data: TrendPoint[] }>()

const option = computed<EChartsOption>(() => ({
  ...chartBase,
  grid: { left: 46, right: 24, top: 34, bottom: 30 },
  legend: {
    data: ['产量', '效率'],
    top: 2,
    right: 8,
    textStyle: { color: PALETTE.textDim },
    itemWidth: 14,
    itemHeight: 8
  },
  tooltip: { ...chartBase.tooltip, trigger: 'axis' },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: props.data.map((p) => p.time),
    axisLine: { lineStyle: { color: PALETTE.grid } },
    axisLabel: { color: PALETTE.textDim, fontSize: 11, interval: 3 }
  },
  yAxis: [
    {
      type: 'value',
      splitLine: { lineStyle: { color: PALETTE.grid } },
      axisLabel: { color: PALETTE.textDim, fontSize: 11 }
    },
    {
      type: 'value',
      max: 100,
      splitLine: { show: false },
      axisLabel: { color: PALETTE.textDim, fontSize: 11, formatter: '{value}%' }
    }
  ],
  series: [
    {
      name: '产量',
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: props.data.map((p) => p.output),
      lineStyle: { width: 2.5, color: PALETTE.cyan, shadowBlur: 12, shadowColor: PALETTE.cyan },
      areaStyle: {
        color: new graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0,240,255,0.35)' },
          { offset: 1, color: 'rgba(0,240,255,0.02)' }
        ])
      }
    },
    {
      name: '效率',
      type: 'line',
      yAxisIndex: 1,
      smooth: true,
      showSymbol: false,
      data: props.data.map((p) => p.efficiency),
      lineStyle: { width: 2, color: PALETTE.purple, shadowBlur: 10, shadowColor: PALETTE.purple }
    }
  ]
}))
</script>

<template>
  <BaseChart :option="option" />
</template>
