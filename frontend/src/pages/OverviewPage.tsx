import { useMemo } from 'react'
import { useAlerts } from '../hooks/useAlerts'
import { usePinMarket, usePinnedMarkets } from '../hooks/usePinnedMarkets'
import { MetricCard } from '../components/common/MetricCard'
import { PinnedTable } from '../components/markets/PinnedTable'
import { PinMarketPanel } from '../components/markets/PinMarketPanel'

export const OverviewPage = () => {
  const { data: pinnedMarkets, isLoading, isFetching } = usePinnedMarkets()
  const { data: alerts } = useAlerts()
  const { mutateAsync: pinMarket, isPending: isPinning } = usePinMarket()

  const stats = useMemo(() => {
    if (!pinnedMarkets || pinnedMarkets.length === 0) {
      return {
        averageProbability: 0,
        averageMove: 0,
      }
    }

    const totalProb = pinnedMarkets.reduce((sum, market) => sum + market.impliedProbability, 0)
    const totalMove = pinnedMarkets.reduce((sum, market) => sum + market.changePct, 0)

    return {
      averageProbability: totalProb / pinnedMarkets.length,
      averageMove: totalMove / pinnedMarkets.length,
    }
  }, [pinnedMarkets])

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <h1>Overview</h1>
          <p>Pin Polymarket trades, monitor probability shifts, and skim Claude insights.</p>
        </div>
        <span className={`status-pill ${isFetching ? 'syncing' : 'live'}`}>
          {isFetching ? 'Syncing…' : 'Live'}
        </span>
      </header>

      <div className="metrics-grid">
        <MetricCard label="Pinned" value={`${pinnedMarkets?.length ?? 0}`} caption="tracking now" />
        <MetricCard
          label="Avg implied"
          value={`${stats.averageProbability.toFixed(1)}%`}
          caption="across pins"
          trend={stats.averageMove}
        />
        <MetricCard
          label="Unread alerts"
          value={`${alerts?.filter((alert) => !alert.seen).length ?? 0}`}
          caption="Claude insights waiting"
        />
      </div>

      <div className="overview-grid">
        <PinnedTable markets={pinnedMarkets} isLoading={isLoading} />
        <PinMarketPanel
          isSubmitting={isPinning}
          onPin={async (input) => {
            await pinMarket(input)
          }}
        />
      </div>
    </section>
  )
}
