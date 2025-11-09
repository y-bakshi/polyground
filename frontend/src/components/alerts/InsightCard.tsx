import type { KeyboardEvent } from 'react'
import type { AlertItem } from '../../api/types'
import { formatDateTime, formatPercent } from '../../utils/format'

interface InsightCardProps {
  alert: AlertItem
  onClick?: (alert: AlertItem) => void
  isProcessing?: boolean
}

export const InsightCard = ({ alert, onClick, isProcessing }: InsightCardProps) => {
  const unread = !alert.seen
  const classes = ['alert-card']
  if (unread) {
    classes.push('alert-card--unread')
  } else {
    classes.push('alert-card--seen')
  }

  const handleActivate = () => {
    if (typeof onClick === 'function') {
      onClick(alert)
    }
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (!onClick) return
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      handleActivate()
    }
  }

  return (
    <article
      className={classes.join(' ')}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={handleActivate}
      onKeyDown={handleKeyDown}
      aria-busy={isProcessing ? 'true' : undefined}
    >
      <header>
        <div>
          <p className="alert-market">{alert.marketTitle}</p>
          <p className="alert-meta">{formatDateTime(alert.createdAt)}</p>
        </div>
        <span className={alert.changePct >= 0 ? 'delta positive' : 'delta negative'}>
          {formatPercent(alert.changePct)}
        </span>
      </header>
      <p className="alert-body">{alert.insightText}</p>
      <footer>
        <span>Threshold: {formatPercent(alert.threshold)}</span>
        {alert.volumeDelta && <span>Volume Δ {alert.volumeDelta.toLocaleString()}</span>}
        {alert.timeToResolution && <span>Resolution in {alert.timeToResolution}</span>}
      </footer>
    </article>
  )
}
