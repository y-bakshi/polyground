/**
 * Extract market ID from Polymarket URL or return the input if it's already an ID
 */
export function extractMarketId(input: string): { marketId: string; error?: string } {
  const trimmed = input.trim()

  // If it's not a URL, assume it's already a market ID
  if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
    return { marketId: trimmed }
  }

  try {
    const url = new URL(trimmed)

    // Check if it's a Polymarket URL
    if (!url.hostname.includes('polymarket.com')) {
      return {
        marketId: '',
        error: 'Please provide a valid Polymarket URL or market ID'
      }
    }

    // Check if it's an event URL (multi-outcome)
    if (url.pathname.startsWith('/event/')) {
      return {
        marketId: '',
        error: 'This is a multi-outcome event. Please share an individual market link instead.'
      }
    }

    // Extract market ID from /market/ URLs
    if (url.pathname.startsWith('/market/')) {
      const parts = url.pathname.split('/')
      const marketSlug = parts[2] // /market/{slug}

      // Extract numeric ID if present at the end of slug
      const match = marketSlug.match(/-(\d+)$/)
      if (match) {
        return { marketId: match[1] }
      }

      // Otherwise return the full slug
      return { marketId: marketSlug }
    }

    // For any other URL pattern, try to extract a numeric ID
    const pathMatch = url.pathname.match(/\/(\d+)/)
    if (pathMatch) {
      return { marketId: pathMatch[1] }
    }

    return {
      marketId: '',
      error: 'Could not extract market ID from URL. Please enter just the market ID (e.g., 516710)'
    }
  } catch (error) {
    // Invalid URL, return as-is (might be a market ID)
    return { marketId: trimmed }
  }
}
