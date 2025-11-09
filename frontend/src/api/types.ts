export interface SparklinePoint {
  ts: string
  value: number
}

export interface PinnedMarket {
  marketId: string
  title: string
  category?: string
  impliedProbability: number
  changePct: number
  volume24h?: number
  updatedAt: string
  sparkline: SparklinePoint[]
  unreadAlerts?: number
}

export interface AlertItem {
  id: string
  marketId: string
  marketTitle: string
  changePct: number
  threshold: number
  insightText: string
  createdAt: string
  seen: boolean
  timeToResolution?: string
  volumeDelta?: number
}

export interface MarketSnapshot {
  marketId: string
  title: string
  description?: string
  resolutionDate?: string
  latest: {
    impliedProbability: number
    price: number
    volume: number
    updatedAt: string
  }
  history: SparklinePoint[]
  alerts: AlertItem[]
}

export interface PinMarketRequest {
  userId: string
  marketId: string
}
