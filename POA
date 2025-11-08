# Project Plan – Polymarket Analytics Extension + Dashboard (Hackathon MVP)

**Project Name:** *To be decided*

**Goal:** Build a Chrome extension + dashboard that lets users pin Polymarket markets, monitors market activity, triggers alerts on significant changes, and provides AI-driven commentary via Claude to help users make more informed yes/no decisions.

---

## MVP Scope

**Included features (hackathon-ready):**

* Search/select Polymarket markets and **pin** them.
* Backend **polls** Polymarket REST API for pinned markets (implied probability/price, volume) on an interval.
* **Rule-based alert**: if market probability changes by > *X*% within last *Y* minutes/hours ➜ create alert.
* On alert: call **Claude API** with a compact market summary (recent deltas, volume, time to resolution) ➜ store and display **insight text**.
* **Dashboard (React+Vite)**: list pinned markets, sparkline/mini-chart, alerts feed with Claude insight, market detail page.
* **Chrome extension** (MV3): shows pinned markets, unread alert badge, deep link to dashboard.

**Deferred (post-hackathon):**

* Real-time WebSocket ingestion from Polymarket CLOB.
* Full ML predictive modeling and backtesting.
* Rich external signals (social/news sentiment, multi-source trends) beyond a single signal.
* Strategy builder, user sharing, mobile app/PWA.
* Production-grade auth, observability, scaling, monetization.

---

## Tech Stack

* **Backend:** FastAPI (Python 3.11+)
* **AI:** Claude API (Anthropic) for explanatory insights
* **Frontend:** React + Vite + TypeScript
* **DB:** Start with SQLite for speed (swap to Postgres after hackathon)
* **Infra (MVP):** Local dev or single VM; optional AWS (EC2 or Lightsail). Use `.env` for secrets (Claude API key). Cron/APSheduler for polling.
* **Extension:** Chrome Manifest v3, background service worker, popup UI; fetches from backend.

---

## High-Level Architecture

```
+----------------------+           +-------------------------+           +----------------------+
|  Chrome Extension    |  HTTPS    |  Backend API (FastAPI) |  HTTPS    |  Polymarket REST API |
|  (pin + alerts UI)   |<--------->|  Ingestion + Alerts     |<--------->|  (markets, prices)    |
+----------------------+           +-------------------------+           +----------------------+
                                        |             
                                        | on alert
                                        v
                                 +------------------+
                                 | Claude API       |
                                 | (Insight text)   |
                                 +------------------+
                                        |
                                        v
                                 +------------------+
                                 |   Database       |
                                 | (pins, history,  |
                                 |  alerts, insight)|
                                 +------------------+
                                        ^
                                        |
                                 +------------------+
                                 | React+Vite App   |
                                 | (Dashboard)      |
                                 +------------------+
```

---

## Backend Modules (FastAPI)

**Routes (MVP):**

* `POST /api/pin` – body: `{ userId, marketId }` ➜ store pin
* `GET  /api/pinned?userId=...` – list pinned markets
* `GET  /api/market/{marketId}` – latest snapshot + recent history
* `GET  /api/alerts?userId=...` – recent alerts with insight

**Services:**

* **PolymarketService**: fetch markets & quotes (REST), normalize to internal schema.
* **Scheduler/Worker**: every *N* minutes: for each pinned market → fetch latest → compute %Δ vs prior → if threshold exceeded ➜ create alert.
* **InsightService (Claude)**: build concise prompt with market deltas, time-to-resolution, optional simple external signal; call Claude; store `insight_text`.
* **Storage**: SQLite with SQLAlchemy. Tables below.

**Tables (initial):**

* `users(id, email)` *(mock/simple for hackathon)*
* `pinned_markets(id, user_id, market_id, pinned_at)`
* `market_history(id, market_id, ts, implied_prob, price, volume)`
* `alerts(id, user_id, market_id, ts, change_pct, threshold, insight_text, seen BOOLEAN)`

**Env/Config:**

* `CLAUDE_API_KEY`, `POLL_INTERVAL_SEC`, `ALERT_THRESHOLD_PCT`, `DATABASE_URL`

---

## Frontend (React + Vite + TS)

**Pages:**

* **Overview**: pinned markets table; latest prob, Δ over window; unread alerts count.
* **Alerts**: list with time, market, Δ, Claude insight; filter by unread.
* **Market Detail**: title, metadata, chart (probability/price over time), alert timeline.

**Components:**

* `PinnedList`, `AlertsList`, `MarketChart` (lightweight charting lib), `InsightCard`.

**State/Calls:**

* `GET /api/pinned`, `GET /api/alerts`, `GET /api/market/{id}`; optimistic updates for pin/unpin.

**Extension (MV3):**

* Popup: quick list of pinned markets + unread alerts badge; click → open dashboard route.
* Background SW: periodic pull of `/api/alerts?userId=...`; create `chrome.notifications` or badge text.

---

## Prompt Template (Claude) – MVP

> **System:** You are an analyst for prediction markets. Be concise and neutral.
>
> **User:**
> Market: "{market_title}"
> Time window: last {window} minutes
> Implied probability: {p_old}% → {p_new}% (Δ {delta_pct}%)
> Volume change: {vol_delta}
> Time to resolution: {ttr}
> External signal (optional): {signal_summary}
>
> In 3–5 sentences: explain plausible drivers of the move, 2 risks to watch, and a neutral note (not financial advice).

---

## API Sketch (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PinReq(BaseModel):
    userId: str
    marketId: str

@app.post("/api/pin")
async def pin_market(req: PinReq):
    # insert into pinned_markets
    return {"status": "ok"}

@app.get("/api/pinned")
async def get_pinned(userId: str):
    # select by userId
    return {"items": []}

@app.get("/api/market/{market_id}")
async def market_snapshot(market_id: str):
    # join latest history rows
    return {"marketId": market_id, "snapshot": {}}

@app.get("/api/alerts")
async def get_alerts(userId: str):
    # select alerts with insight
    return {"alerts": []}
```

---

## Demo Script (Judge-Friendly)

1. Open Dashboard → sign in (mock) → **Pinned list** shown.
2. **Search** and **Pin** a market (or already pinned).
3. Trigger polling (or run manual job) → an **Alert** appears (lower threshold for demo).
4. Open **Alerts** page → show Δ and **Claude insight**.
5. Open **Market Detail** → show chart and alert timeline.
6. Open **Chrome Extension** popup → see unread badge and quick access; click → deep link to market detail.
7. Close with **roadmap**: real-time WS, richer signals, ML predictions, backtesting.

---

## Risks & Mitigations

* **No movement during demo**: Preselect active markets; use small thresholds; allow manual backfill.
* **Claude latency/cost**: Async call + cached insight; keep prompts concise.
* **API hiccups**: Implement basic retries; show fallback UI.
* **Scope creep**: Stick to MVP; list extras as roadmap.
* **Compliance**: Add disclaimer: informational only, not financial advice.

---

## Post-Hackathon Roadmap

* Swap polling ➜ **WebSockets** (CLOB) for near-real-time.
* Add **Google Trends/news/social** as features; build **feature store**.
* Implement **ML** for short-horizon probability movement; add **backtesting**.
* Proper **auth** (JWT/OIDC), **Postgres**, **observability** (OpenTelemetry), CI/CD.
* **Monetization**: premium alerts, strategy marketplace, team dashboards.

---

## Checklist (MVP)

* [ ] FastAPI up with core endpoints
* [ ] SQLite schema & migrations
* [ ] Polymarket fetch + normalization
* [ ] Pin/unpin flow (UI + API)
* [ ] Poller + Δ computation + alerts
* [ ] Claude integration and insight rendering
* [ ] React dashboard (overview, alerts, detail)
* [ ] Chrome extension popup + badge + deep link
* [ ] Demo data + thresholds + script
* [ ] README and architecture section

