import type { AlertItem } from '../../api/types'
import { formatDateTime, formatPercent } from '../../utils/format'

interface InsightCardProps {
  alert: AlertItem
}

export const InsightCard = ({ alert }: InsightCardProps) => (
  <article className={`alert-card ${alert.seen ? '' : 'alert-card--unread'}`}>
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
