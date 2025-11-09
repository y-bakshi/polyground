import type { PinnedMarket } from '../../api/types'
import { Sparkline } from '../charts/Sparkline'
import { formatPercent } from '../../utils/format'
import { Link } from 'react-router-dom'

interface PinnedTableProps {
  markets?: PinnedMarket[]
  isLoading: boolean
  selectedMarketIds: Set<string>
  onToggleSelection: (marketId: string) => void
  onDeleteSelected: () => Promise<void> | void
  isDeleting: boolean
  onSelectAll: (checked: boolean) => void
  areAllSelected: boolean
}

export const PinnedTable = ({
  markets,
  isLoading,
  selectedMarketIds,
  onToggleSelection,
  onDeleteSelected,
  isDeleting,
  onSelectAll,
  areAllSelected,
}: PinnedTableProps) => {
  if (isLoading) {
    return <div className="card">Loading pinned markets...</div>
  }

  if (!markets || markets.length === 0) {
    return <div className="card">No pinned markets yet. Use the Pin form to track a contract.</div>
  }

  return (
    <div className="card">
      <div className="pinned-toolbar">
        <label className="select-all-toggle">
          <input
            type="checkbox"
            checked={areAllSelected}
            onChange={(event) => onSelectAll(event.target.checked)}
            disabled={isDeleting}
          />
          <span>{areAllSelected ? 'Deselect all' : 'Select all'}</span>
        </label>

        {selectedMarketIds.size > 0 && (
          <div className="pinned-actions">
            <span>{selectedMarketIds.size} selected</span>
            <button
              type="button"
              className="bulk-delete-btn"
              onClick={() => onDeleteSelected()}
              disabled={isDeleting}
              aria-label={isDeleting ? 'Deleting selected markets' : 'Delete selected markets'}
              title={isDeleting ? 'Deleting selected markets' : 'Delete selected markets'}
            >
              {isDeleting ? (
                '…'
              ) : (
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M7 6h10m-9 0V4h8v2m1 0v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V6h12Z"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M10 11v6m4-6v6"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
            </button>
          </div>
        )}
      </div>
      <table className="pinned-table">
        <thead>
          <tr>
            <th className="pin-select-col">Select</th>
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
                <td className="pin-select">
                  <input
                    type="checkbox"
                    aria-label={`Select ${market.title}`}
                    checked={selectedMarketIds.has(market.marketId)}
                    onChange={() => onToggleSelection(market.marketId)}
                  />
                </td>
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
                <td className="sparkline-cell">
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
