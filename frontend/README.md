# Polymarket Scout Frontend

A Vite + React dashboard and companion Chrome extension that highlight pinned Polymarket markets, polling data from the FastAPI backend and surfacing Claude-generated alerts.

## Web App

### Setup

```bash
cd frontend
npm install
npm run dev
```

- Set `VITE_API_BASE_URL` (defaults to `http://localhost:8000`).
- Set `VITE_USE_MOCK=true` to use the built-in mock store instead of the backend (handy for demoing without FastAPI).

### Scripts

- `npm run dev` – local dev server (default port 5173)
- `npm run build` – production build under `dist/`
- `npm run preview` – preview the production build
- `npm run package:extension` – zips `frontend/extension` into `frontend/extension-dist/polymarket-scout-extension.zip`

## Chrome Extension (MV3)

Located in `frontend/extension`. It contains:

- `manifest.json` – declares popup UI plus a background service worker
- `popup.html/css/js` – lightweight UI for pinned markets + recent alerts
- `background.js` – polls `/api/alerts`, updates the badge every minute, and fires a Chrome notification when a new alert arrives

### Load Locally

1. Update `frontend/extension/config.js` with the correct `API_BASE_URL`, `DASHBOARD_BASE_URL`, `USER_ID`, and poll cadence.
2. Start the backend API (default `http://localhost:8000`).
3. Build/run the React dashboard (`npm run dev`) so dashboard links resolve to `http://localhost:5173`.
4. In Chrome → `chrome://extensions` → enable **Developer mode** → **Load unpacked** → select `frontend/extension`.
5. Pin “Polymarket Scout” from the extensions toolbar. The badge text displays the count of unread alerts fetched from the backend.

> When deploying, adjust `frontend/extension/config.js`, update the `host_permissions` in `manifest.json`, then run `npm run package:extension` and upload the generated zip to the Chrome Web Store.
