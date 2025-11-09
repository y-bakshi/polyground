import { API_BASE_URL, USE_MOCK_DATA } from '../config/constants'
import { mockStore } from './mockData'
import type {
  AlertItem,
  EventDetail,
  MarketSnapshot,
  PinMarketRequest,
  PinnedMarket,
  SparklinePoint,
} from './types'

const JSON_HEADERS = { 'Content-Type': 'application/json' }
const shouldMock = USE_MOCK_DATA

// Backend response types (snake_case)
interface BackendPinnedMarket {
  id: number
  user_id: number
  market_id: string
  pinned_at: string
  latest_prob: number | null
  latest_price: number | null
  latest_volume: number | null
  market_title: string | null
  history: BackendMarketHistory[]
}

interface BackendAlert {
  id: number
  user_id: number
  market_id: string
  ts: string
  change_pct: number
  threshold: number
  market_title: string | null
  insight_text: string
  seen: boolean
}

interface BackendMarketHistory {
  ts: string
  implied_prob: number
  price: number
  volume: number
  market_title: string | null
}

interface BackendMarketDetail {
  market_id: string
  latest: BackendMarketHistory
  history: BackendMarketHistory[]
  data_points: number
}

// Adapter functions to convert backend responses to frontend types
function adaptPinnedMarket(backend: BackendPinnedMarket): PinnedMarket {
  // Convert history to sparkline format
  const sparkline: SparklinePoint[] = backend.history.map(h => ({
    ts: h.ts,
    value: h.implied_prob,
  }))

  // Calculate change percentage from first to last data point
  let changePct = 0
  if (backend.history.length >= 2) {
    const firstProb = backend.history[0].implied_prob
    const lastProb = backend.history[backend.history.length - 1].implied_prob
    changePct = lastProb - firstProb
  }

  return {
    marketId: backend.market_id,
    title: backend.market_title || `Market ${backend.market_id}`,
    impliedProbability: backend.latest_prob || 0,
    changePct,
    volume24h: backend.latest_volume || undefined,
    updatedAt: backend.pinned_at,
    sparkline,
  }
}

function adaptAlert(backend: BackendAlert): AlertItem {
  return {
    id: String(backend.id),
    marketId: backend.market_id,
    marketTitle: backend.market_title || `Market ${backend.market_id}`,
    changePct: backend.change_pct,
    threshold: backend.threshold,
    insightText: backend.insight_text,
    createdAt: backend.ts,
    seen: backend.seen,
  }
}

function adaptMarketSnapshot(backend: BackendMarketDetail): MarketSnapshot {
  const history: SparklinePoint[] = backend.history.map(h => ({
    ts: h.ts,
    value: h.implied_prob,
  }))

  return {
    marketId: backend.market_id,
    title: backend.latest.market_title || `Market ${backend.market_id}`,
    latest: {
      impliedProbability: backend.latest.implied_prob,
      price: backend.latest.price,
      volume: backend.latest.volume,
      updatedAt: backend.latest.ts,
    },
    history,
    alerts: [], // Will be fetched separately
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: JSON_HEADERS,
    ...init,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Request failed')
  }

  return response.json() as Promise<T>
}

const withFallback = async <T>(
  path: string,
  init: RequestInit | undefined,
  fallback: () => T,
): Promise<T> => {
  if (shouldMock) {
    return fallback()
  }

  try {
    return await request<T>(path, init)
  } catch (error) {
    console.warn(`Falling back to mock data for ${path}`, error)
    return fallback()
  }
}

export interface PinMarketResponse {
  status: string
  pinned?: PinnedMarket
}

export const apiClient = {
  getPinnedMarkets: async (userId: string): Promise<PinnedMarket[]> => {
    if (shouldMock) {
      return mockStore.getPinnedMarkets()
    }

    try {
      const response = await request<{ items: BackendPinnedMarket[] }>(
        `/api/pinned?userId=${userId}`,
      )
      return response.items.map(adaptPinnedMarket)
    } catch (error) {
      console.warn('Falling back to mock data for pinned markets', error)
      return mockStore.getPinnedMarkets()
    }
  },

  pinMarket: async (payload: PinMarketRequest): Promise<PinMarketResponse> => {
    if (shouldMock) {
      return { status: 'mocked', pinned: mockStore.pinMarket(payload.marketId) }
    }

    try {
      const response = await request<{ status: string; message: string }>(
        '/api/pin',
        {
          method: 'POST',
          body: JSON.stringify({ userId: Number(payload.userId), marketId: payload.marketId }),
        },
      )
      return { status: response.status }
    } catch (error) {
      console.warn('Falling back to mock data for pin market', error)
      return { status: 'mocked', pinned: mockStore.pinMarket(payload.marketId) }
    }
  },

  getAlerts: async (userId: string): Promise<AlertItem[]> => {
    if (shouldMock) {
      return mockStore.getAlerts()
    }

    try {
      const response = await request<{ alerts: BackendAlert[] }>(
        `/api/alerts?userId=${userId}`,
      )
      return response.alerts.map(adaptAlert)
    } catch (error) {
      console.warn('Falling back to mock data for alerts', error)
      return mockStore.getAlerts()
    }
  },

  getMarketSnapshot: async (marketId: string): Promise<MarketSnapshot> => {
    if (shouldMock) {
      return mockStore.getMarketSnapshot(marketId)
    }

    try {
      const response = await request<BackendMarketDetail>(
        `/api/market/${marketId}?hours=24`,
      )
      return adaptMarketSnapshot(response)
    } catch (error) {
      console.warn('Falling back to mock data for market snapshot', error)
      return mockStore.getMarketSnapshot(marketId)
    }
  },

  getEventDetail: async (eventId: string): Promise<EventDetail> => {
    if (shouldMock) {
      throw new Error('Events not supported in mock mode')
    }

    try {
      const response = await request<EventDetail>(
        `/api/event/${eventId}`,
      )
      return response
    } catch (error) {
      console.error('Failed to fetch event details', error)
      throw error
    }
  },
}

export const isMockMode = shouldMock
