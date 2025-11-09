export function extractMarketId(input) {
  const trimmed = input.trim()

  if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
    return { marketId: trimmed }
  }

  try {
    const url = new URL(trimmed)

    if (!url.hostname.includes('polymarket.com')) {
      return {
        marketId: '',
        error: 'Please provide a valid Polymarket URL or market ID',
      }
    }

    if (url.pathname.startsWith('/event/')) {
      const parts = url.pathname.split('/')
      const eventSlug = parts[2]
      const match = eventSlug.match(/-(\d+)$/)
      if (match) {
        return { marketId: match[1], isEvent: true }
      }
      return { marketId: eventSlug, isEvent: true }
    }

    if (url.pathname.startsWith('/market/')) {
      const parts = url.pathname.split('/')
      const marketSlug = parts[2]
      const match = marketSlug.match(/-(\d+)$/)
      if (match) {
        return { marketId: match[1] }
      }
      return { marketId: marketSlug }
    }

    const pathMatch = url.pathname.match(/\/(\d+)/)
    if (pathMatch) {
      return { marketId: pathMatch[1] }
    }

    return {
      marketId: '',
      error: 'Could not extract market ID. Paste the numeric ID (e.g., 516710)',
    }
  } catch (error) {
    return { marketId: trimmed }
  }
}
