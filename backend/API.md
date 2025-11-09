# Polymarket Analytics API Documentation

## Base URL
```
http://localhost:8000
```

## Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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
Pin a market for a user.

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
  "message": "Market 0x1234567890abcdef pinned successfully"
}
```

**Status Codes:**
- `200` - Success
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
Get all pinned markets for a user with their latest data.

**Query Parameters:**
- `userId` (required) - User ID

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "market_id": "0x1234567890abcdef",
      "pinned_at": "2025-11-08T12:00:00",
      "latest_prob": 67.5,
      "latest_price": 0.675,
      "latest_volume": 15000,
      "market_title": "Will Bitcoin hit $100k by end of year?"
    }
  ],
  "total": 1
}
```

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
      "market_id": "0x1234567890abcdef",
      "ts": "2025-11-08T16:00:00",
      "change_pct": 15.5,
      "threshold": 10.0,
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
- `insight_text` - Claude-generated insight
- `seen` - Boolean (read/unread status)

---

## Testing with curl

### Pin a market
```bash
curl -X POST http://localhost:8000/api/pin \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "marketId": "0x1234567890abcdef"}'
```

### Get pinned markets
```bash
curl http://localhost:8000/api/pinned?userId=1
```

### Get market details
```bash
curl http://localhost:8000/api/market/0x1234567890abcdef?hours=24
```

### Get alerts
```bash
curl http://localhost:8000/api/alerts?userId=1&unread_only=false
```

### Mark alert as seen
```bash
curl -X PATCH http://localhost:8000/api/alerts/1/mark-seen
```
