import type { AlertItem, MarketSnapshot, PinnedMarket, SparklinePoint } from './types'

const now = Date.now()

const hoursAgo = (hours: number) => new Date(now - hours * 60 * 60 * 1000).toISOString()

const buildHistory = (values: number[], spacingHours = 2): SparklinePoint[] =>
  values.map((value, idx) => ({ ts: hoursAgo((values.length - idx) * spacingHours), value }))

const snapshotFromHistory = (
  marketId: string,
  title: string,
  historyValues: number[],
  opts: Partial<Omit<MarketSnapshot, 'marketId' | 'title' | 'history' | 'latest'>> & {
    latestVolume?: number
    latestPrice?: number
  } = {},
): MarketSnapshot => {
  const history = buildHistory(historyValues)
  const latestPoint = history[history.length - 1]
  return {
    marketId,
    title,
    description: opts.description,
    resolutionDate: opts.resolutionDate,
    latest: {
      impliedProbability: latestPoint.value,
      price: opts.latestPrice ?? Number((latestPoint.value / 100).toFixed(2)),
      volume: opts.latestVolume ?? 10000,
      updatedAt: latestPoint.ts,
    },
    history,
    alerts: [],
  }
}

const baseSnapshots: MarketSnapshot[] = [
  snapshotFromHistory('trump-2024', 'Will Donald Trump win the 2024 U.S. presidential election?', [
    58.1,
    59.3,
    57.6,
    60.4,
    62.5,
    61.2,
    63.8,
    64.1,
    65.3,
    64.9,
    66.2,
    67.1,
  ], {
    description: 'Tracking the implied probability that Donald Trump will win the 2024 election.',
    resolutionDate: '2024-11-06T00:00:00Z',
    latestVolume: 245000,
  }),
  snapshotFromHistory('btc-100k', 'Will Bitcoin reach $100k before year end?', [
    42.5,
    43.8,
    41.9,
    44.2,
    46.7,
    48.1,
    49.5,
    50.3,
    52.1,
    53.4,
    54.6,
    55.8,
  ], {
    description: 'Binary market on Bitcoin touching $100k before Dec 31.',
    resolutionDate: '2024-12-31T23:59:59Z',
    latestVolume: 178400,
  }),
  snapshotFromHistory('ai-regulation', 'Will a major AI regulation pass in the US by Q4?', [
    34.2,
    33.8,
    35.1,
    36.4,
    37.3,
    38.9,
    39.7,
    38.5,
    40.2,
    41.6,
    43.1,
    44.4,
  ], {
    description: 'Captures the chance of a comprehensive AI regulation passing Congress.',
    resolutionDate: '2024-10-01T00:00:00Z',
    latestVolume: 98600,
  }),
]

const mockAlerts: AlertItem[] = [
  {
    id: 'alert-001',
    marketId: 'trump-2024',
    marketTitle: baseSnapshots[0].title,
    changePct: 4.6,
    threshold: 3,
    insightText:
      'Turnout models are shifting after several swing-state polls tightened. Watch for fundraising headlines and legal calendar updates that could reverse sentiment.',
    createdAt: hoursAgo(3),
    seen: false,
    timeToResolution: '3 months',
    volumeDelta: 52000,
  },
  {
    id: 'alert-002',
    marketId: 'btc-100k',
    marketTitle: baseSnapshots[1].title,
    changePct: 5.3,
    threshold: 4,
    insightText:
      'BTC ripped after ETF inflows hit a weekly high and miners signaled lower sell pressure. Key risk: CPI surprise or hawkish Fed minutes.',
    createdAt: hoursAgo(6),
    seen: false,
    timeToResolution: '5 months',
    volumeDelta: 76000,
  },
  {
    id: 'alert-003',
    marketId: 'ai-regulation',
    marketTitle: baseSnapshots[2].title,
    changePct: -2.1,
    threshold: 2,
    insightText:
      'Momentum cooled after committee markup slipped. Still expect headlines around bipartisan privacy talks; watch lobbying disclosures.',
    createdAt: hoursAgo(12),
    seen: true,
    timeToResolution: '2 months',
    volumeDelta: 15000,
  },
]

const clone = <T>(value: T): T =>
  typeof structuredClone === 'function' ? structuredClone(value) : JSON.parse(JSON.stringify(value))

const snapshotMap = new Map<string, MarketSnapshot>()
baseSnapshots.forEach((snapshot) => {
  snapshotMap.set(snapshot.marketId, snapshot)
})

const toPinned = (snapshot: MarketSnapshot): PinnedMarket => {
  const first = snapshot.history[0]
  const last = snapshot.history[snapshot.history.length - 1]
  const changePct = Number((last.value - first.value).toFixed(2))
  return {
    marketId: snapshot.marketId,
    title: snapshot.title,
    category: snapshot.description?.includes('Bitcoin') ? 'Crypto' : 'Politics',
    impliedProbability: snapshot.latest.impliedProbability,
    changePct,
    volume24h: snapshot.latest.volume,
    updatedAt: snapshot.latest.updatedAt,
    sparkline: snapshot.history,
    unreadAlerts: mockAlerts.filter((alert) => !alert.seen && alert.marketId === snapshot.marketId).length,
  }
}

let pinnedMarkets = baseSnapshots.map(toPinned)

const ensureSnapshot = (marketId: string): MarketSnapshot => {
  if (snapshotMap.has(marketId)) {
    return snapshotMap.get(marketId) as MarketSnapshot
  }

  const placeholderHistory = Array.from({ length: 12 }, (_, idx) => {
    const base = 30 + idx * 1.5
    const jitter = (Math.random() - 0.5) * 4
    return Number(Math.min(90, Math.max(10, base + jitter)).toFixed(2))
  })

  const placeholder = snapshotFromHistory(
    marketId,
    `Pinned market ${marketId}`,
    placeholderHistory,
    {
      description: 'Placeholder market while real data loads.',
      resolutionDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      latestVolume: 25000 + Math.floor(Math.random() * 25000),
    },
  )

  snapshotMap.set(marketId, placeholder)
  return placeholder
}

export const mockStore = {
  getPinnedMarkets: (): PinnedMarket[] => clone(pinnedMarkets),
  pinMarket: (marketId: string): PinnedMarket => {
    const snapshot = ensureSnapshot(marketId)
    const exists = pinnedMarkets.some((item) => item.marketId === marketId)
    if (!exists) {
      pinnedMarkets = [...pinnedMarkets, toPinned(snapshot)]
    }
    return toPinned(snapshot)
  },
  unpinMarket: (marketId: string): void => {
    pinnedMarkets = pinnedMarkets.filter((item) => item.marketId !== marketId)
  },
  getAlerts: (): AlertItem[] => clone(mockAlerts),
  markAlertSeen: (alertId: string): void => {
    const index = mockAlerts.findIndex((alert) => alert.id === alertId)
    if (index !== -1) {
      mockAlerts[index] = { ...mockAlerts[index], seen: true }
    }
  },
  getMarketSnapshot: (marketId: string): MarketSnapshot => {
    const snapshot = clone(ensureSnapshot(marketId))
    const relatedAlerts = mockAlerts.filter((alert) => alert.marketId === marketId)
    return { ...snapshot, alerts: clone(relatedAlerts) }
  },
}
