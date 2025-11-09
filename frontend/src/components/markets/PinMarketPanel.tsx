import { useState } from 'react'

interface PinMarketPanelProps {
  isSubmitting: boolean
  onPin: (marketId: string) => Promise<unknown>
}

const quickPicks = [
  { id: 'trump-2024', label: 'US Election' },
  { id: 'btc-100k', label: 'BTC $100k' },
  { id: 'ai-regulation', label: 'AI Bill' },
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
    try {
      await onPin(trimmed)
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
        <p>Paste a Polymarket marketId or tap a quick pick.</p>
      </header>
      <form onSubmit={handleSubmit} className="pin-form">
        <input
          type="text"
          placeholder="e.g. trump-2024"
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
