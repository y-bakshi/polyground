import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { AlertItem } from '../api/types'
import { DEMO_USER_ID } from '../config/constants'

const alertsKey = ['alerts', DEMO_USER_ID]

export const useAlerts = () =>
  useQuery<AlertItem[]>({
    queryKey: alertsKey,
    queryFn: () => apiClient.getAlerts(DEMO_USER_ID),
    refetchInterval: 45_000,
  })

export const useUnreadAlertCount = () => {
  const { data } = useAlerts()
  return data?.filter((alert) => !alert.seen).length ?? 0
}
