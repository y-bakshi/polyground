import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { EventDetail } from '../api/types'

export const useEventDetails = (eventId: string | undefined) =>
  useQuery<EventDetail>({
    queryKey: ['event', eventId],
    queryFn: () => apiClient.getEventDetail(eventId as string),
    enabled: Boolean(eventId),
    refetchInterval: 120_000,
    retry: false, // Don't retry if it's not an event
  })
