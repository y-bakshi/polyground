# Polymarket Scout – Full Project Documentation

## 1. Concept & Goals

Polymarket Scout is a hackathon-friendly monorepo that pairs a FastAPI backend, a Vite + React dashboard, and a Chrome MV3 extension. Together they let power-users:

- Pin Polymarket markets/events they care about.
- Continuously poll official Gamma/CLOB APIs to capture price/probability/volume deltas.
- Trigger rule-based alerts when movements exceed a configurable threshold.
- Generate concise “what changed?” blurbs via Claude (Anthropic API).
- Surface those alerts inside a rich dashboard and a lightweight browser action.

The stack intentionally trades complexity for iteration speed: SQLite + SQLAlchemy for persistence, React Query for data fetching, and a polling worker instead of a full realtime feed.

---

## 2. Repository Layout

```
asuHacks/
├── backend/          # FastAPI app + worker + DB models
├── frontend/         # Vite/React dashboard + extension + tooling
├── docs/             # Project-wide documentation (this file)
├── README.md         # High-level quick start
└── CLAUDE.md         # Claude-specific onboarding tips
```

---

## 3. High-Level Architecture

```
                   ┌──────────────────────┐
                   │  Chrome Extension    │
                   │  (popup + SW badge)  │
                   └─────────▲────────────┘
                             │
                             │ HTTP (JSON)
                             │
┌─────────────────────────────┴──────────────────────────────┐
│                  FastAPI Backend (backend/)                │
│ ┌──────────────┐    ┌─────────────┐    ┌────────────────┐ │
│ │ REST Routes  │ →  │ Services    │ →  │ SQLite via ORM │ │
│ └──────────────┘    └─────────────┘    └────────────────┘ │
│            ↑            ↑           ┌──────────────────┐   │
│            │            │           │ Background Worker│   │
│            │            │           └──────────────────┘   │
└────────────┴────────────┴──────────────────────────────────┘
             │
             │ HTTP (JSON)
             │
┌────────────▼────────────┐
│ React Dashboard         │
│ (frontend/src)          │
└─────────────────────────┘
```

**Key flows**

1. Users pin/unpin markets via frontend or extension (`POST/DELETE /api/pin`).
2. Worker polls Polymarket for all pinned market IDs, stores snapshots, and compares vs. a sliding window.
3. When movement passes the configured threshold, it writes an `alerts` record and optionally hits the Claude API to enrich insight text.
4. Dashboard and extension consume `/api/pinned`, `/api/market/{id}`, `/api/event/{id}`, and `/api/alerts` to render tables, charts, sparks, and actionable alerts/badges.

---

## 4. Backend (FastAPI)

### 4.1 Project Anatomy

| File/Dir                  | Purpose                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| `main.py`                 | FastAPI entry point, CORS setup, worker bootstrap.                      |
| `routes.py`               | All REST endpoints (pinning, pinned list, market detail, alerts, events).|
| `models.py`               | SQLAlchemy models (`User`, `PinnedMarket`, `MarketHistory`, `Alert`).   |
| `schemas.py`              | Pydantic DTOs mirroring the SQL models for serialization.               |
| `database.py`             | Engine/session boilerplate, `init_db()`/`drop_db()`.                    |
| `services/`               | Polymarket client, Claude insight client, polling worker.               |
| `init_db.py`              | CLI for creating/resetting/seeding the SQLite database.                 |
| `setup.sh` / `.bat`       | Automated venv + dependencies + DB bootstrap.                           |
| `start.sh` / `.bat`       | Thin wrappers around `uvicorn main:app --reload`.                      |

### 4.2 Notable Services

- **PolymarketService (`services/polymarket.py`)**  
  Async HTTPX client hitting Gamma (metadata) and CLOB (price history). Handles distinguishing events from markets, fallback parsing of token IDs, and snapshot normalization (implied prob, price, volume).

- **InsightService (`services/insight.py`)**  
  Wraps the Anthropic Python SDK. Given two snapshots, it crafts the hackathon prompt template (from `docs/POA.md`) and returns Claude’s response or `None` when disabled.

- **MarketPollingWorker (`services/worker.py`)**  
  *Configuration:* `POLL_INTERVAL_SEC`, `ALERT_THRESHOLD_PCT`, `ENABLE_WORKER` env vars.  
  *Behavior:* for every unique pinned `market_id`, fetch a snapshot, persist to `market_history`, and compare vs. the first sample within the configured lookback window. If abs(delta)>=threshold, create alerts per user and request a Claude insight.

### 4.3 Environment

`.env.example` documents everything:

```
DATABASE_URL=sqlite:///./polymarket_analytics.db
CLAUDE_API_KEY=your_key
POLL_INTERVAL_SEC=300
ALERT_THRESHOLD_PCT=10.0
ENABLE_WORKER=true
```

### 4.4 Database Schema

- `users(id, email, created_at)`
- `pinned_markets(id, user_id, market_id, pinned_at)`
- `market_history(id, market_id, ts, implied_prob, price, volume, market_title)`
- `alerts(id, user_id, market_id, ts, change_pct, threshold, insight_text, seen)`

### 4.5 API Surface (summary)

| Method & Path                        | Description                                                                          |
|-------------------------------------|--------------------------------------------------------------------------------------|
| `POST /api/pin`                     | Pin a market/event for a user. Idempotent; returns “Already pinned” if duplicate.    |
| `DELETE /api/pin`                   | Remove a pin.                                                                        |
| `GET /api/pinned?userId=`           | List user pins with the latest `market_history` snapshot.                           |
| `GET /api/market/{marketId}?hours=` | Latest + historical series for charting.                                            |
| `GET /api/event/{eventId}`          | Resolve multi-outcome events and enumerate sub-markets.                              |
| `GET /api/alerts?userId=...`        | Alerts feed with optional unread filter + counts.                                    |
| `PATCH /api/alerts/{id}/mark-seen`  | Mark an alert read.                                                                  |
| `GET /health` / `/`                 | Simple readiness endpoints.                                                          |

### 4.6 Testing

`backend/tests/test_api.py` uses `pytest` + `fastapi.testclient`. It:

- Boots FastAPI with a throwaway SQLite DB.
- Seeds deterministic fixtures (user, pinned market, history, alert).
- Exercises pin creation, pinned-market listing, and the event endpoint (with a monkeypatched Polymarket service) to ensure sub-markets render for users—directly targeting the “cannot see sub markets” regression reported.

Run tests via:

```bash
cd backend
./venv/bin/pytest   # or `pytest` if venv activated
```

---

## 5. Frontend (Vite + React + TS)

### 5.1 Project Anatomy

| File/Dir                         | Purpose                                                                              |
|----------------------------------|--------------------------------------------------------------------------------------|
| `src/App.tsx`                    | Router setup + React Query provider + layout shell.                                  |
| `src/pages/*`                    | Overview, Alerts, MarketDetail, EventDetail screens.                                 |
| `src/components/`                | Layout shell, metric cards, sparkline chart, tables, insight cards, pin form.        |
| `src/api/client.ts`              | Typed fetch layer with mock fallback toggled via `VITE_USE_MOCK`.                    |
| `src/config/constants.ts`        | `DEMO_USER_ID`, `API_BASE_URL`, mock toggle.                                         |
| `src/hooks/*`                    | React Query wrappers for pinned markets, alerts, market/event detail.                |
| `src/utils/format.ts`            | Intl wrappers for percentages and datetime.                                          |
| `src/utils/polymarket.ts`        | Safe extraction of market/event IDs from arbitrary Polymarket URLs.                  |
| `public/index.html`              | Vite entry (note: update `<script src>` if renaming `main.tsx`).                     |

### 5.2 Data Flow

- Hooks call `apiClient.*`, which hits `/api/...` endpoints or returns `mockStore` data when `VITE_USE_MOCK=true`.
- Overview aggregates pinned-market stats, surfaces pin form, and shows sparkline data (derived from backend `market_history`).
- Alerts page provides quick filtering (`all` vs `unread`).
- Market detail page auto-detects events by firing both `/api/market/{id}` and `/api/event/{id}`; if an event payload returns, it redirects to the event view so users can browse sub-markets, resolving the “sub markets visibility” UX gap.

### 5.3 Styling

Custom CSS (`App.css`, `index.css`) builds a dark, glassy dashboard vibe. Sparkline component renders inline SVG with gradients for a compact history view without pulling in a charting library.

### 5.4 Commands

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
npm run build      # production bundle under dist/
npm run preview    # preview prod build
npm run lint       # eslint@9 config
```

Environment flags in `.env` or invoked via `VITE_…`:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK=true   # optional
```

---

## 6. Chrome Extension (frontend/extension)

### 6.1 Structure

| File                | Description                                                         |
|---------------------|---------------------------------------------------------------------|
| `manifest.json`     | MV3 manifest (popup + background service worker).                   |
| `config.js`         | Runtime constants (`API_BASE_URL`, `USER_ID`, poll cadence).        |
| `popup.html/css/js` | Toolbar UI: pinned list, quick pin form, latest alerts, refresh CTA.|
| `background.js`     | Uses `chrome.alarms` to poll `/api/alerts`, updates badge, shows notifications linking into the dashboard. |
| `icons/`            | PNG icon set (128px).                                               |

### 6.2 Packaging

`npm run package:extension` zips `frontend/extension` into `extension-dist/polymarket-scout-extension.zip` using `scripts/package-extension.mjs`.

### 6.3 Local Testing

1. Update `config.js` to point at running backend/frontend.
2. Load unpacked via `chrome://extensions` (Developer mode).
3. Pin “Polymarket Scout” so the badge text surfaces unread counts.

---

## 7. End-to-End Workflow

1. **Bootstrap backend**
   ```bash
   cd backend
   ./setup.sh      # creates venv, installs deps, seeds DB
   ./start.sh      # uvicorn main:app --reload
   ```
   Ensure `.env` has `CLAUDE_API_KEY` if insights are desired; otherwise the warning is benign.

2. **Run frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **(Optional) Extension** – load the unpacked directory after setting `config.js` to `USER_ID='1'` (matches seeded DB).

4. **User flow**
   - Visit `http://localhost:5173`.
   - Pin a market via ID or Polymarket URL. Quick picks help for demos.
   - Worker stores history every poll. To speed demos, lower `ALERT_THRESHOLD_PCT` or manually insert history rows via `init_db.py --reset --seed`.
   - Alerts show up in both the dashboard and extension as soon as the worker detects movement. Clicking notifications deep-links into `#/market/{id}`.

---

## 8. Troubleshooting & Tips

| Symptom                                       | Fix                                                                                      |
|-----------------------------------------------|------------------------------------------------------------------------------------------|
| `PermissionError` binding to ports            | Run commands with elevated permissions or change `HOST/PORT` envs before launching.      |
| Worker spam (during local dev)                | Set `ENABLE_WORKER=false` in `.env` to stop the polling loop when testing endpoints.     |
| Event detail shows “Could not load event…”    | Means the ID was a single-market slug. Use `/market/{id}` instead or confirm Polymarket slug includes numeric suffix. |
| Frontend hitting wrong backend URL            | Export `VITE_API_BASE_URL` or set `.env` in frontend with proper origin.                 |
| Tests timing out                              | Ensure `pytest` runs inside the venv (`./venv/bin/pytest`). Tests mock the Polymarket service so they don’t require network access. |

---

## 9. Roadmap Highlights

From `docs/POA.md` and `DEMO.md`:

- Swap polling for Polymarket WebSockets (CLOB) to achieve near-real-time updates.
- Replace SQLite with Postgres for multi-user production deployments.
- Expand insight generation with richer signals (news, social, macro data).
- Build auth (JWT/OIDC) and multi-user dashboards/notification preferences.
- Package extension for Chrome Web Store and potentially ship Firefox variant.

---

## 10. Quick Reference

| Area      | Command / Path                                |
|-----------|-----------------------------------------------|
| Backend   | `./setup.sh`, `./start.sh`, `uvicorn main:app --reload` |
| Frontend  | `npm run dev`, `npm run build`                 |
| Tests     | `cd backend && ./venv/bin/pytest`              |
| Extension | `npm run package:extension`, load `frontend/extension` |
| Docs      | `README.md`, `docs/POA.md`, `DEMO.md`, `docs/PROJECT_OVERVIEW.md` |

With this document plus the repo’s existing READMEs, new engineers (or judges) can ramp quickly on setup, architecture, debugging techniques, and demo scripts.
