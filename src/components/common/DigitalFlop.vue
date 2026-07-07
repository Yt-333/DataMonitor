<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = withDefaults(
  defineProps<{ value: number; unit?: string; decimals?: number }>(),
  { unit: '', decimals: 0 }
)

const display = ref(0)
let raf = 0

/** Ease `display` from its current value to `target` over ~800ms. */
function animateTo(target: number): void {
  cancelAnimationFrame(raf)
  const from = display.value
  const start = performance.now()
  const duration = 800

  const step = (now: number): void => {
    const t = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - t, 3)
    display.value = from + (target - from) * eased
    if (t < 1) raf = requestAnimationFrame(step)
    else display.value = target
  }
  raf = requestAnimationFrame(step)
}

onMounted(() => animateTo(props.value))
watch(() => props.value, (v) => animateTo(v))
</script>

<template>
  <div class="flop">
    <span class="flop__value">{{ display.toFixed(decimals) }}</span>
    <span v-if="unit" class="flop__unit">{{ unit }}</span>
  </div>
</template>

<style scoped lang="scss">
@use '../../styles/tokens' as *;

.flop {
  display: flex;
  align-items: baseline;
  gap: 6px;

  &__value {
    font-size: 40px;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    letter-spacing: 1px;
    @include glow-text($cyan);
  }
  &__unit {
    font-size: 15px;
    color: $text-dim;
  }
}
</style>
