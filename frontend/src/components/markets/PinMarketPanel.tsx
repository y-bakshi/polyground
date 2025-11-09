import { useState } from 'react'
import { extractMarketId } from '../../utils/polymarket'

interface PinMarketPanelProps {
  isSubmitting: boolean
  onPin: (marketId: string) => Promise<unknown>
}

const quickPicks = [
  { id: '516710', label: 'US Recession 2025' },
  { id: '623603', label: 'Gov Shutdown Nov 12-15' },
]

type StatusMessage = {
  type: 'success' | 'error'
  message: string
}

export const PinMarketPanel = ({ isSubmitting, onPin }: PinMarketPanelProps) => {
  const [value, setValue] = useState('')
  const [status, setStatus] = useState<StatusMessage | null>(null)

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmed = value.trim()
    if (!trimmed) return

    setStatus(null)

    // Extract market ID from URL or validate input
    const { marketId, error } = extractMarketId(trimmed)

    if (error) {
      setStatus({ type: 'error', message: error })
      return
    }

    if (!marketId) {
      setStatus({ type: 'error', message: 'Please enter a valid market ID or URL' })
      return
    }

    try {
      await onPin(marketId)
      setValue('')
      setStatus({ type: 'success', message: "Pinned! We'll watch it for moves." })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unable to pin market'
      setStatus({ type: 'error', message })
    }
  }

  return (
    <div className="card pin-panel">
      <header>
        <h3>Pin a market</h3>
        <p>Paste a Polymarket URL or market ID, or tap a quick pick.</p>
      </header>
      <form onSubmit={handleSubmit} className="pin-form">
        <input
          type="text"
          placeholder="e.g. 516710 or https://polymarket.com/..."
          value={value}
          onChange={(event) => setValue(event.target.value)}
          disabled={isSubmitting}
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Pinning…' : 'Pin market'}
        </button>
      </form>
      <div className="quick-picks">
        {quickPicks.map((pick) => (
          <button key={pick.id} type="button" onClick={() => setValue(pick.id)} disabled={isSubmitting}>
            {pick.label}
          </button>
        ))}
      </div>
      {status && <p className={`pin-status ${status.type}`}>{status.message}</p>}
    </div>
  )
}
