"""
Polymarket Service - Fetch market data from Polymarket APIs
"""

import httpx
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timezone
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class PolymarketService:
    """Service for interacting with Polymarket Gamma and CLOB APIs"""

    GAMMA_API_BASE = "https://gamma-api.polymarket.com"
    CLOB_API_BASE = "https://clob.polymarket.com"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def resolve_market_input(self, input_str: str) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
        """
        Resolve a user input (URL, slug, or ID) to market/event details.

        Args:
            input_str: URL, slug, or numeric ID

        Returns:
            Tuple of (market_id, event_id, event_title, is_event)
        """
        input_str = input_str.strip()

        # Check if it's a URL
        if input_str.startswith('http://') or input_str.startswith('https://'):
            parsed = urlparse(input_str)

            # Check if it's a Polymarket URL
            if 'polymarket.com' not in parsed.hostname:
                return (None, None, None, False)

            # Extract path segments
            path_parts = [p for p in parsed.path.split('/') if p]

            if len(path_parts) < 2:
                return (None, None, None, False)

            path_type = path_parts[0]  # 'event' or 'market'
            slug = path_parts[1]

            # Resolve based on type
            if path_type == 'event':
                return await self._resolve_event_slug(slug)
            elif path_type == 'market':
                return await self._resolve_market_slug(slug)

        # If it's numeric, assume it's a market ID
        if input_str.isdigit():
            return (input_str, None, None, False)

        # Otherwise, try as a slug (market first, then event)
        result = await self._resolve_market_slug(input_str)
        if result[0]:
            return result

        return await self._resolve_event_slug(input_str)

    async def _resolve_market_slug(self, slug: str) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
        """Resolve a market slug to market ID."""
        try:
            url = f"{self.GAMMA_API_BASE}/markets"
            params = {"slug": slug, "limit": 1}
            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    market = data[0]
                    return (market.get('id'), None, None, False)
        except Exception as e:
            logger.error(f"Error resolving market slug {slug}: {e}")

        return (None, None, None, False)

    async def _resolve_event_slug(self, slug: str) -> Tuple[Optional[str], Optional[str], Optional[str], bool]:
        """Resolve an event slug to event ID, market ID, and event title."""
        try:
            url = f"{self.GAMMA_API_BASE}/events"
            params = {"slug": slug, "limit": 1}
            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    event = data[0]
                    event_id = event.get('id')
                    event_title = event.get('title')

                    # Get first active market
                    markets = event.get('markets', [])
                    if markets:
                        # Find first active, non-closed market
                        active_market = next(
                            (m for m in markets if m.get('active') and not m.get('closed')),
                            markets[0]  # Fallback to first market
                        )
                        market_id = active_market.get('id')
                        return (market_id, event_id, event_title, True)
        except Exception as e:
            logger.error(f"Error resolving event slug {slug}: {e}")

        return (None, None, None, False)

    async def check_if_event(self, id_str: str) -> Optional[Dict[str, Any]]:
        """
        Check if an ID corresponds to a multi-outcome event.

        Args:
            id_str: The ID to check

        Returns:
            Event data if it's an event, None otherwise
        """
        try:
            # Try direct event endpoint
            url = f"{self.GAMMA_API_BASE}/events/{id_str}"
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()

            # Try searching by numeric ID in events
            url = f"{self.GAMMA_API_BASE}/events"
            params = {"id": id_str}
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0]

            return None

        except Exception as e:
            logger.debug(f"Not an event: {id_str}")
            return None

    async def get_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch market data from Gamma API by market ID.

        Args:
            market_id: The Polymarket market ID

        Returns:
            Market data dictionary or None if not found
        """
        try:
            url = f"{self.GAMMA_API_BASE}/markets/{market_id}"
            response = await self.client.get(url)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Market {market_id} not found")
                return None
            else:
                logger.error(f"Error fetching market {market_id}: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Exception fetching market {market_id}: {e}")
            return None

    async def search_markets(
        self,
        limit: int = 10,
        offset: int = 0,
        active: Optional[bool] = None,
        closed: Optional[bool] = None,
        order: str = "volume24hr",
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for markets using Gamma API.

        Args:
            limit: Maximum number of results
            offset: Pagination offset
            active: Filter by active status
            closed: Filter by closed status
            order: Field to order by (volume24hr, createdAt, etc.)
            ascending: Sort ascending if True, descending if False

        Returns:
            List of market data dictionaries
        """
        try:
            params = {
                "limit": limit,
                "offset": offset,
                "order": order,
                "direction": "ASC" if ascending else "DESC"
            }

            if active is not None:
                params["active"] = str(active).lower()
            if closed is not None:
                params["closed"] = str(closed).lower()

            url = f"{self.GAMMA_API_BASE}/markets"
            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error searching markets: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Exception searching markets: {e}")
            return []

    async def get_last_trade_price(self, token_id: str) -> Optional[float]:
        """
        Get the last trade price for a token from CLOB API.

        Args:
            token_id: The CLOB token ID

        Returns:
            Last trade price or None if not available
        """
        try:
            url = f"{self.CLOB_API_BASE}/prices-history"
            params = {"market": token_id, "interval": "max", "fidelity": "1"}

            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if data and "history" in data and len(data["history"]) > 0:
                    # Get the most recent price
                    latest = data["history"][-1]
                    return float(latest.get("p", 0))
                return None
            else:
                logger.error(f"Error fetching price for token {token_id}: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Exception fetching price for token {token_id}: {e}")
            return None

    async def get_market_snapshot(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a complete snapshot of a market including price data.

        This combines data from Gamma API (market info) and CLOB API (prices).

        Args:
            market_id: The Polymarket market ID

        Returns:
            Dictionary with market snapshot data or None if error
        """
        try:
            # Get market metadata from Gamma
            market = await self.get_market(market_id)
            if not market:
                return None

            # Extract key information
            snapshot = {
                "market_id": market_id,
                "question": market.get("question"),
                "outcomes": market.get("outcomes"),
                "end_date": market.get("endDate"),
                "closed": market.get("closed", False),
                "volume_24hr": market.get("volume24hrClob", 0),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

            # Try to get price data if token IDs are available
            clob_token_ids = market.get("clobTokenIds")
            if clob_token_ids:
                # Parse token IDs (they might be stored as JSON string)
                if isinstance(clob_token_ids, str):
                    import json
                    try:
                        clob_token_ids = json.loads(clob_token_ids)
                    except:
                        clob_token_ids = None

                if clob_token_ids and len(clob_token_ids) > 0:
                    # Get price for the first outcome (typically "Yes")
                    token_id = clob_token_ids[0]
                    price = await self.get_last_trade_price(token_id)

                    if price is not None:
                        snapshot["price"] = price
                        snapshot["implied_prob"] = price * 100  # Convert to percentage

            # Fallback: use lastTradePrice if available
            if "price" not in snapshot:
                last_price = market.get("lastTradePrice", 0)
                if last_price > 0:
                    snapshot["price"] = last_price
                    snapshot["implied_prob"] = last_price * 100
                else:
                    # Default values if no price data available
                    snapshot["price"] = 0.5
                    snapshot["implied_prob"] = 50.0

            snapshot["volume"] = market.get("volume24hrClob", 0)

            return snapshot

        except Exception as e:
            logger.error(f"Exception getting market snapshot for {market_id}: {e}")
            return None


# Singleton instance
_polymarket_service: Optional[PolymarketService] = None


def get_polymarket_service() -> PolymarketService:
    """Get or create the Polymarket service instance"""
    global _polymarket_service
    if _polymarket_service is None:
        _polymarket_service = PolymarketService()
    return _polymarket_service
