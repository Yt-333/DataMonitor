import type { EChartsOption } from 'echarts'

export const PALETTE = {
  nebulaBlue: '#00C2FF',
  cyan: '#00F0FF',
  purple: '#A855F7',
  text: '#E0F7FA',
  textDim: 'rgba(224,247,250,0.55)',
  grid: 'rgba(0,240,255,0.10)'
}

/** Shared dark base merged into every chart option. */
export const chartBase: EChartsOption = {
  textStyle: {
    color: PALETTE.text,
    fontFamily: 'Rajdhani, "Microsoft YaHei", sans-serif'
  },
  color: [PALETTE.cyan, PALETTE.nebulaBlue, PALETTE.purple, '#34D399', '#FBBF24', '#FB7185'],
  tooltip: {
    backgroundColor: 'rgba(8,13,32,0.92)',
    borderColor: 'rgba(0,240,255,0.35)',
    textStyle: { color: PALETTE.text }
  }
}
