from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User table - simplified for hackathon MVP"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pinned_markets = relationship("PinnedMarket", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")


class PinnedMarket(Base):
    """Stores user's pinned markets"""
    __tablename__ = "pinned_markets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    market_id = Column(String, nullable=False, index=True)  # Polymarket market ID
    pinned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="pinned_markets")

    # Composite unique constraint to prevent duplicate pins
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class MarketHistory(Base):
    """Time-series data for market snapshots"""
    __tablename__ = "market_history"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(String, nullable=False, index=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)

    # Market data
    implied_prob = Column(Float, nullable=False)  # Implied probability (0-100)
    price = Column(Float, nullable=False)  # Current price
    volume = Column(Float, default=0.0)  # Trading volume

    # Additional metadata (optional)
    market_title = Column(String, nullable=True)

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class Alert(Base):
    """Alerts triggered by significant market changes"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    market_id = Column(String, nullable=False, index=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)

    # Alert trigger data
    change_pct = Column(Float, nullable=False)  # Percentage change that triggered alert
    threshold = Column(Float, nullable=False)  # Threshold that was exceeded

    # Claude-generated insight
    insight_text = Column(Text, nullable=True)

    # User interaction
    seen = Column(Boolean, default=False, index=True)

    # Relationships
    user = relationship("User", back_populates="alerts")

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
