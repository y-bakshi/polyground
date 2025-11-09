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
  isEvent?: boolean  // True if this is a multi-outcome event
  eventId?: string  // Event ID if isEvent=true
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
  marketId: string  // Can be URL, slug, or numeric ID
}

export interface EventMarket {
  id: string
  question: string
  outcome_prices: string
  active: boolean
  closed: boolean
  group_item_title: string
}

export interface EventDetail {
  id: string
  title: string
  description?: string
  end_date?: string
  active: boolean
  closed: boolean
  volume_24hr: number
  markets: EventMarket[]
  market_count: number
}
