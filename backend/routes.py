"""
API Routes for Polymarket Analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timedelta

from database import get_db
from models import User, PinnedMarket, MarketHistory, Alert
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

router = APIRouter(prefix="/api", tags=["api"])


# ========== PIN ENDPOINTS ==========

@router.post("/pin", response_model=StatusResponse)
async def pin_market(req: PinRequest, db: Session = Depends(get_db)):
    """
    Pin a market or event for a user.
    Creates a new pinned market entry if it doesn't already exist.
    Accepts both individual market IDs and multi-outcome event IDs.
    """
    # Check if user exists
    user = db.query(User).filter(User.id == req.userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already pinned
    existing = (
        db.query(PinnedMarket)
        .filter(
            PinnedMarket.user_id == req.userId,
            PinnedMarket.market_id == req.marketId
        )
        .first()
    )

    if existing:
        return StatusResponse(
            status="ok",
            message="Already pinned"
        )

    # Create new pin
    new_pin = PinnedMarket(
        user_id=req.userId,
        market_id=req.marketId,
    )

    db.add(new_pin)
    db.commit()
    db.refresh(new_pin)

    return StatusResponse(
        status="ok",
        message=f"Pinned successfully"
    )


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

    db.delete(pin)
    db.commit()

    return StatusResponse(
        status="ok",
        message=f"Market {req.marketId} unpinned successfully"
    )


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
    user = db.query(User).filter(User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all pinned markets for user
    pinned = (
        db.query(PinnedMarket)
        .filter(PinnedMarket.user_id == userId)
        .order_by(desc(PinnedMarket.pinned_at))
        .all()
    )

    # For each pinned market, get the latest market data
    items = []
    for pin in pinned:
        latest_history = (
            db.query(MarketHistory)
            .filter(MarketHistory.market_id == pin.market_id)
            .order_by(desc(MarketHistory.ts))
            .first()
        )

        item = PinnedMarketWithLatest(
            id=pin.id,
            user_id=pin.user_id,
            market_id=pin.market_id,
            pinned_at=pin.pinned_at,
            latest_prob=latest_history.implied_prob if latest_history else None,
            latest_price=latest_history.price if latest_history else None,
            latest_volume=latest_history.volume if latest_history else None,
            market_title=latest_history.market_title if latest_history else None,
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
    since = datetime.utcnow() - timedelta(hours=hours)

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
    user = db.query(User).filter(User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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

    alert.seen = True
    db.commit()

    return StatusResponse(
        status="ok",
        message=f"Alert {alert_id} marked as seen"
    )


# ========== EVENT ENDPOINT ==========

@router.get("/event/{event_id}")
async def get_event_detail(event_id: str):
    """
    Get event details with all individual markets for multi-outcome events.
    Returns event metadata and list of all markets within the event.
    """
    polymarket = get_polymarket_service()

    # Try to fetch event data
    event_data = await polymarket.check_if_event(event_id)

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
