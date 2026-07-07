import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { MockService } from '../src/api/mock/mockService'

// Force the failure branch off so latency/shape assertions are deterministic.
function noFailure(): void {
  vi.spyOn(Math, 'random').mockReturnValue(0.5)
}

describe('MockService', () => {
  let service: MockService

  beforeEach(() => {
    service = new MockService()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('getMetrics resolves with the four numeric fields', async () => {
    noFailure()
    const m = await service.getMetrics()
    expect(typeof m.deviceCount).toBe('number')
    expect(typeof m.onlineRate).toBe('number')
    expect(typeof m.dailyOutput).toBe('number')
    expect(typeof m.alarmCount).toBe('number')
  })

  it('delays before resolving (fake timers)', async () => {
    vi.useFakeTimers()
    noFailure()
    let settled = false
    const p = service.getMetrics().then((v) => {
      settled = true
      return v
    })
    // Not resolved before the minimum 300ms delay elapses.
    await vi.advanceTimersByTimeAsync(200)
    expect(settled).toBe(false)
    await vi.advanceTimersByTimeAsync(700)
    await p
    expect(settled).toBe(true)
  })

  it('produces varying data across calls (randomness)', async () => {
    const results = await Promise.all(
      Array.from({ length: 8 }, () => service.getTrendData().catch(() => null))
    )
    const signatures = results
      .filter((r): r is NonNullable<typeof r> => r !== null)
      .map((r) => r.map((p) => p.output).join(','))
    expect(new Set(signatures).size).toBeGreaterThan(1)
  })

  it('getChartData returns categories, ranking and radar dimensions', async () => {
    noFailure()
    const c = await service.getChartData()
    expect(c.alarmCategories.length).toBeGreaterThan(0)
    expect(c.regionalRanking.length).toBeGreaterThan(0)
    expect(c.radar.length).toBeGreaterThanOrEqual(5)
  })
})
