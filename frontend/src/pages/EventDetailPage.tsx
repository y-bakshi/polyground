import { Link, useParams } from 'react-router-dom'
import { useEventDetails } from '../hooks/useEventDetails'
import { formatDateTime } from '../utils/format'

export const EventDetailPage = () => {
  const { eventId } = useParams<{ eventId: string }>()
  const { data: event, isLoading, error } = useEventDetails(eventId)

  if (!eventId) {
    return (
      <section className="page">
        <p>Missing event id.</p>
        <Link to="/">Return home</Link>
      </section>
    )
  }

  if (isLoading) {
    return (
      <section className="page">
        <div className="card">Loading event details…</div>
      </section>
    )
  }

  if (error || !event) {
    return (
      <section className="page">
        <div className="card">
          <p>Could not load event details. This might be a single market instead of an event.</p>
          <Link to={`/market/${eventId}`}>View as market</Link>
        </div>
      </section>
    )
  }

  return (
    <section className="page">
      <Link to="/" className="link">
        ← Back to overview
      </Link>
      <header className="page-head">
        <div>
          <h1>{event.title}</h1>
          {event.description && <p>{event.description}</p>}
        </div>
      </header>

      <div className="detail-summary">
        <div className="card">
          <p className="muted">Status</p>
          <h2>{event.closed ? 'Closed' : event.active ? 'Active' : 'Inactive'}</h2>
          {event.end_date && <p className="muted">Ends {formatDateTime(event.end_date)}</p>}
        </div>
        <div className="card">
          <p className="muted">24h volume</p>
          <h2>${event.volume_24hr.toLocaleString()}</h2>
          <p className="muted">{event.market_count} markets in this event</p>
        </div>
      </div>

      <div className="card">
        <header>
          <h3>Individual Markets ({event.market_count})</h3>
          <p>Click any market to view details and pin it individually</p>
        </header>
        <div className="event-markets-grid">
          {event.markets.map((market) => (
            <Link
              key={market.id}
              to={`/market/${market.id}`}
              className="event-market-card"
            >
              <div className="event-market-header">
                <h4>{market.group_item_title || market.question}</h4>
                <span className={`status-badge ${market.active ? 'active' : 'inactive'}`}>
                  {market.closed ? 'Closed' : market.active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <p className="event-market-question">{market.question}</p>
              {market.outcome_prices && (
                <p className="muted">Price: {market.outcome_prices}</p>
              )}
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}
