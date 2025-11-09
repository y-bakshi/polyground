import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAlerts } from '../hooks/useAlerts'
import { usePinMarket, usePinnedMarkets, useUnpinMarket } from '../hooks/usePinnedMarkets'
import { MetricCard } from '../components/common/MetricCard'
import { PinnedTable } from '../components/markets/PinnedTable'
import { PinMarketPanel } from '../components/markets/PinMarketPanel'

export const OverviewPage = () => {
  const navigate = useNavigate()
  const { data: pinnedMarkets, isLoading, isFetching } = usePinnedMarkets()
  const { data: alerts } = useAlerts()
  const { mutateAsync: pinMarket, isPending: isPinning } = usePinMarket()
  const { mutateAsync: unpinMarket } = useUnpinMarket()
  const [selectedMarketIds, setSelectedMarketIds] = useState<Set<string>>(new Set())
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    if (!pinnedMarkets || pinnedMarkets.length === 0) {
      setSelectedMarketIds(new Set())
      return
    }

    setSelectedMarketIds((current) => {
      const validIds = new Set(pinnedMarkets.map((market) => market.marketId))
      let changed = false
      const next = new Set<string>()

      current.forEach((id) => {
        if (validIds.has(id)) {
          next.add(id)
        } else {
          changed = true
        }
      })

      return changed ? next : current
    })
  }, [pinnedMarkets])

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

  const allMarketIds = useMemo(
    () => (pinnedMarkets ? pinnedMarkets.map((market) => market.marketId) : []),
    [pinnedMarkets],
  )

  const areAllSelected = allMarketIds.length > 0 && allMarketIds.every((id) => selectedMarketIds.has(id))

  const toggleSelection = (marketId: string) => {
    setSelectedMarketIds((current) => {
      const next = new Set(current)
      if (next.has(marketId)) {
        next.delete(marketId)
      } else {
        next.add(marketId)
      }
      return next
    })
  }

  const handleDeleteSelected = async () => {
    if (selectedMarketIds.size === 0 || isDeleting) return
    setIsDeleting(true)
    try {
      for (const marketId of selectedMarketIds) {
        await unpinMarket(marketId)
      }
      setSelectedMarketIds(new Set())
    } catch (error) {
      console.error('Failed to delete selected markets', error)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleSelectAll = (checked: boolean) => {
    if (allMarketIds.length === 0) return
    if (checked) {
      setSelectedMarketIds(new Set(allMarketIds))
    } else {
      setSelectedMarketIds(new Set())
    }
  }

  return (
    <section className="page">
      <header className="page-head page-head--centered">
        <div>
          <h1>Overview</h1>
          <p>Pin Polymarket trades, monitor probability shifts, and skim Claude insights.</p>
        </div>
        <span className={`status-pill ${isFetching ? 'syncing' : 'live'}`}>
          {isFetching ? 'Syncing…' : 'Live'}
        </span>
      </header>

      <PinMarketPanel
        isSubmitting={isPinning}
        onPin={async (input) => {
          await pinMarket(input)
        }}
      />

      <div className="pinned-layout">
        <PinnedTable
          markets={pinnedMarkets}
          isLoading={isLoading}
          selectedMarketIds={selectedMarketIds}
          onToggleSelection={toggleSelection}
          onDeleteSelected={handleDeleteSelected}
          isDeleting={isDeleting}
          onSelectAll={handleSelectAll}
          areAllSelected={areAllSelected}
        />
        <div className="metrics-column">
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
            onClick={() => navigate('/alerts')}
          />
        </div>
      </div>
    </section>
  )
}
