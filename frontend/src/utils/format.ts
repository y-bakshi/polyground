const percentFormatter = new Intl.NumberFormat('en-US', {
  style: 'percent',
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
})

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
})

export const formatPercent = (value: number) => percentFormatter.format(value / 100)

export const formatDateTime = (isoDate: string) => {
  try {
    return dateFormatter.format(new Date(isoDate))
  } catch (error) {
    console.warn('Failed to format date', error)
    return isoDate
  }
}
