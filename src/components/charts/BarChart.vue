<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import { graphic } from 'echarts/core'
import BaseChart from './BaseChart.vue'
import { chartBase, PALETTE } from './chartTheme'
import type { NamedValue } from '../../api/types'

const props = defineProps<{ data: NamedValue[] }>()

const option = computed<EChartsOption>(() => ({
  ...chartBase,
  grid: { left: 70, right: 30, top: 16, bottom: 20 },
  tooltip: { ...chartBase.tooltip, trigger: 'axis', axisPointer: { type: 'shadow' } },
  xAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: PALETTE.grid } },
    axisLabel: { color: PALETTE.textDim, fontSize: 11 }
  },
  yAxis: {
    type: 'category',
    inverse: true,
    data: props.data.map((d) => d.name),
    axisLine: { lineStyle: { color: PALETTE.grid } },
    axisTick: { show: false },
    axisLabel: { color: PALETTE.text, fontSize: 12 }
  },
  series: [
    {
      type: 'bar',
      barWidth: 12,
      data: props.data.map((d) => d.value),
      label: { show: true, position: 'right', color: PALETTE.textDim, fontSize: 11 },
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: new graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: PALETTE.nebulaBlue },
          { offset: 1, color: PALETTE.purple }
        ])
      }
    }
  ]
}))
</script>

<template>
  <BaseChart :option="option" />
</template>
