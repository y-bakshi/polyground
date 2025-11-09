import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_ROOT))

os.environ["DATABASE_URL"] = "sqlite:///./test_api.db"
os.environ["ENABLE_WORKER"] = "false"

from fastapi.testclient import TestClient
import pytest

from main import app
from database import SessionLocal, init_db, drop_db
from models import User, PinnedMarket, MarketHistory, Alert
import routes


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Remove the temporary SQLite file after the test session."""
    yield
    db_path = "./test_api.db"
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def db_session():
    """Reset the database and seed deterministic fixtures for each test."""
    drop_db()
    init_db()
    db = SessionLocal()

    user = User(email="tester@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)

    pinned = PinnedMarket(user_id=user.id, market_id="market-abc")
    db.add(pinned)
    db.commit()

    now = datetime.utcnow()
    history_entries = [
        MarketHistory(
            market_id="market-abc",
            ts=now - timedelta(minutes=30),
            implied_prob=48.0,
            price=0.48,
            volume=15000,
            market_title="Test Market",
        ),
        MarketHistory(
            market_id="market-abc",
            ts=now,
            implied_prob=55.0,
            price=0.55,
            volume=17500,
            market_title="Test Market",
        ),
    ]
    db.add_all(history_entries)

    alert = Alert(
        user_id=user.id,
        market_id="market-abc",
        change_pct=7.0,
        threshold=5.0,
        insight_text="Sample insight",
        seen=False,
    )
    db.add(alert)
    db.commit()

    yield {"session": db, "user_id": user.id, "market_id": pinned.market_id}

    db.close()


@pytest.fixture
def client(db_session):
    """Provide a FastAPI test client with seeded database state."""
    with TestClient(app) as test_client:
        yield test_client


def test_pin_market_creates_new_record(client, db_session):
    response = client.post(
        "/api/pin",
        json={"userId": db_session["user_id"], "marketId": "market-new"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"

    db = db_session["session"]
    stored = (
        db.query(PinnedMarket)
        .filter(
            PinnedMarket.user_id == db_session["user_id"],
            PinnedMarket.market_id == "market-new",
        )
        .first()
    )
    assert stored is not None


def test_get_pinned_markets_returns_latest_snapshot(client, db_session):
    response = client.get(f"/api/pinned?userId={db_session['user_id']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1

    pinned = payload["items"][0]
    assert pinned["market_id"] == db_session["market_id"]
    assert pinned["latest_prob"] == pytest.approx(55.0)
    assert pinned["latest_volume"] == 17500
    assert pinned["market_title"] == "Test Market"


def test_event_endpoint_returns_sub_markets(client, monkeypatch):
    class FakePolymarketService:
        async def check_if_event(self, event_id: str):
            return {
                "id": event_id,
                "title": "Demo Event",
                "description": "Example multi-market event",
                "endDate": "2025-01-01T00:00:00Z",
                "active": True,
                "closed": False,
                "volume24hr": 12345,
                "markets": [
                    {
                        "id": "sub-1",
                        "question": "Will it rain?",
                        "outcomePrices": [0.45, 0.55],
                        "active": True,
                        "closed": False,
                        "groupItemTitle": "Rain",
                    },
                    {
                        "id": "sub-2",
                        "question": "Will it snow?",
                        "outcomePrices": [0.30, 0.70],
                        "active": False,
                        "closed": True,
                        "groupItemTitle": "Snow",
                    },
                ],
            }

    monkeypatch.setattr(routes, "get_polymarket_service", lambda: FakePolymarketService())

    response = client.get("/api/event/demo-event")

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Demo Event"
    assert payload["market_count"] == 2
    assert len(payload["markets"]) == 2
    assert payload["markets"][0]["id"] == "sub-1"


def test_event_endpoint_with_slug(client, monkeypatch):
    """Test event endpoint with MrBeast-style slug"""
    class FakePolymarketService:
        async def check_if_event(self, event_id: str):
            # Simulate that slug-based lookup returns event data
            if "mrbeast" in event_id.lower() or event_id == "of-views-of-next-mrbeast-video-on-day-1-764":
                return {
                    "id": "764",
                    "slug": "of-views-of-next-mrbeast-video-on-day-1-764",
                    "title": "# of views of next MrBeast video on day 1",
                    "description": "Multi-outcome event for MrBeast video views",
                    "endDate": "2025-12-31T00:00:00Z",
                    "active": True,
                    "closed": False,
                    "volume24hr": 50000,
                    "markets": [
                        {
                            "id": "market-1",
                            "question": "Will it get over 50M views?",
                            "outcomePrices": [0.65, 0.35],
                            "active": True,
                            "closed": False,
                            "groupItemTitle": "Over 50M",
                        },
                        {
                            "id": "market-2",
                            "question": "Will it get 40-50M views?",
                            "outcomePrices": [0.25, 0.75],
                            "active": True,
                            "closed": False,
                            "groupItemTitle": "40-50M",
                        },
                        {
                            "id": "market-3",
                            "question": "Will it get under 40M views?",
                            "outcomePrices": [0.10, 0.90],
                            "active": True,
                            "closed": False,
                            "groupItemTitle": "Under 40M",
                        },
                    ],
                }
            return None

    monkeypatch.setattr(routes, "get_polymarket_service", lambda: FakePolymarketService())

    # Test with the full slug from the URL
    response = client.get("/api/event/of-views-of-next-mrbeast-video-on-day-1-764")

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "# of views of next MrBeast video on day 1"
    assert payload["market_count"] == 3
    assert len(payload["markets"]) == 3
    assert payload["markets"][0]["question"] == "Will it get over 50M views?"
    assert payload["markets"][1]["question"] == "Will it get 40-50M views?"
