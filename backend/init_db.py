"""
Database initialization script.

Run this script to:
1. Create all database tables
2. Optionally seed with test data

Usage:
    python init_db.py              # Just create tables
    python init_db.py --seed       # Create tables and add test data
    python init_db.py --reset      # Drop all tables and recreate
"""

import argparse
from database import init_db, drop_db, SessionLocal
from models import User, PinnedMarket, MarketHistory, Alert
from datetime import datetime, timedelta, timezone


def seed_test_data():
    """Add some test data for development"""
    db = SessionLocal()

    try:
        # Create test user
        test_user = User(email="test@example.com")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        print(f"✓ Created test user: {test_user.email} (ID: {test_user.id})")

        # Create some pinned markets (using example Polymarket market IDs)
        pinned_markets = [
            PinnedMarket(
                user_id=test_user.id,
                market_id="0x1234567890abcdef",  # Example market ID
            ),
            PinnedMarket(
                user_id=test_user.id,
                market_id="0xfedcba0987654321",  # Example market ID
            ),
        ]

        db.add_all(pinned_markets)
        db.commit()

        print(f"✓ Created {len(pinned_markets)} pinned markets")

        # Create some market history data points
        base_time = datetime.now(timezone.utc) - timedelta(hours=2)
        history_entries = []

        for i in range(12):  # 12 data points over 2 hours (every 10 minutes)
            ts = base_time + timedelta(minutes=i * 10)

            # Simulate some price movement
            prob1 = 45 + (i * 2)  # Gradual increase
            prob2 = 60 - (i * 1.5)  # Gradual decrease

            history_entries.extend([
                MarketHistory(
                    market_id="0x1234567890abcdef",
                    ts=ts,
                    implied_prob=prob1,
                    price=prob1 / 100,
                    volume=10000 + (i * 500),
                    market_title="Will Bitcoin hit $100k by end of year?"
                ),
                MarketHistory(
                    market_id="0xfedcba0987654321",
                    ts=ts,
                    implied_prob=prob2,
                    price=prob2 / 100,
                    volume=5000 + (i * 300),
                    market_title="Will the Fed cut rates in Q1 2025?"
                ),
            ])

        db.add_all(history_entries)
        db.commit()

        print(f"✓ Created {len(history_entries)} market history entries")

        # Create a test alert
        test_alert = Alert(
            user_id=test_user.id,
            market_id="0x1234567890abcdef",
            change_pct=15.5,
            threshold=10.0,
            market_title="Will Bitcoin hit $100k by end of year?",
            insight_text="Sample insight: The market has moved significantly due to recent news. "
                         "Risk 1: High volatility expected. Risk 2: Low liquidity. "
                         "Note: This is for informational purposes only.",
            seen=False
        )

        db.add(test_alert)
        db.commit()

        print(f"✓ Created test alert (ID: {test_alert.id})")

        print("\n✅ Test data seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Initialize the database")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed the database with test data"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables and recreate (WARNING: deletes all data!)"
    )

    args = parser.parse_args()

    if args.reset:
        print("⚠️  Dropping all tables...")
        drop_db()
        print()

    print("Creating database tables...")
    init_db()

    if args.seed:
        print("\nSeeding test data...")
        seed_test_data()

    print("\n✅ Database initialization complete!")
    print(f"\nDatabase file: polymarket_analytics.db")


if __name__ == "__main__":
    main()
