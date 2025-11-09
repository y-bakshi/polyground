# Complete Documentation

This document contains API documentation, architecture details, examples, and reference information for the Polymarket Analytics project.

## Table of Contents

1. [Architecture](#architecture)
2. [API Reference](#api-reference)
3. [URL Examples & Usage](#url-examples--usage)
4. [Code Improvements](#code-improvements)
5. [Project Structure](#project-structure)
6. [Development Workflow](#development-workflow)
7. [Production Considerations](#production-considerations)

---

## Architecture

### System Overview

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

### Data Flow

#### 1. User Pins a Market
```
Frontend → POST /api/pin → Backend
                           ↓
                      Save to DB
                           ↓
Frontend ← 200 OK ← Backend
```

#### 2. Background Worker Polling
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

#### 3. Frontend Auto-Refresh
```
Every 60s: Refetch pinned markets
Every 45s: Refetch alerts
Every 120s: Refetch market details (on detail pages)
```

### Response Adapters

The backend uses `snake_case` while the frontend uses `camelCase`. The frontend has adapter functions to convert:

**Pinned Market:**
```typescript
Backend: {user_id, market_id, latest_prob, change_pct}
Frontend: {userId, marketId, impliedProbability, changePct}
```

**Alert:**
```typescript
Backend: {user_id, market_id, change_pct, insight_text, seen}
Frontend: {userId, marketId, changePct, insightText, seen}
```

---

## API Reference

### Base URL
```
http://localhost:8000
```

### Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Architecture Notes for Frontend Team

**Backend-Side Processing:**
The backend handles ALL URL parsing, slug resolution, and business logic calculations. The frontend should:
- Send raw user input (URLs, slugs, or IDs) directly to the backend
- NOT parse URLs or make direct calls to Polymarket API
- NOT calculate derived values like `change_pct`
- Simply display data received from the backend

### Endpoints

#### Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

#### Pin/Unpin Markets

**POST** `/api/pin`

Pin a market or event for a user. Accepts URLs, slugs, or numeric IDs.

**Request:**
```json
{
  "userId": 1,
  "marketId": "https://polymarket.com/market/us-recession-2025"
}
```

**Alternative formats (all work):**
- Slug: `{"userId": 1, "marketId": "us-recession-2025"}`
- Numeric ID: `{"userId": 1, "marketId": "516710"}`
- Event URL: `{"userId": 1, "marketId": "https://polymarket.com/event/2024-election"}`

**Response:**
```json
{
  "status": "ok",
  "message": "Pinned market successfully"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid input (couldn't resolve to market/event)
- `404` - User not found

---

**DELETE** `/api/pin`

Unpin a market for a user.

**Request:**
```json
{
  "userId": 1,
  "marketId": "516710"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Market 516710 unpinned successfully"
}
```

---

#### Get Pinned Markets

**GET** `/api/pinned?userId={userId}`

Get all pinned markets for a user with their latest data and 24-hour history.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "market_id": "516710",
      "pinned_at": "2025-11-08T12:00:00",
      "latest_prob": 67.5,
      "latest_price": 0.675,
      "latest_volume": 15000,
      "market_title": "Will Bitcoin hit $100k by end of year?",
      "history": [...],
      "change_pct": 22.5,
      "is_event": false,
      "event_id": null,
      "event_title": null
    }
  ],
  "total": 1
}
```

**Field Descriptions:**
- `history` - Array of historical data points for sparkline visualization (last 24 hours)
- `change_pct` - **Calculated by backend**: Percentage change from first to last data point
- `is_event` - `true` if this is a multi-outcome event, `false` for single markets

---

#### Get Market Details

**GET** `/api/market/{marketId}?hours={hours}`

Get market snapshot and historical data.

**Query Parameters:**
- `hours` (optional, default: 24) - Number of hours of history to fetch

**Response:**
```json
{
  "market_id": "516710",
  "latest": {
    "ts": "2025-11-08T16:00:00",
    "implied_prob": 67.5,
    "price": 0.675,
    "volume": 15000,
    "market_title": "Will Bitcoin hit $100k by end of year?"
  },
  "history": [...],
  "data_points": 12
}
```

---

#### Get Event Details

**GET** `/api/event/{eventId}`

Get event details including all constituent markets. Accepts both numeric event IDs and slugs.

**Examples:**
```bash
# Using slug
curl http://localhost:8000/api/event/which-party-will-win-the-house-in-2026

# Using numeric ID
curl http://localhost:8000/api/event/12345
```

**Response:**
```json
{
  "id": "which-party-will-win-the-house-in-2026",
  "title": "Which party will win the House in 2026?",
  "description": "This market will resolve...",
  "end_date": "2026-11-03T00:00:00",
  "active": true,
  "closed": false,
  "volume_24hr": 156789.45,
  "market_count": 3,
  "markets": [...]
}
```

---

#### Get Alerts

**GET** `/api/alerts?userId={userId}&unread_only={bool}&limit={limit}`

Get alerts for a user.

**Query Parameters:**
- `userId` (required) - User ID
- `unread_only` (optional, default: false) - Only show unread alerts
- `limit` (optional, default: 50) - Maximum number of alerts to return

**Response:**
```json
{
  "alerts": [
    {
      "id": 1,
      "user_id": 1,
      "market_id": "516710",
      "ts": "2025-11-08T16:00:00",
      "change_pct": 15.5,
      "threshold": 10.0,
      "market_title": "Will Bitcoin hit $100k by end of year?",
      "insight_text": "Sample insight: The market has moved significantly...",
      "seen": false
    }
  ],
  "total": 1,
  "unread_count": 1
}
```

---

**PATCH** `/api/alerts/{alertId}/mark-seen`

Mark an alert as seen/read.

**Response:**
```json
{
  "status": "ok",
  "message": "Alert 1 marked as seen"
}
```

---

### Database Schema

#### Users
- `id` - Primary key
- `email` - User email (unique)
- `created_at` - Timestamp

#### Pinned Markets
- `id` - Primary key
- `user_id` - Foreign key to users
- `market_id` - Polymarket market ID
- `pinned_at` - Timestamp
- `is_event` - Boolean (true for events, false for markets)
- `event_id` - Event slug (null for markets)
- `event_title` - Event title (null for markets)

#### Market History
- `id` - Primary key
- `market_id` - Polymarket market ID (indexed)
- `ts` - Timestamp (indexed)
- `implied_prob` - Implied probability (0-100)
- `price` - Current price
- `volume` - Trading volume
- `market_title` - Market title

#### Alerts
- `id` - Primary key
- `user_id` - Foreign key to users (indexed)
- `market_id` - Polymarket market ID (indexed)
- `ts` - Timestamp (indexed)
- `change_pct` - Percentage change that triggered alert
- `threshold` - Threshold that was exceeded
- `market_title` - Market title
- `insight_text` - Claude-generated insight
- `seen` - Boolean (read/unread status, indexed)

---

## URL Examples & Usage

### Supported Input Formats

The `/api/pin` endpoint accepts any of these formats:

1. **Direct Market ID (Numeric)**
   ```
   516710
   ```

2. **Full Polymarket URL (Market)**
   ```
   https://polymarket.com/market/us-recession-in-2025?tid=1758818660485
   ```
   → Extracts slug: `us-recession-in-2025`
   → Resolves to ID: `516710`

3. **Full Polymarket URL (Event)**
   ```
   https://polymarket.com/event/fed-decision-in-october?tid=1758818660485
   ```
   → Extracts slug: `fed-decision-in-october`
   → Resolves to Event ID: `27824`

4. **Just the Slug**
   ```
   us-recession-in-2025
   ```
   → Resolves to ID: `516710`

### Examples to Try

**Markets:**
- `https://polymarket.com/market/us-recession-in-2025`
- `https://polymarket.com/market/fed-rate-hike-in-2025`
- `https://polymarket.com/market/fed-emergency-rate-cut-in-2025`

**Events (Multi-outcome):**
- `https://polymarket.com/event/fed-decision-in-october`

**Direct IDs:**
- `516710` (US Recession 2025)
- `516706` (Fed Rate Hike 2025)
- `516711` (Fed Emergency Rate Cut 2025)

### Frontend Integration Tips

**Handling User Input:**
```typescript
// ✅ CORRECT: Send raw input to backend
const handlePin = async (userInput: string) => {
  await fetch('/api/pin', {
    method: 'POST',
    body: JSON.stringify({
      userId: 1,
      marketId: userInput  // Just pass it through!
    })
  })
}

// ❌ WRONG: Don't parse URLs in frontend
const handlePin = async (userInput: string) => {
  const slug = parseUrl(userInput)  // Don't do this!
  const marketId = await resolveSlug(slug)  // Don't do this!
}
```

**Displaying Change Percentage:**
```typescript
// ✅ CORRECT: Use backend-calculated value
const PinnedMarket = ({ market }) => {
  return <div>Change: {market.change_pct}%</div>
}
```

**Event vs Market Display:**
```typescript
const displayTitle = market.is_event
  ? market.event_title  // Use event_title for events
  : market.market_title  // Use market_title for markets
```

---

## Code Improvements

### Critical Fixes Implemented

1. **DateTime Deprecation Fix**
   - Replaced all `datetime.utcnow()` with `datetime.now(timezone.utc)`
   - Added `utc_now()` helper function for SQLAlchemy defaults

2. **Database Transaction Error Handling**
   - Added try/except blocks around all database commits
   - Added `db.rollback()` on exceptions
   - Improved error messages

3. **CORS Configuration**
   - Now uses `CORS_ORIGINS` environment variable
   - Supports comma-separated origins
   - Defaults to localhost for development

4. **HTTP Client Cleanup**
   - Added shutdown handler to close httpx clients
   - Prevents resource leaks

5. **Exception Handling**
   - Replaced silent exceptions with proper logging
   - Better error visibility

6. **Database Indexes**
   - Added index on `Alert.user_id` for better query performance

7. **Code Deduplication**
   - Created reusable `get_user()` helper function
   - Eliminates duplicate code

8. **Logging Improvements**
   - Replaced `print()` with proper `logger` calls
   - Better production logging

9. **Frontend Error Handling**
   - Improved error message parsing
   - Handles JSON and text error responses
   - Better user experience

### Future Improvements

See `IMPROVEMENTS.md` for a complete list of suggested improvements including:
- Rate limiting
- Caching
- Database migrations (Alembic)
- Unit and integration tests
- Monitoring and metrics
- Performance optimizations

---

## Project Structure

### Backend Structure
```
backend/
├── main.py              # FastAPI app entry point
├── routes.py            # API endpoint definitions
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic request/response schemas
├── database.py          # Database configuration
├── init_db.py           # Database initialization script
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (gitignored)
└── services/
    ├── polymarket.py    # Polymarket API integration
    ├── worker.py        # Background polling worker
    └── insight.py       # Claude insight generation
```

### Frontend Structure
```
frontend/
├── src/
│   ├── api/              # API client and types
│   │   ├── client.ts     # API client with adapters
│   │   ├── types.ts      # TypeScript interfaces
│   │   └── mockData.ts   # Mock data for fallback
│   ├── components/       # React components
│   ├── pages/            # Page components
│   ├── hooks/            # React Query hooks
│   ├── config/           # Configuration
│   └── utils/            # Utilities
├── public/               # Static assets
└── .env                  # Environment variables (gitignored)
```

---

## Development Workflow

### Adding a New API Endpoint

1. **Backend:**
   - Add route in `backend/routes.py`
   - Add request/response schemas in `backend/schemas.py`
   - Update API documentation

2. **Frontend:**
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

---

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

---

## Complete User Journey Example

See `backend/DEMO.md` for a complete step-by-step demo of:
- Pinning a market
- Viewing market trends
- Receiving alerts with AI insights
- Complete end-to-end flow

---

## Additional Resources

- [Installation Guide](installation.md) - Setup instructions
- [Running Guide](running.md) - How to run the application
- [Testing Guide](testing.md) - Testing documentation

For detailed API examples and curl commands, see the interactive Swagger UI at http://localhost:8000/docs
