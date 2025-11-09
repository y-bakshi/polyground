interface MetricCardProps {
  label: string
  value: string
  caption?: string
  trend?: number
}

export const MetricCard = ({ label, value, caption, trend }: MetricCardProps) => {
  const formattedTrend = typeof trend === 'number' ? `${trend > 0 ? '+' : ''}${trend.toFixed(1)}%` : null
  const trendClass = trend && trend < 0 ? 'trend negative' : 'trend positive'

  return (
    <div className="metric-card">
      <p className="metric-label">{label}</p>
      <div className="metric-value">{value}</div>
      <div className="metric-footer">
        {caption && <span>{caption}</span>}
        {formattedTrend && <span className={trendClass}>{formattedTrend}</span>}
      </div>
    </div>
  )
}
