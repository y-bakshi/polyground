/**
 * Extract slug or market ID from Polymarket URL
 * Returns either a numeric market ID or a slug that needs to be resolved
 */
export function extractMarketId(input: string): { marketId?: string; slug?: string; isEvent?: boolean; error?: string } {
  const trimmed = input.trim()

  // If it's not a URL, assume it's already a market ID (numeric)
  if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
    // Check if it's a numeric ID
    if (/^\d+$/.test(trimmed)) {
      return { marketId: trimmed }
    }
    // Otherwise treat it as a slug
    return { slug: trimmed }
  }

  try {
    const url = new URL(trimmed)

    // Check if it's a Polymarket URL
    if (!url.hostname.includes('polymarket.com')) {
      return {
        error: 'Please provide a valid Polymarket URL or market ID'
      }
    }

    // Handle event URLs (multi-outcome events)
    // Example: https://polymarket.com/event/fed-decision-in-october?tid=123
    if (url.pathname.startsWith('/event/')) {
      const parts = url.pathname.split('/').filter(Boolean)
      if (parts.length >= 2) {
        const eventSlug = parts[1] // /event/{slug}
        return { slug: eventSlug, isEvent: true }
      }
    }

    // Handle market URLs
    // Example: https://polymarket.com/market/us-recession-in-2025?tid=123
    if (url.pathname.startsWith('/market/')) {
      const parts = url.pathname.split('/').filter(Boolean)
      if (parts.length >= 2) {
        const marketSlug = parts[1] // /market/{slug}
        return { slug: marketSlug }
      }
    }

    // For any other URL pattern, try to extract from pathname
    const pathParts = url.pathname.split('/').filter(Boolean)
    if (pathParts.length > 0) {
      const lastPart = pathParts[pathParts.length - 1]
      return { slug: lastPart }
    }

    return {
      error: 'Could not extract market slug from URL. Please enter the market ID (e.g., 516710)'
    }
  } catch (error) {
    // Invalid URL, treat as slug or ID
    if (/^\d+$/.test(trimmed)) {
      return { marketId: trimmed }
    }
    return { slug: trimmed }
  }
}

/**
 * Resolve a slug to a market ID using the Polymarket Gamma API
 */
export async function resolveSlugToMarketId(slug: string, isEvent: boolean = false): Promise<string | null> {
  try {
    const endpoint = isEvent ? 'events' : 'markets'
    const response = await fetch(`https://gamma-api.polymarket.com/${endpoint}?slug=${slug}&limit=1`)

    if (!response.ok) {
      console.error('Failed to resolve slug:', response.status)
      return null
    }

    const data = await response.json()

    if (Array.isArray(data) && data.length > 0) {
      return data[0].id
    }

    return null
  } catch (error) {
    console.error('Error resolving slug to market ID:', error)
    return null
  }
}
