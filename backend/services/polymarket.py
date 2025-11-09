"""
Polymarket Service - Fetch market data from Polymarket APIs
"""

import httpx
from typing import Optional, Dict, List, Any
from datetime import datetime
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

    async def check_if_event(self, id_str: str) -> Optional[Dict[str, Any]]:
        """
        Check if an ID/slug corresponds to a multi-outcome event.

        Supports both numeric IDs and slug-based lookups (e.g., from URLs).

        Args:
            id_str: The ID or slug to check (e.g., "764" or "of-views-of-next-mrbeast-video-on-day-1-764")

        Returns:
            Event data if it's an event, None otherwise
        """
        try:
            # Try slug-based lookup first (handles URL slugs)
            url = f"{self.GAMMA_API_BASE}/events"
            params = {"slug": id_str}
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"Found event by slug: {id_str}")
                    return data[0]

            # Try numeric ID lookup
            params = {"id": id_str}
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    logger.info(f"Found event by ID: {id_str}")
                    return data[0]

            # Try direct endpoint (legacy support)
            url = f"{self.GAMMA_API_BASE}/events/{id_str}"
            response = await self.client.get(url)
            if response.status_code == 200:
                logger.info(f"Found event by direct endpoint: {id_str}")
                return response.json()

            logger.debug(f"Event not found: {id_str}")
            return None

        except Exception as e:
            logger.error(f"Error checking event {id_str}: {e}")
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
                "fetched_at": datetime.utcnow().isoformat(),
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
