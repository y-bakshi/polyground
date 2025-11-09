import { useId } from 'react'
import type { SparklinePoint } from '../../api/types'

interface SparklineProps {
  data: SparklinePoint[]
  height?: number
  width?: number
}

export const Sparkline = ({ data, height = 40, width = 140 }: SparklineProps) => {
  const gradientId = useId()
  if (!data || data.length === 0) {
    return <div className="sparkline-placeholder">No history</div>
  }

  const values = data.map((point) => point.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1

  const points = data
    .map((point, idx) => {
      const x = (idx / (data.length - 1 || 1)) * width
      const y = height - ((point.value - min) / range) * height
      return `${x.toFixed(2)},${y.toFixed(2)}`
    })
    .join(' ')

  return (
    <svg className="sparkline" width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Market sparkline">
      <polyline fill="none" stroke={`url(#${gradientId})`} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" points={points} />
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#60a5fa" />
          <stop offset="100%" stopColor="#22d3ee" />
        </linearGradient>
      </defs>
    </svg>
  )
}
