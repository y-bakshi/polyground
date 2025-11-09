import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient, isMockMode } from '../api/client'
import type { PinnedMarket } from '../api/types'
import { DEMO_USER_ID } from '../config/constants'

const pinnedKey = ['pinned', DEMO_USER_ID]

export const usePinnedMarkets = () =>
  useQuery<PinnedMarket[]>({
    queryKey: pinnedKey,
    queryFn: () => apiClient.getPinnedMarkets(DEMO_USER_ID),
    refetchInterval: 60_000,
  })

export const usePinMarket = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (marketId: string) =>
      apiClient.pinMarket({ userId: DEMO_USER_ID, marketId }),
    onSuccess: (response, marketId) => {
      if (isMockMode && response.pinned) {
        queryClient.setQueryData<PinnedMarket[]>(pinnedKey, (current) => {
          if (!current) return [response.pinned as PinnedMarket]
          const exists = current.some((item) => item.marketId === marketId)
          return exists ? current : [...current, response.pinned as PinnedMarket]
        })
      } else {
        queryClient.invalidateQueries({ queryKey: pinnedKey })
      }
    },
  })
}
