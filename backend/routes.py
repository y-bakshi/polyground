"""
API Routes for Polymarket Analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta, timezone
import httpx
import logging

from database import get_db
from models import User, PinnedMarket, MarketHistory, Alert

logger = logging.getLogger(__name__)
from schemas import (
    PinRequest,
    UnpinRequest,
    PinResponse,
    PinnedMarketsResponse,
    PinnedMarketWithLatest,
    MarketDetail,
    MarketSnapshot,
    AlertResponse,
    AlertsListResponse,
    StatusResponse,
)
from services.polymarket import get_polymarket_service
from services.worker import get_worker

router = APIRouter(prefix="/api", tags=["api"])


# ========== DEPENDENCIES ==========

def get_user(user_id: int, db: Session) -> User:
    """
    Helper function to get user by ID, raises 404 if not found.
    Reusable across endpoints to eliminate duplicate code.
    
    Args:
        user_id: The user ID to look up
        db: Database session
        
    Returns:
        User object if found
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ========== PIN ENDPOINTS ==========

@router.post("/pin", response_model=StatusResponse)
async def pin_market(req: PinRequest, db: Session = Depends(get_db)):
    """
    Pin a market or event for a user.
    Accepts Polymarket URLs, slugs, or numeric IDs.
    Backend resolves all formats automatically.
    """
    # Check if user exists
    user = get_user(req.userId, db)

    # Resolve the input to market/event details
    polymarket = get_polymarket_service()
    market_id, event_id, event_title, is_event = await polymarket.resolve_market_input(req.marketId)

    if not market_id:
        raise HTTPException(
            status_code=400,
            detail=f"Could not resolve '{req.marketId}' to a valid market or event"
        )

    # Check if already pinned
    existing = (
        db.query(PinnedMarket)
        .filter(
            PinnedMarket.user_id == req.userId,
            PinnedMarket.market_id == market_id
        )
        .first()
    )

    if existing:
        return StatusResponse(
            status="ok",
            message="Already pinned"
        )

    # Create new pin
    try:
        new_pin = PinnedMarket(
            user_id=req.userId,
            market_id=market_id,
            is_event=is_event,
            event_id=event_id,
            event_title=event_title,
        )

        db.add(new_pin)
        db.commit()
        db.refresh(new_pin)

        # Generate initial alert for the newly pinned market
        try:
            worker = get_worker()

            # Fetch current market snapshot
            current_snapshot = await polymarket.get_market_snapshot(market_id)

            if current_snapshot:
                # Get the most recent historical data for comparison
                latest_history = (
                    db.query(MarketHistory)
                    .filter(MarketHistory.market_id == market_id)
                    .order_by(desc(MarketHistory.ts))
                    .first()
                )

                # Create initial alert with current market state
                current_prob = current_snapshot.get("implied_prob", 50.0)
                market_title = current_snapshot.get("question", "Unknown Market")

                # If we have historical data, show change from last known point
                if latest_history:
                    old_prob = latest_history.implied_prob
                    change_pct = current_prob - old_prob
                    old_snapshot = {
                        "implied_prob": old_prob,
                        "volume": latest_history.volume
                    }
                else:
                    # For brand new markets with no history, show as 0% change
                    old_prob = current_prob
                    change_pct = 0.0
                    old_snapshot = {
                        "implied_prob": current_prob,
                        "volume": current_snapshot.get("volume", 0)
                    }

                # Create the initial alert
                await worker.create_alert(
                    user_id=req.userId,
                    market_id=market_id,
                    market_title=market_title,
                    old_prob=old_prob,
                    new_prob=current_prob,
                    change_pct=change_pct,
                    old_snapshot=old_snapshot,
                    new_snapshot=current_snapshot,
                    db=db
                )

                logger.info(f"Created initial alert for user {req.userId} on market {market_id}")
        except Exception as alert_error:
            # Don't fail the pin operation if alert creation fails
            logger.warning(f"Failed to create initial alert: {alert_error}")

        pin_type = "event" if is_event else "market"
        return StatusResponse(
            status="ok",
            message=f"Pinned {pin_type} successfully"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to pin market: {str(e)}")


@router.delete("/pin", response_model=StatusResponse)
async def unpin_market(req: UnpinRequest, db: Session = Depends(get_db)):
    """
    Unpin a market for a user.
    """
    pin = (
        db.query(PinnedMarket)
        .filter(
            PinnedMarket.user_id == req.userId,
            PinnedMarket.market_id == req.marketId
        )
        .first()
    )

    if not pin:
        raise HTTPException(status_code=404, detail="Pinned market not found")

    try:
        db.delete(pin)
        db.commit()
        return StatusResponse(
            status="ok",
            message=f"Market {req.marketId} unpinned successfully"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to unpin market: {str(e)}")


# ========== PINNED MARKETS ENDPOINT ==========

@router.get("/pinned", response_model=PinnedMarketsResponse)
async def get_pinned_markets(
    userId: int = Query(..., description="User ID to get pinned markets for"),
    db: Session = Depends(get_db)
):
    """
    Get all pinned markets for a user with their latest data.
    """
    # Check if user exists
    user = get_user(userId, db)

    # Get all pinned markets for user
    pinned = (
        db.query(PinnedMarket)
        .filter(PinnedMarket.user_id == userId)
        .order_by(desc(PinnedMarket.pinned_at))
        .all()
    )

    # For each pinned market, get the latest market data and recent history
    items = []
    for pin in pinned:
        latest_history = (
            db.query(MarketHistory)
            .filter(MarketHistory.market_id == pin.market_id)
            .order_by(desc(MarketHistory.ts))
            .first()
        )

        # Get last 24 hours of history for sparkline and change calculation
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        history_records = (
            db.query(MarketHistory)
            .filter(
                MarketHistory.market_id == pin.market_id,
                MarketHistory.ts >= since
            )
            .order_by(MarketHistory.ts)
            .all()
        )

        # Convert to MarketSnapshot objects
        history_snapshots = [
            MarketSnapshot(
                ts=h.ts,
                implied_prob=h.implied_prob,
                price=h.price,
                volume=h.volume,
                market_title=h.market_title
            )
            for h in history_records
        ]

        # Calculate change percentage from first to last data point
        change_pct = 0.0
        if len(history_records) >= 2:
            first_prob = history_records[0].implied_prob
            last_prob = history_records[-1].implied_prob
            change_pct = last_prob - first_prob

        # For events, use event_title instead of market_title
        display_title = pin.event_title if pin.is_event else (latest_history.market_title if latest_history else None)

        item = PinnedMarketWithLatest(
            id=pin.id,
            user_id=pin.user_id,
            market_id=pin.market_id,
            pinned_at=pin.pinned_at,
            latest_prob=latest_history.implied_prob if latest_history else None,
            latest_price=latest_history.price if latest_history else None,
            latest_volume=latest_history.volume if latest_history else None,
            market_title=display_title,
            history=history_snapshots,
            change_pct=change_pct,
            is_event=pin.is_event,
            event_id=pin.event_id,
            event_title=pin.event_title,
        )
        items.append(item)

    return PinnedMarketsResponse(
        items=items,
        total=len(items)
    )


# ========== MARKET DETAIL ENDPOINT ==========

@router.get("/market/{market_id}", response_model=MarketDetail)
async def get_market_detail(
    market_id: str,
    hours: int = Query(24, description="Number of hours of history to fetch"),
    db: Session = Depends(get_db)
):
    """
    Get market snapshot and historical data for a specific market.
    Returns the latest data point and time-series history.
    """
    # Get time window
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    # Get latest snapshot
    latest = (
        db.query(MarketHistory)
        .filter(MarketHistory.market_id == market_id)
        .order_by(desc(MarketHistory.ts))
        .first()
    )

    # Get historical data
    history = (
        db.query(MarketHistory)
        .filter(
            MarketHistory.market_id == market_id,
            MarketHistory.ts >= since
        )
        .order_by(MarketHistory.ts)
        .all()
    )

    # Convert to response models
    latest_snapshot = None
    if latest:
        latest_snapshot = MarketSnapshot(
            ts=latest.ts,
            implied_prob=latest.implied_prob,
            price=latest.price,
            volume=latest.volume,
            market_title=latest.market_title
        )

    history_snapshots = [
        MarketSnapshot(
            ts=h.ts,
            implied_prob=h.implied_prob,
            price=h.price,
            volume=h.volume,
            market_title=h.market_title
        )
        for h in history
    ]

    return MarketDetail(
        market_id=market_id,
        latest=latest_snapshot,
        history=history_snapshots,
        data_points=len(history_snapshots)
    )


# ========== ALERTS ENDPOINT ==========

@router.get("/alerts", response_model=AlertsListResponse)
async def get_alerts(
    userId: int = Query(..., description="User ID to get alerts for"),
    unread_only: bool = Query(False, description="Only show unread alerts"),
    limit: int = Query(50, description="Maximum number of alerts to return"),
    db: Session = Depends(get_db)
):
    """
    Get alerts for a user, optionally filtered by read/unread status.
    Returns alerts sorted by most recent first.
    """
    # Check if user exists
    user = get_user(userId, db)

    # Build query
    query = db.query(Alert).filter(Alert.user_id == userId)

    if unread_only:
        query = query.filter(Alert.seen == False)

    # Get alerts
    alerts = query.order_by(desc(Alert.ts)).limit(limit).all()

    # Count unread
    unread_count = (
        db.query(Alert)
        .filter(Alert.user_id == userId, Alert.seen == False)
        .count()
    )

    # Convert to response models
    alert_responses = [
        AlertResponse(
            id=alert.id,
            user_id=alert.user_id,
            market_id=alert.market_id,
            ts=alert.ts,
            change_pct=alert.change_pct,
            threshold=alert.threshold,
            market_title=alert.market_title,
            insight_text=alert.insight_text,
            seen=alert.seen
        )
        for alert in alerts
    ]

    return AlertsListResponse(
        alerts=alert_responses,
        total=len(alert_responses),
        unread_count=unread_count
    )


@router.patch("/alerts/{alert_id}/mark-seen", response_model=StatusResponse)
async def mark_alert_seen(alert_id: int, db: Session = Depends(get_db)):
    """
    Mark an alert as seen/read.
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    try:
        alert.seen = True
        db.commit()
        return StatusResponse(
            status="ok",
            message=f"Alert {alert_id} marked as seen"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to mark alert as seen: {str(e)}")


# ========== EVENT ENDPOINT ==========

@router.get("/event/{event_id}")
async def get_event_detail(event_id: str):
    """
    Get event details with all individual markets for multi-outcome events.
    Accepts both numeric event IDs and slugs.
    Returns event metadata and list of all markets within the event.
    """
    polymarket = get_polymarket_service()

    # Try to fetch event data by ID first
    event_data = await polymarket.check_if_event(event_id)

    # If not found and event_id doesn't look like a number, try as slug
    if not event_data and not event_id.isdigit():
        # Try to resolve slug to event
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://gamma-api.polymarket.com/events?slug={event_id}&limit=1"
                )
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        event_data = data[0]
        except Exception as e:
            logger.warning(f"Failed to resolve event slug {event_id}: {e}")

    if not event_data:
        raise HTTPException(status_code=404, detail="Event not found")

    # Extract market information
    markets = event_data.get("markets", [])

    # Format response with complete market data
    return {
        "id": event_data.get("id"),
        "slug": event_data.get("slug"),
        "title": event_data.get("title"),
        "description": event_data.get("description"),
        "end_date": event_data.get("endDate"),
        "start_date": event_data.get("startDate"),
        "active": event_data.get("active"),
        "closed": event_data.get("closed"),
        "volume": event_data.get("volume"),
        "volume_24hr": event_data.get("volume24hr"),
        "liquidity": event_data.get("liquidity"),
        "markets": [
            {
                "id": m.get("id"),
                "slug": m.get("slug"),
                "question": m.get("question"),
                "outcome_prices": m.get("outcomePrices"),  # Array of current odds
                "outcomes": m.get("outcomes"),  # ["Yes", "No"] or custom outcomes
                "active": m.get("active"),
                "closed": m.get("closed"),
                "group_item_title": m.get("groupItemTitle"),
                # Pricing data
                "last_trade_price": m.get("lastTradePrice"),
                "best_bid": m.get("bestBid"),
                "best_ask": m.get("bestAsk"),
                # Volume data
                "volume": m.get("volumeNum"),
                "volume_24hr": m.get("volume24hr"),
                # Price changes
                "one_day_price_change": m.get("oneDayPriceChange"),
                "one_hour_price_change": m.get("oneHourPriceChange"),
                # Liquidity
                "liquidity": m.get("liquidityNum"),
            }
            for m in markets
        ],
        "market_count": len(markets),
    }
