import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { MarketSnapshot } from '../api/types'

export const useMarketDetails = (marketId: string | undefined) =>
  useQuery<MarketSnapshot>({
    queryKey: ['market', marketId],
    queryFn: () => apiClient.getMarketSnapshot(marketId as string),
    enabled: Boolean(marketId),
    refetchInterval: 120_000,
  })
