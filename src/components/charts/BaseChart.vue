<script setup lang="ts">
import VChart from 'vue-echarts'
import type { EChartsOption } from 'echarts'
import { registerECharts } from './echartsSetup'

registerECharts()

defineProps<{ option: EChartsOption }>()
</script>

<template>
  <div class="base-chart">
    <VChart class="chart" :option="option" autoresize />
  </div>
</template>

<style scoped lang="scss">
.base-chart {
  width: 100%;
  height: 100%;
}
.chart {
  width: 100%;
  height: 100%;
}
</style>
