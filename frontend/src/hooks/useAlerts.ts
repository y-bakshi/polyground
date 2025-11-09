import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { AlertItem } from '../api/types'
import { DEMO_USER_ID } from '../config/constants'

export const alertsKey = ['alerts', DEMO_USER_ID]

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

export const useMarkAlertSeen = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (alertId: string) => apiClient.markAlertSeen(alertId),
    onMutate: async (alertId: string) => {
      await queryClient.cancelQueries({ queryKey: alertsKey })
      const previousAlerts = queryClient.getQueryData<AlertItem[]>(alertsKey)

      queryClient.setQueryData<AlertItem[]>(alertsKey, (current) => {
        if (!current) return current
        return current.map((alert) =>
          alert.id === alertId ? { ...alert, seen: true } : alert,
        )
      })

      return { previousAlerts }
    },
    onError: (_error, _variables, context) => {
      if (context?.previousAlerts) {
        queryClient.setQueryData(alertsKey, context.previousAlerts)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: alertsKey })
    },
  })
}
