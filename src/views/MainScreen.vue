<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useScreenStore } from '../stores/screenStore'
import { useScreenAdapt } from '../composables/useScreenAdapt'
import { usePolling } from '../composables/usePolling'
import { useDataService } from '../composables/useDataService'
import BorderBox from '../components/common/BorderBox.vue'
import DigitalFlop from '../components/common/DigitalFlop.vue'
import Loading from '../components/common/Loading.vue'
import AlarmScroll from '../components/common/AlarmScroll.vue'
import LineChart from '../components/charts/LineChart.vue'
import BarChart from '../components/charts/BarChart.vue'
import PieChart from '../components/charts/PieChart.vue'
import RadarChart from '../components/charts/RadarChart.vue'

const store = useScreenStore()
const { metrics, trendData, alarmList, chartData, loading, hasLoadedOnce } = storeToRefs(store)
const { style } = useScreenAdapt()
// Resolve the DataService once, inside setup, so polling can run outside inject().
const dataService = useDataService()

const REFRESH_MS = 5000

// Live clock, updated every second.
const now = ref(new Date())
let clockTimer = 0
function pad(n: number): string {
  return String(n).padStart(2, '0')
}
const clock = computed(
  () => `${pad(now.value.getHours())}:${pad(now.value.getMinutes())}:${pad(now.value.getSeconds())}`
)
const dateLabel = computed(
  () => `${now.value.getFullYear()}-${pad(now.value.getMonth() + 1)}-${pad(now.value.getDate())}`
)

const flops = computed(() => [
  { label: '设备总数', value: metrics.value?.deviceCount ?? 0, unit: '台', decimals: 0 },
  { label: '在线率', value: metrics.value?.onlineRate ?? 0, unit: '%', decimals: 2 },
  { label: '今日产量', value: metrics.value?.dailyOutput ?? 0, unit: '件', decimals: 0 },
  { label: '告警数量', value: metrics.value?.alarmCount ?? 0, unit: '条', decimals: 0 }
])

onMounted(() => {
  void store.fetchAllData(dataService)
  clockTimer = window.setInterval(() => (now.value = new Date()), 1000)
})
onUnmounted(() => window.clearInterval(clockTimer))

usePolling(() => store.fetchAllData(dataService), REFRESH_MS)
</script>

<template>
  <div class="nebula-backdrop" />
  <div class="stage" :style="style">
    <Loading v-if="loading && !hasLoadedOnce" />

    <header class="topbar">
      <div class="topbar__side topbar__side--left">
        <span class="status">
          <span class="status__dot" />
          系统正常
        </span>
      </div>
      <h1 class="title">
        NebulaScreen<span class="title__sub">星云数据驾驶舱</span>
      </h1>
      <div class="topbar__side topbar__side--right">
        <span class="clock">{{ clock }}</span>
        <span class="date">{{ dateLabel }}</span>
      </div>
    </header>

    <main class="grid">
      <!-- Left: KPI stack -->
      <div class="col-left">
        <BorderBox
          v-for="f in flops"
          :key="f.label"
          :title="f.label"
          class="kpi"
        >
          <DigitalFlop :value="f.value" :unit="f.unit" :decimals="f.decimals" />
        </BorderBox>
      </div>

      <!-- Center -->
      <div class="col-center">
        <BorderBox title="24 小时产量 · 效率趋势" class="panel panel--trend">
          <LineChart :data="trendData" />
        </BorderBox>
        <div class="center-bottom">
          <BorderBox title="告警分类占比" class="panel">
            <PieChart v-if="chartData" :data="chartData.alarmCategories" />
          </BorderBox>
          <BorderBox title="综合运行评分" class="panel">
            <RadarChart v-if="chartData" :data="chartData.radar" />
          </BorderBox>
        </div>
      </div>

      <!-- Right: regional ranking -->
      <div class="col-right">
        <BorderBox title="区域生产排行" class="panel panel--rank">
          <BarChart v-if="chartData" :data="chartData.regionalRanking" />
        </BorderBox>
      </div>
    </main>

    <footer class="footer">
      <BorderBox title="实时告警流" class="panel panel--alarm">
        <AlarmScroll :items="alarmList" />
      </BorderBox>
    </footer>
  </div>
</template>

<style scoped lang="scss">
@use '../styles/tokens' as *;

.stage {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px 22px 18px;
}

// ── Top bar ──────────────────────────────
.topbar {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  height: 68px;
  border-bottom: 1px solid rgba($cyan, 0.18);
}

.title {
  font-size: 34px;
  font-weight: 700;
  letter-spacing: 6px;
  text-align: center;
  @include glow-text($cyan);

  &__sub {
    margin-left: 16px;
    font-size: 16px;
    letter-spacing: 4px;
    color: $text-dim;
    text-shadow: none;
  }
}

.topbar__side {
  display: flex;
  align-items: center;
  gap: 16px;

  &--left {
    justify-self: start;
  }
  &--right {
    justify-self: end;
    flex-direction: column;
    align-items: flex-end;
    gap: 2px;
  }
}

.status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border: 1px solid rgba($notice, 0.4);
  border-radius: 4px;
  color: $notice;
  letter-spacing: 2px;

  &__dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: $notice;
    box-shadow: 0 0 10px $notice;
    animation: blink 1.6s ease-in-out infinite;
  }
}

.clock {
  font-size: 26px;
  font-variant-numeric: tabular-nums;
  @include glow-text($text);
}
.date {
  font-size: 13px;
  color: $text-dim;
}

// ── Grid ─────────────────────────────────
.grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 360px 1fr 420px;
  gap: 14px;
}

.col-left {
  display: grid;
  grid-template-rows: repeat(4, 1fr);
  gap: 14px;
}

.kpi :deep(.border-box__body) {
  display: flex;
  align-items: center;
}

.col-center {
  display: grid;
  grid-template-rows: 1.15fr 1fr;
  gap: 14px;
  min-height: 0;
}

.center-bottom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  min-height: 0;
}

.col-right {
  min-height: 0;
}

.panel {
  min-height: 0;
}

.footer {
  height: 168px;
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.35;
  }
}
</style>
