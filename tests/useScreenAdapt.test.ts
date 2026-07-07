import { describe, it, expect } from 'vitest'
import { calcScale } from '../src/composables/useScreenAdapt'

describe('useScreenAdapt · calcScale', () => {
  it('returns 1 at the exact design resolution', () => {
    expect(calcScale(1920, 1080)).toBe(1)
  })

  it('scales to the constraining axis (contain-fit)', () => {
    // Half width, full height → limited by width.
    expect(calcScale(960, 1080)).toBeCloseTo(0.5)
    // Full width, half height → limited by height.
    expect(calcScale(1920, 540)).toBeCloseTo(0.5)
  })

  it('picks the smaller ratio when aspect ratios differ', () => {
    // 2560x1080: width ratio 1.333, height ratio 1 → min is 1.
    expect(calcScale(2560, 1080)).toBeCloseTo(1)
    // 1920x2160: width ratio 1, height ratio 2 → min is 1.
    expect(calcScale(1920, 2160)).toBeCloseTo(1)
  })
})
