# Frontend-Backend Integration Guide

This document describes how the frontend and backend are integrated in the asuHacks project.

## Overview

The project consists of two main components:
- **Frontend**: React + TypeScript + Vite application (Polymarket Scout dashboard)
- **Backend**: FastAPI + SQLAlchemy + SQLite API server

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│                   http://localhost:5173                     │
│  - React Query for state management                         │
│  - Auto-refresh: pinned markets (60s), alerts (45s)         │
│  - Mock data fallback for offline development               │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API (CORS enabled)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│                   http://localhost:8000                     │
│  - SQLite database with SQLAlchemy ORM                      │
│  - Background worker for market polling                     │
│  - Claude AI integration for insights                       │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     ┌─────────┐           ┌──────────────┐
     │Polymarket│          │  Claude API  │
     │   API   │          │   (Insights) │
     └─────────┘          └──────────────┘
```

## API Endpoints

### Pin/Unpin Management
- **POST** `/api/pin` - Pin a market for a user
  - Request: `{userId: int, marketId: str}`
  - Response: `{status: str, message: str}`

- **DELETE** `/api/pin` - Unpin a market
  - Request: `{userId: int, marketId: str}`
  - Response: `{status: str, message: str}`

### Market Data
- **GET** `/api/pinned?userId={id}` - Get all pinned markets with latest data
  - Response: `{items: PinnedMarket[], total: int}`

- **GET** `/api/market/{marketId}?hours={hours}` - Get market snapshot and history
  - Response: `{market_id: str, latest: MarketSnapshot, history: MarketSnapshot[], data_points: int}`

- **GET** `/api/event/{eventId}` - Get event details with all constituent markets
  - Response: `EventDetail` object with markets array

### Alerts
- **GET** `/api/alerts?userId={id}&unread_only={bool}&limit={limit}` - Get user alerts
  - Response: `{alerts: Alert[], total: int, unread_count: int}`

- **PATCH** `/api/alerts/{alertId}/mark-seen` - Mark alert as read
  - Response: `{status: str, message: str}`

## Configuration

### Backend Configuration (`.env`)

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./polymarket_analytics.db

# Claude API (Required for insights)
CLAUDE_API_KEY=your_claude_api_key_here

# Polling & Alert Configuration
POLL_INTERVAL_SEC=60           # How often to poll markets (seconds)
ALERT_THRESHOLD_PCT=5.0        # Percentage change to trigger alerts
ENABLE_WORKER=true             # Enable background polling worker
```

### Frontend Configuration (`.env`)

```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Set to 'true' to use mock data instead of real API
VITE_USE_MOCK=false
```

## Data Flow

### 1. User Pins a Market
```
Frontend → POST /api/pin → Backend
                           ↓
                      Save to DB
                           ↓
Frontend ← 200 OK ← Backend
```

### 2. Background Worker Polling
```
Every POLL_INTERVAL_SEC:
  For each pinned market:
    1. Fetch current data from Polymarket API
    2. Store snapshot in MarketHistory table
    3. Compare with historical data (last WINDOW_MINUTES)
    4. If change > ALERT_THRESHOLD_PCT:
       a. Call Claude API for insight
       b. Create Alert for each user with that market pinned
```

### 3. Frontend Auto-Refresh
```
Every 60s: Refetch pinned markets
Every 45s: Refetch alerts
Every 120s: Refetch market details (on detail pages)
```

## Response Adapters

The backend uses `snake_case` while the frontend uses `camelCase`. The frontend has adapter functions to convert:

### Backend Response → Frontend Types

```typescript
// Pinned Market
BackendPinnedMarket → PinnedMarket
{
  id, user_id, market_id, pinned_at,
  latest_prob, latest_price, latest_volume,
  market_title
} → {
  marketId, title, impliedProbability,
  changePct, volume24h, updatedAt, sparkline
}

// Alert
BackendAlert → AlertItem
{
  id, user_id, market_id, ts,
  change_pct, threshold, market_title,
  insight_text, seen
} → {
  id, marketId, marketTitle, changePct,
  threshold, insightText, createdAt, seen
}

// Market Detail
BackendMarketDetail → MarketSnapshot
{
  market_id, latest, history, data_points
} → {
  marketId, title, latest, history, alerts
}
```

## Fallback Behavior

The frontend includes comprehensive mock data fallback:

- If `VITE_USE_MOCK=true`, always use mock data
- If backend is unreachable, automatically fall back to mock data
- Mock data includes:
  - 3 sample markets with historical data
  - 3 sample alerts with Claude insights
  - Dynamic placeholder generation for unknown market IDs

## Running the Integration

### Option 1: Using the Startup Script (Recommended)

```bash
./start-dev.sh
```

This script:
- Checks and installs dependencies if needed
- Starts the backend on port 8000
- Starts the frontend on port 5173
- Manages both processes with a single command
- Logs to `backend.log` and `frontend.log`

### Option 2: Manual Startup

#### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## Testing the Integration

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### 2. Check API Documentation
Open http://localhost:8000/docs in your browser

### 3. Test Frontend Connection
1. Open http://localhost:5173 in your browser
2. Open browser console (F12)
3. Look for any API errors or fallback warnings
4. Try pinning a market (use quick-pick buttons or enter a market ID)

### 4. Test Background Worker
1. Pin a market that has active trading
2. Wait for the polling interval (60 seconds default)
3. Check backend logs for polling activity
4. Check if alerts are generated when thresholds are met

## Database Schema

### Users
- `id` (PK)
- `email` (unique)
- `created_at`

### PinnedMarkets
- `id` (PK)
- `user_id` (FK → users)
- `market_id` (Polymarket ID)
- `pinned_at`

### MarketHistory
- `id` (PK)
- `market_id` (indexed)
- `ts` (indexed)
- `implied_prob` (0-100)
- `price` (0-1)
- `volume`
- `market_title`

### Alerts
- `id` (PK)
- `user_id` (FK → users)
- `market_id` (indexed)
- `ts` (indexed)
- `change_pct` (signed percentage change)
- `threshold`
- `market_title` (for display)
- `insight_text` (Claude-generated)
- `seen` (boolean)

## Troubleshooting

### Frontend can't connect to backend
1. Check backend is running on port 8000
2. Verify `VITE_API_BASE_URL` in frontend `.env`
3. Check browser console for CORS errors
4. Check backend CORS configuration in `main.py`

### No alerts being generated
1. Check `ENABLE_WORKER=true` in backend `.env`
2. Verify `CLAUDE_API_KEY` is set correctly
3. Check backend logs for polling activity
4. Verify pinned markets have sufficient price movement
5. Check `ALERT_THRESHOLD_PCT` setting (try lowering it for testing)

### Mock data showing instead of real data
1. Check `VITE_USE_MOCK=false` in frontend `.env`
2. Verify backend is responding (check browser network tab)
3. Check for error messages in browser console

### Database issues
1. Delete `backend/polymarket_analytics.db` to reset
2. Restart backend to recreate tables
3. Check file permissions on database file

## Development Workflow

### Adding a New API Endpoint

1. **Backend**:
   - Add route in `backend/routes.py`
   - Add request/response schemas in `backend/schemas.py`
   - Update API documentation

2. **Frontend**:
   - Add TypeScript types in `frontend/src/api/types.ts`
   - Add API client function in `frontend/src/api/client.ts`
   - Add adapter function if needed
   - Create React Query hook if needed

### Modifying Database Schema

1. Update model in `backend/models.py`
2. Delete database file (for MVP - in production use migrations)
3. Update schemas in `backend/schemas.py`
4. Update frontend types and adapters
5. Restart backend to recreate tables

## Production Considerations

For production deployment, consider:

1. **Database**: Migrate from SQLite to PostgreSQL
2. **Authentication**: Add proper user authentication/authorization
3. **API Keys**: Use secure key management (not .env files)
4. **CORS**: Restrict to production domain only
5. **Rate Limiting**: Add rate limiting to API endpoints
6. **Monitoring**: Add application performance monitoring
7. **Error Handling**: Improve error messages and logging
8. **WebSockets**: Consider WebSockets for real-time updates instead of polling
9. **Caching**: Add Redis for caching frequently accessed data
10. **Background Tasks**: Use Celery or similar for better task management
