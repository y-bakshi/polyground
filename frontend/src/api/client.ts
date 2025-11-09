import { API_BASE_URL, USE_MOCK_DATA } from '../config/constants'
import { mockStore } from './mockData'
import type {
  AlertItem,
  MarketSnapshot,
  PinMarketRequest,
  PinnedMarket,
} from './types'

const JSON_HEADERS = { 'Content-Type': 'application/json' }
const shouldMock = USE_MOCK_DATA ?? import.meta.env.DEV

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
  getPinnedMarkets: (userId: string): Promise<PinnedMarket[]> =>
    withFallback<{ items: PinnedMarket[] }>(
      `/api/pinned?userId=${userId}`,
      undefined,
      () => ({ items: mockStore.getPinnedMarkets() }),
    ).then((payload) => payload.items),

  pinMarket: (payload: PinMarketRequest): Promise<PinMarketResponse> =>
    withFallback<PinMarketResponse>(
      '/api/pin',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      () => ({ status: 'mocked', pinned: mockStore.pinMarket(payload.marketId) }),
    ),

  getAlerts: (userId: string): Promise<AlertItem[]> =>
    withFallback<{ alerts: AlertItem[] }>(
      `/api/alerts?userId=${userId}`,
      undefined,
      () => ({ alerts: mockStore.getAlerts() }),
    ).then((payload) => payload.alerts),

  getMarketSnapshot: (marketId: string): Promise<MarketSnapshot> =>
    withFallback<MarketSnapshot>(
      `/api/market/${marketId}`,
      undefined,
      () => mockStore.getMarketSnapshot(marketId),
    ),
}

export const isMockMode = shouldMock
