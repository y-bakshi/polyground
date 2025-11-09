import { useMemo, useState } from 'react'
import type { AlertItem } from '../api/types'
import { useAlerts, useMarkAlertSeen } from '../hooks/useAlerts'
import { InsightCard } from '../components/alerts/InsightCard'

const filters = [
  { value: 'all', label: 'All' },
  { value: 'unread', label: 'Unread' },
] as const

export const AlertsPage = () => {
  const { data: alerts, isLoading } = useAlerts()
  const [filter, setFilter] = useState<(typeof filters)[number]['value']>('all')
  const { mutateAsync: markSeen } = useMarkAlertSeen()
  const [markingId, setMarkingId] = useState<string | null>(null)

  const filteredAlerts = useMemo(() => {
    if (!alerts) return []
    return filter === 'all' ? alerts : alerts.filter((alert) => !alert.seen)
  }, [alerts, filter])

  const handleAlertClick = async (alert: AlertItem) => {
    if (alert.seen || markingId === alert.id) return
    setMarkingId(alert.id)
    try {
      await markSeen(alert.id)
    } catch (error) {
      console.error('Failed to mark alert as seen', error)
    } finally {
      setMarkingId((current) => (current === alert.id ? null : current))
    }
  }

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <h1>Alerts</h1>
          <p>Claude summarizes large moves so you can react quickly.</p>
        </div>
        <div className="filter-group">
          {filters.map((option) => (
            <button
              key={option.value}
              className={filter === option.value ? 'filter-btn active' : 'filter-btn'}
              onClick={() => setFilter(option.value)}
              type="button"
            >
              {option.label}
            </button>
          ))}
        </div>
      </header>

      {isLoading && <div className="card">Loading alerts…</div>}
      {!isLoading && filteredAlerts.length === 0 && <div className="card">No alerts yet. Lower the threshold or wait for a poll cycle.</div>}
      <div className="alerts-grid">
        {filteredAlerts.map((alert) => (
          <InsightCard
            key={alert.id}
            alert={alert}
            onClick={handleAlertClick}
            isProcessing={markingId === alert.id}
          />
        ))}
      </div>
    </section>
  )
}
