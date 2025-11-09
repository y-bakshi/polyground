"""
Polling Worker - Periodically fetch market data, detect changes, and create alerts
"""

import asyncio
import os
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from database import SessionLocal
from models import PinnedMarket, MarketHistory, Alert, User
from services.polymarket import get_polymarket_service
from services.insight import get_insight_service

logger = logging.getLogger(__name__)


class MarketPollingWorker:
    """Worker that polls Polymarket for pinned markets and creates alerts"""

    def __init__(
        self,
        poll_interval_sec: int = 300,  # 5 minutes default
        alert_threshold_pct: float = 10.0,  # 10% change threshold
        window_minutes: int = 60  # Look back 1 hour for comparison
    ):
        """
        Initialize the polling worker.

        Args:
            poll_interval_sec: How often to poll (in seconds)
            alert_threshold_pct: Threshold for triggering alerts (percentage change)
            window_minutes: Time window to compare for detecting changes
        """
        self.poll_interval = poll_interval_sec
        self.alert_threshold = alert_threshold_pct
        self.window_minutes = window_minutes

        self.polymarket = get_polymarket_service()
        self.insight_service = get_insight_service()

        logger.info(
            f"MarketPollingWorker initialized: "
            f"interval={poll_interval_sec}s, threshold={alert_threshold_pct}%, "
            f"window={window_minutes}min"
        )

    async def poll_market(self, market_id: str, db: Session) -> bool:
        """
        Poll a single market, store history, and check for alerts.

        Args:
            market_id: The Polymarket market ID
            db: Database session

        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch current market snapshot
            snapshot = await self.polymarket.get_market_snapshot(market_id)
            if not snapshot:
                logger.warning(f"Failed to fetch snapshot for market {market_id}")
                return False

            market_title = snapshot.get("question", "Unknown Market")
            implied_prob = snapshot.get("implied_prob", 50.0)
            price = snapshot.get("price", 0.5)
            volume = snapshot.get("volume", 0)

            # Store in market history
            history_entry = MarketHistory(
                market_id=market_id,
                ts=datetime.utcnow(),
                implied_prob=implied_prob,
                price=price,
                volume=volume,
                market_title=market_title
            )
            db.add(history_entry)
            db.commit()

            logger.info(
                f"Stored history for {market_id}: "
                f"prob={implied_prob:.1f}%, vol={volume:.0f}"
            )

            # Check for alerts by comparing with historical data
            await self.check_for_alerts(market_id, snapshot, db)

            return True

        except Exception as e:
            logger.error(f"Error polling market {market_id}: {e}")
            db.rollback()
            return False

    async def check_for_alerts(
        self,
        market_id: str,
        current_snapshot: dict,
        db: Session
    ):
        """
        Check if the market has changed significantly and create alerts.

        Args:
            market_id: The market ID
            current_snapshot: Current market snapshot
            db: Database session
        """
        try:
            # Get historical data from the window
            window_start = datetime.utcnow() - timedelta(minutes=self.window_minutes)

            old_history = (
                db.query(MarketHistory)
                .filter(
                    MarketHistory.market_id == market_id,
                    MarketHistory.ts >= window_start
                )
                .order_by(MarketHistory.ts)
                .first()
            )

            if not old_history:
                logger.debug(f"No historical data for market {market_id} in window")
                return

            # Calculate change
            old_prob = old_history.implied_prob
            new_prob = current_snapshot.get("implied_prob", 50.0)
            change_pct = abs(new_prob - old_prob)

            # Check if threshold exceeded
            if change_pct >= self.alert_threshold:
                logger.info(
                    f"Alert triggered for {market_id}: "
                    f"{old_prob:.1f}% -> {new_prob:.1f}% "
                    f"(Δ {change_pct:+.1f}%)"
                )

                # Get all users who have this market pinned
                pinned_users = (
                    db.query(PinnedMarket)
                    .filter(PinnedMarket.market_id == market_id)
                    .all()
                )

                # Create alerts for each user
                for pinned in pinned_users:
                    await self.create_alert(
                        user_id=pinned.user_id,
                        market_id=market_id,
                        market_title=current_snapshot.get("question", "Unknown"),
                        old_prob=old_prob,
                        new_prob=new_prob,
                        change_pct=new_prob - old_prob,  # Signed change
                        old_snapshot={
                            "implied_prob": old_prob,
                            "volume": old_history.volume
                        },
                        new_snapshot=current_snapshot,
                        db=db
                    )

        except Exception as e:
            logger.error(f"Error checking alerts for {market_id}: {e}")

    async def create_alert(
        self,
        user_id: int,
        market_id: str,
        market_title: str,
        old_prob: float,
        new_prob: float,
        change_pct: float,
        old_snapshot: dict,
        new_snapshot: dict,
        db: Session
    ):
        """
        Create an alert with Claude-generated insight.

        Args:
            user_id: User to alert
            market_id: Market ID
            market_title: Market title/question
            old_prob: Old probability
            new_prob: New probability
            change_pct: Signed percentage change
            old_snapshot: Old market snapshot
            new_snapshot: New market snapshot
            db: Database session
        """
        try:
            # Generate insight using Claude
            insight_text = self.insight_service.generate_insight_from_history(
                market_title=market_title,
                old_snapshot=old_snapshot,
                new_snapshot=new_snapshot,
                window_minutes=self.window_minutes,
                time_to_resolution=None  # TODO: Calculate from market end_date
            )

            # Create alert
            alert = Alert(
                user_id=user_id,
                market_id=market_id,
                ts=datetime.utcnow(),
                change_pct=change_pct,
                threshold=self.alert_threshold,
                insight_text=insight_text,
                seen=False
            )

            db.add(alert)
            db.commit()

            logger.info(
                f"Created alert for user {user_id}: "
                f"{market_title[:40]}... ({change_pct:+.1f}%)"
            )

        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            db.rollback()

    async def poll_all_markets(self):
        """Poll all pinned markets across all users"""
        db = SessionLocal()

        try:
            # Get all unique pinned market IDs
            pinned_markets = (
                db.query(PinnedMarket.market_id)
                .distinct()
                .all()
            )

            market_ids = [pm.market_id for pm in pinned_markets]

            if not market_ids:
                logger.info("No pinned markets to poll")
                return

            logger.info(f"Polling {len(market_ids)} pinned markets")

            # Poll each market
            for market_id in market_ids:
                await self.poll_market(market_id, db)

            logger.info(f"Completed polling {len(market_ids)} markets")

        except Exception as e:
            logger.error(f"Error in poll_all_markets: {e}")
        finally:
            db.close()

    async def run_once(self):
        """Run one polling cycle (for testing)"""
        await self.poll_all_markets()

    async def start(self):
        """Start the polling loop"""
        logger.info("Starting market polling worker")

        while True:
            try:
                await self.poll_all_markets()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry


# Singleton instance
_worker: Optional[MarketPollingWorker] = None


def get_worker(
    poll_interval_sec: Optional[int] = None,
    alert_threshold_pct: Optional[float] = None
) -> MarketPollingWorker:
    """Get or create the worker instance"""
    global _worker

    if _worker is None:
        # Get config from environment
        interval = poll_interval_sec or int(os.getenv("POLL_INTERVAL_SEC", "300"))
        threshold = alert_threshold_pct or float(os.getenv("ALERT_THRESHOLD_PCT", "10.0"))

        _worker = MarketPollingWorker(
            poll_interval_sec=interval,
            alert_threshold_pct=threshold
        )

    return _worker
