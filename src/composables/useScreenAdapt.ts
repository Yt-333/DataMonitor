import { computed, onMounted, onUnmounted, ref, type CSSProperties } from 'vue'

/**
 * Design resolution (1920×1080) — the baseline the layout was authored against.
 * The stage is scaled to fit the viewport while maintaining aspect ratio.
 *
 * Mobile (width < 768): switches to a stacked responsive layout — no transform
 * scaling. Call isMobile() to branch in templates.
 */
const DESIGN_W = 1920
const DESIGN_H = 1080
const MOBILE_BREAKPOINT = 768

const viewW = ref(window.innerWidth)
const viewH = ref(window.innerHeight)
let resizeTimer = 0

function onResize() {
  viewW.value = window.innerWidth
  viewH.value = window.innerHeight
}

function debouncedResize() {
  window.clearTimeout(resizeTimer)
  resizeTimer = window.setTimeout(onResize, 120)
}

onMounted(() => window.addEventListener('resize', debouncedResize))
onUnmounted(() => {
  window.removeEventListener('resize', debouncedResize)
  window.clearTimeout(resizeTimer)
})

/** Whether the viewport is in mobile range. */
export function isMobile(): boolean {
  return viewW.value < MOBILE_BREAKPOINT
}

export function useScreenAdapt() {
  const style = computed<CSSProperties>(() => {
    if (isMobile()) {
      return {
        width: '100%',
        height: '100%',
      }
    }

    const scaleX = viewW.value / DESIGN_W
    const scaleY = viewH.value / DESIGN_H
    const scale = Math.min(scaleX, scaleY)

    const offsetX = (viewW.value - DESIGN_W * scale) / 2
    const offsetY = (viewH.value - DESIGN_H * scale) / 2

    return {
      width: `${DESIGN_W}px`,
      height: `${DESIGN_H}px`,
      transform: `translate(${offsetX}px, ${offsetY}px) scale(${scale})`,
      transformOrigin: 'top left',
    }
  })

  const isMobileStyle = computed(() => isMobile())

  return { style, isMobile: isMobileStyle }
}
