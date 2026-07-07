import { onMounted, onUnmounted } from 'vue'

/** Run `callback` every `interval` ms while the component is mounted. */
export function usePolling(callback: () => void | Promise<void>, interval: number): void {
  let timer: ReturnType<typeof setInterval> | null = null

  onMounted(() => {
    timer = setInterval(() => {
      void callback()
    }, interval)
  })

  onUnmounted(() => {
    if (timer !== null) {
      clearInterval(timer)
      timer = null
    }
  })
}
