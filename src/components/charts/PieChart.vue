<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import BaseChart from './BaseChart.vue'
import { chartBase, PALETTE } from './chartTheme'
import type { NamedValue } from '../../api/types'

const props = defineProps<{ data: NamedValue[] }>()

const total = computed(() => props.data.reduce((sum, d) => sum + d.value, 0))

const option = computed<EChartsOption>(() => ({
  ...chartBase,
  tooltip: { ...chartBase.tooltip, trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: {
    orient: 'vertical',
    right: 8,
    top: 'center',
    textStyle: { color: PALETTE.textDim, fontSize: 12 },
    itemWidth: 10,
    itemHeight: 10
  },
  graphic: [
    {
      type: 'text',
      left: '32%',
      top: '42%',
      style: { text: String(total.value), fill: PALETTE.cyan, fontSize: 30, fontWeight: 700 }
    },
    {
      type: 'text',
      left: '30%',
      top: '58%',
      style: { text: '总告警数', fill: PALETTE.textDim, fontSize: 12 }
    }
  ],
  series: [
    {
      type: 'pie',
      radius: ['52%', '74%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      label: { show: false },
      labelLine: { show: false },
      itemStyle: { borderColor: '#080d20', borderWidth: 2 },
      data: props.data.map((d) => ({ name: d.name, value: d.value }))
    }
  ]
}))
</script>

<template>
  <BaseChart :option="option" />
</template>
