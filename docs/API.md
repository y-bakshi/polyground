# Polymarket Analytics API Documentation

## Base URL
```
http://localhost:8000
```

## Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Architecture Notes for Frontend Team

### Backend-Side Processing
The backend handles ALL URL parsing, slug resolution, and business logic calculations. The frontend should:
- Send raw user input (URLs, slugs, or IDs) directly to the backend
- NOT parse URLs or make direct calls to Polymarket API
- NOT calculate derived values like `change_pct`
- Simply display data received from the backend

### Supported Input Formats
The `/api/pin` endpoint accepts any of these formats:
- **Full URLs**: `https://polymarket.com/market/slug-name` or `https://polymarket.com/event/slug-name`
- **Slugs**: `slug-name`
- **Numeric IDs**: `123456`

The backend automatically detects the format and resolves it to the correct market/event.

---

## Endpoints

### Health Check

#### `GET /health`
Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Pin/Unpin Markets

#### `POST /api/pin`
Pin a market or event for a user.

**IMPORTANT**: The backend handles all URL parsing and slug resolution. Just send the raw user input!

**Request Body:**
```json
{
  "userId": 1,
  "marketId": "https://polymarket.com/market/us-recession-2025"
}
```

**Alternative formats (all work):**
```json
// Slug only
{"userId": 1, "marketId": "us-recession-2025"}

// Numeric ID
{"userId": 1, "marketId": "516710"}

// Event URL
{"userId": 1, "marketId": "https://polymarket.com/event/2024-election"}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Pinned market successfully"
}
```

**Response (for events):**
```json
{
  "status": "ok",
  "message": "Pinned event successfully"
}
```

**Error Response:**
```json
{
  "detail": "Could not resolve 'invalid-input' to a valid market or event"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid input (couldn't resolve to market/event)
- `404` - User not found

---

#### `DELETE /api/pin`
Unpin a market for a user.

**Request Body:**
```json
{
  "userId": 1,
  "marketId": "0x1234567890abcdef"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Market 0x1234567890abcdef unpinned successfully"
}
```

**Status Codes:**
- `200` - Success
- `404` - Pinned market not found

---

### Get Pinned Markets

#### `GET /api/pinned?userId={userId}`
Get all pinned markets for a user with their latest data and 24-hour history.

**Query Parameters:**
- `userId` (required) - User ID

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
      "history": [
        {
          "ts": "2025-11-08T14:00:00",
          "implied_prob": 45.0,
          "price": 0.45,
          "volume": 10000,
          "market_title": "Will Bitcoin hit $100k by end of year?"
        },
        {
          "ts": "2025-11-08T15:00:00",
          "implied_prob": 56.5,
          "price": 0.565,
          "volume": 12500,
          "market_title": "Will Bitcoin hit $100k by end of year?"
        }
      ],
      "change_pct": 22.5,
      "is_event": false,
      "event_id": null,
      "event_title": null
    }
  ],
  "total": 1
}
```

**Response (for events):**
```json
{
  "items": [
    {
      "id": 2,
      "user_id": 1,
      "market_id": "562802",
      "pinned_at": "2025-11-08T12:00:00",
      "latest_prob": 69.5,
      "latest_price": 0.695,
      "latest_volume": 23332,
      "market_title": "Which party will win the House in 2026?",
      "history": [...],
      "change_pct": 0.0,
      "is_event": true,
      "event_id": "which-party-will-win-the-house-in-2026",
      "event_title": "Which party will win the House in 2026?"
    }
  ],
  "total": 1
}
```

**Field Descriptions:**
- `history` - Array of historical data points for sparkline visualization (last 24 hours)
- `change_pct` - **Calculated by backend**: Percentage change from first to last data point in history
- `is_event` - `true` if this is a multi-outcome event, `false` for single markets
- `event_id` - Event slug if `is_event=true`
- `event_title` - Event title if `is_event=true` (displayed instead of market_title)

**Status Codes:**
- `200` - Success
- `404` - User not found

---

### Get Market Details

#### `GET /api/market/{marketId}?hours={hours}`
Get market snapshot and historical data.

**Path Parameters:**
- `marketId` (required) - Polymarket market ID

**Query Parameters:**
- `hours` (optional, default: 24) - Number of hours of history to fetch

**Response:**
```json
{
  "market_id": "0x1234567890abcdef",
  "latest": {
    "ts": "2025-11-08T16:00:00",
    "implied_prob": 67.5,
    "price": 0.675,
    "volume": 15000,
    "market_title": "Will Bitcoin hit $100k by end of year?"
  },
  "history": [
    {
      "ts": "2025-11-08T14:00:00",
      "implied_prob": 45.0,
      "price": 0.45,
      "volume": 10000,
      "market_title": "Will Bitcoin hit $100k by end of year?"
    },
    {
      "ts": "2025-11-08T15:00:00",
      "implied_prob": 56.5,
      "price": 0.565,
      "volume": 12500,
      "market_title": "Will Bitcoin hit $100k by end of year?"
    }
  ],
  "data_points": 12
}
```

**Status Codes:**
- `200` - Success

---

### Get Event Details

#### `GET /api/event/{eventId}`
Get event details including all constituent markets.

**IMPORTANT**: Accepts both numeric event IDs and slugs!

**Path Parameters:**
- `eventId` (required) - Event ID or slug

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
  "markets": [
    {
      "id": "562802",
      "question": "Will the Democratic Party control the House after the 2026 Midterm elections?",
      "outcome_prices": "0.695",
      "active": true,
      "closed": false,
      "group_item_title": "Democratic Party"
    },
    {
      "id": "562803",
      "question": "Will the Republican Party control the House after the 2026 Midterm elections?",
      "outcome_prices": "0.305",
      "active": true,
      "closed": false,
      "group_item_title": "Republican Party"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `404` - Event not found

---

### Get Alerts

#### `GET /api/alerts?userId={userId}&unread_only={bool}&limit={limit}`
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

**Status Codes:**
- `200` - Success
- `404` - User not found

---

#### `PATCH /api/alerts/{alertId}/mark-seen`
Mark an alert as seen/read.

**Path Parameters:**
- `alertId` (required) - Alert ID

**Response:**
```json
{
  "status": "ok",
  "message": "Alert 1 marked as seen"
}
```

**Status Codes:**
- `200` - Success
- `404` - Alert not found

---

## Database Schema

### Users
- `id` - Primary key
- `email` - User email (unique)
- `created_at` - Timestamp

### Pinned Markets
- `id` - Primary key
- `user_id` - Foreign key to users
- `market_id` - Polymarket market ID
- `pinned_at` - Timestamp
- `is_event` - Boolean (true for events, false for markets)
- `event_id` - Event slug (null for markets)
- `event_title` - Event title (null for markets)

### Market History
- `id` - Primary key
- `market_id` - Polymarket market ID
- `ts` - Timestamp
- `implied_prob` - Implied probability (0-100)
- `price` - Current price
- `volume` - Trading volume
- `market_title` - Market title

### Alerts
- `id` - Primary key
- `user_id` - Foreign key to users
- `market_id` - Polymarket market ID
- `ts` - Timestamp
- `change_pct` - Percentage change that triggered alert
- `threshold` - Threshold that was exceeded
- `market_title` - Market title
- `insight_text` - Claude-generated insight
- `seen` - Boolean (read/unread status)

---

## Testing with curl

### Pin a market (URL)
```bash
curl -X POST http://localhost:8000/api/pin \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "marketId": "https://polymarket.com/market/us-recession-2025"}'
```

### Pin a market (slug)
```bash
curl -X POST http://localhost:8000/api/pin \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "marketId": "us-recession-2025"}'
```

### Pin a market (numeric ID)
```bash
curl -X POST http://localhost:8000/api/pin \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "marketId": "516710"}'
```

### Pin an event (URL)
```bash
curl -X POST http://localhost:8000/api/pin \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "marketId": "https://polymarket.com/event/which-party-will-win-the-house-in-2026"}'
```

### Get pinned markets
```bash
curl http://localhost:8000/api/pinned?userId=1
```

### Get market details
```bash
curl http://localhost:8000/api/market/516710?hours=24
```

### Get event details (slug)
```bash
curl http://localhost:8000/api/event/which-party-will-win-the-house-in-2026
```

### Get event details (numeric ID)
```bash
curl http://localhost:8000/api/event/12345
```

### Get alerts
```bash
curl http://localhost:8000/api/alerts?userId=1&unread_only=false
```

### Mark alert as seen
```bash
curl -X PATCH http://localhost:8000/api/alerts/1/mark-seen
```

---

## Frontend Integration Tips

### Handling User Input
When a user enters a market URL or ID:

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
  // ...
}
```

### Displaying Change Percentage
The backend calculates `change_pct` - just display it:

```typescript
// ✅ CORRECT: Use backend-calculated value
const PinnedMarket = ({ market }) => {
  return <div>Change: {market.change_pct}%</div>
}

// ❌ WRONG: Don't calculate in frontend
const PinnedMarket = ({ market }) => {
  const changePct = calculateChange(market.history)  // Don't do this!
  return <div>Change: {changePct}%</div>
}
```

### Event vs Market Display
Check the `is_event` flag to display the correct title:

```typescript
const displayTitle = market.is_event
  ? market.event_title  // Use event_title for events
  : market.market_title  // Use market_title for markets
```
