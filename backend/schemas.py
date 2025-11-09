"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Pin market schemas
class PinRequest(BaseModel):
    userId: int = Field(..., description="User ID")
    marketId: str = Field(..., description="Polymarket market ID")


class UnpinRequest(BaseModel):
    userId: int = Field(..., description="User ID")
    marketId: str = Field(..., description="Polymarket market ID")


class PinResponse(BaseModel):
    id: int
    user_id: int
    market_id: str
    pinned_at: datetime

    class Config:
        from_attributes = True


# Market history schemas
class MarketSnapshot(BaseModel):
    ts: datetime
    implied_prob: float
    price: float
    volume: float
    market_title: Optional[str] = None

    class Config:
        from_attributes = True


class MarketDetail(BaseModel):
    market_id: str
    latest: Optional[MarketSnapshot] = None
    history: List[MarketSnapshot] = []
    data_points: int = 0


# Alert schemas
class AlertResponse(BaseModel):
    id: int
    user_id: int
    market_id: str
    ts: datetime
    change_pct: float
    threshold: float
    market_title: Optional[str] = None
    insight_text: Optional[str] = None
    seen: bool

    class Config:
        from_attributes = True


class AlertsListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    unread_count: int


# Pinned markets list response
class PinnedMarketWithLatest(BaseModel):
    id: int
    user_id: int
    market_id: str
    pinned_at: datetime
    latest_prob: Optional[float] = None
    latest_price: Optional[float] = None
    latest_volume: Optional[float] = None
    market_title: Optional[str] = None
    history: List[MarketSnapshot] = []  # Historical data for sparkline and change calculation

    class Config:
        from_attributes = True


class PinnedMarketsResponse(BaseModel):
    items: List[PinnedMarketWithLatest]
    total: int


# Generic response
class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
