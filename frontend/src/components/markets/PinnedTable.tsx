import type { PinnedMarket } from '../../api/types'
import { Sparkline } from '../charts/Sparkline'
import { formatPercent } from '../../utils/format'
import { Link } from 'react-router-dom'

interface PinnedTableProps {
  markets?: PinnedMarket[]
  isLoading: boolean
}

export const PinnedTable = ({ markets, isLoading }: PinnedTableProps) => {
  if (isLoading) {
    return <div className="card">Loading pinned markets...</div>
  }

  if (!markets || markets.length === 0) {
    return <div className="card">No pinned markets yet. Use the Pin form to track a contract.</div>
  }

  return (
    <div className="card">
      <table className="pinned-table">
        <thead>
          <tr>
            <th>Market</th>
            <th>Implied %</th>
            <th>Δ</th>
            <th>24h Vol</th>
            <th>History</th>
          </tr>
        </thead>
        <tbody>
          {markets.map((market) => {
            // Link to event page if this is an event, otherwise link to market page
            const linkPath = market.isEvent && market.eventId
              ? `/event/${market.eventId}`
              : `/market/${market.marketId}`

            return (
              <tr key={market.marketId}>
                <td>
                  <Link to={linkPath} className="market-link">
                    <p>{market.title}</p>
                    <span>{market.isEvent ? 'Multi-outcome event' : (market.category ?? 'General')}</span>
                  </Link>
                </td>
                <td>{formatPercent(market.impliedProbability)}</td>
                <td>
                  <span className={market.changePct >= 0 ? 'delta positive' : 'delta negative'}>
                    {formatPercent(market.changePct)}
                  </span>
                </td>
                <td>{market.volume24h ? `$${market.volume24h.toLocaleString()}` : '—'}</td>
                <td>
                  <Sparkline data={market.sparkline} />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
