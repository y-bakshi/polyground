import { Link, useParams, useNavigate } from 'react-router-dom'
import { useMarketDetails } from '../hooks/useMarketDetails'
import { useEventDetails } from '../hooks/useEventDetails'
import { Sparkline } from '../components/charts/Sparkline'
import { formatDateTime, formatPercent } from '../utils/format'
import { InsightCard } from '../components/alerts/InsightCard'
import { useEffect } from 'react'

export const MarketDetailPage = () => {
  const { marketId } = useParams<{ marketId: string }>()
  const navigate = useNavigate()
  const { data: market, isLoading: marketLoading, error: marketError } = useMarketDetails(marketId)
  const { data: event, isLoading: eventLoading } = useEventDetails(marketId)

  // If it's an event, redirect to event detail page
  useEffect(() => {
    if (event && !eventLoading) {
      navigate(`/event/${marketId}`, { replace: true })
    }
  }, [event, eventLoading, marketId, navigate])

  const isLoading = marketLoading || eventLoading

  if (!marketId) {
    return (
      <section className="page">
        <p>Missing market id.</p>
        <Link to="/">Return home</Link>
      </section>
    )
  }

  if (isLoading || !market) {
    return (
      <section className="page">
        <div className="card">Loading market details…</div>
      </section>
    )
  }

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <h1>{market.title}</h1>
          {market.description && <p>{market.description}</p>}
        </div>
        <Link to="/" className="link">
          ← Back to overview
        </Link>
      </header>

      <div className="detail-summary">
        <div className="card">
          <p className="muted">Latest implied</p>
          <h2>{formatPercent(market.latest.impliedProbability)}</h2>
          <p className="muted">
            Price {market.latest.price.toFixed(2)} • Updated {formatDateTime(market.latest.updatedAt)}
          </p>
        </div>
        <div className="card">
          <p className="muted">24h volume</p>
          <h2>${market.latest.volume.toLocaleString()}</h2>
          {market.resolutionDate && <p className="muted">Resolves {formatDateTime(market.resolutionDate)}</p>}
        </div>
      </div>

      <div className="detail-grid">
        <div className="card">
          <header>
            <h3>Probability trend</h3>
          </header>
          <Sparkline data={market.history} height={220} width={600} />
        </div>
        <div className="card">
          <header>
            <h3>Recent alerts</h3>
          </header>
          {market.alerts && market.alerts.length > 0 ? (
            <div className="alert-stack">
              {market.alerts.map((alert) => (
                <InsightCard key={alert.id} alert={alert} />
              ))}
            </div>
          ) : (
            <p>No alerts fired for this market yet.</p>
          )}
        </div>
      </div>
    </section>
  )
}
