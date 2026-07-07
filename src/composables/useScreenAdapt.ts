import { onMounted, onUnmounted, ref, type Ref } from 'vue'

const DESIGN_WIDTH = 1920
const DESIGN_HEIGHT = 1080

export interface ScreenAdaptStyle {
  width: string
  height: string
  transform: string
  transformOrigin: string
}

/** Compute the contain-fit scale for the 1920x1080 canvas at a viewport size. */
export function calcScale(vw: number, vh: number): number {
  return Math.min(vw / DESIGN_WIDTH, vh / DESIGN_HEIGHT)
}

/** Reactive style that scales the 1920x1080 stage to fit any viewport. */
export function useScreenAdapt(): { style: Ref<ScreenAdaptStyle>; scale: Ref<number> } {
  const scale = ref(1)
  const style = ref<ScreenAdaptStyle>({
    width: `${DESIGN_WIDTH}px`,
    height: `${DESIGN_HEIGHT}px`,
    transform: 'scale(1)',
    transformOrigin: 'top left'
  })

  function update(): void {
    const s = calcScale(window.innerWidth, window.innerHeight)
    scale.value = s
    // Center the scaled stage within the viewport.
    const left = (window.innerWidth - DESIGN_WIDTH * s) / 2
    const top = (window.innerHeight - DESIGN_HEIGHT * s) / 2
    style.value = {
      width: `${DESIGN_WIDTH}px`,
      height: `${DESIGN_HEIGHT}px`,
      transform: `translate(${left}px, ${top}px) scale(${s})`,
      transformOrigin: 'top left'
    }
  }

  onMounted(() => {
    update()
    window.addEventListener('resize', update)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', update)
  })

  return { style, scale }
}
