interface MetricCardProps {
  label: string
  value: string
  caption?: string
  trend?: number
  onClick?: () => void
}

export const MetricCard = ({ label, value, caption, trend, onClick }: MetricCardProps) => {
  const formattedTrend = typeof trend === 'number' ? `${trend > 0 ? '+' : ''}${trend.toFixed(1)}%` : null
  const trendClass = trend && trend < 0 ? 'trend negative' : 'trend positive'
  const clickable = typeof onClick === 'function'
  const className = clickable ? 'metric-card metric-card--action' : 'metric-card'

  const content = (
    <>
      <p className="metric-label">{label}</p>
      <div className="metric-value">{value}</div>
      <div className="metric-footer">
        {caption && <span>{caption}</span>}
        {formattedTrend && <span className={trendClass}>{formattedTrend}</span>}
      </div>
    </>
  )

  if (clickable) {
    return (
      <button type="button" className={className} onClick={onClick}>
        {content}
      </button>
    )
  }

  return <div className={className}>{content}</div>
}
