# Running the Application

This guide covers how to run the Polymarket Analytics application in development.

## Quick Start

### Start Both Services (Recommended)

Use the startup script to run both frontend and backend together:

```bash
./start-dev.sh
```

This script:
- Checks and installs dependencies if needed
- Starts the backend on port 8000
- Starts the frontend on port 5173
- Manages both processes with a single command
- Logs to `backend.log` and `frontend.log`

**Access Points:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

Press `Ctrl+C` to stop all services.

## Manual Startup

### Option 1: Separate Terminals

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

### Option 2: Backend Only

If you only need the backend API:

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Access:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Option 3: Frontend Only (Mock Mode)

If you want to develop frontend without backend:

1. Set `VITE_USE_MOCK=true` in `frontend/.env`
2. Start frontend:
   ```bash
   cd frontend
   npm run dev
   ```

The frontend will use mock data instead of making API calls.

## Development Commands

### Frontend Commands

```bash
cd frontend

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Backend Commands

```bash
cd backend
source venv/bin/activate

# Start development server with auto-reload
uvicorn main:app --reload

# Start with custom host/port
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start without auto-reload (production-like)
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Background Worker

The backend includes a background worker that polls Polymarket markets for changes.

### Enable/Disable Worker

Set in `backend/.env`:
```bash
ENABLE_WORKER=true   # Enable worker
ENABLE_WORKER=false  # Disable worker
```

### Worker Configuration

```bash
# How often to poll markets (in seconds)
POLL_INTERVAL_SEC=300

# Percentage change threshold to trigger alerts
ALERT_THRESHOLD_PCT=10.0
```

### Worker Status

Check backend logs to see worker activity:
```bash
tail -f backend.log
```

You should see messages like:
```
INFO - Polling 7 pinned markets
INFO - Stored history for 516710: prob=4.1%, vol=4747
```

## Auto-Refresh Intervals

The frontend automatically refreshes data:

- **Pinned Markets:** Every 60 seconds
- **Alerts:** Every 45 seconds
- **Market Details:** Every 120 seconds (on detail pages)

These intervals are configured in the React Query hooks.

## Verification

### Check Backend is Running

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### Check Frontend is Running

Open http://localhost:5173 in your browser. You should see the dashboard.

### Check API Documentation

Open http://localhost:8000/docs in your browser. You should see the Swagger UI.

## Troubleshooting

### Port Already in Use

**Problem:** Port 8000 or 5173 is already in use

**Solution:**
- Find and stop the process using the port:
  ```bash
  # Find process on port 8000
  lsof -i :8000  # Mac/Linux
  netstat -ano | findstr :8000  # Windows
  
  # Kill the process
  kill -9 <PID>  # Mac/Linux
  taskkill /PID <PID> /F  # Windows
  ```
- Or use different ports:
  ```bash
  # Backend on different port
  uvicorn main:app --reload --port 8001
  
  # Update frontend .env
  VITE_API_BASE_URL=http://localhost:8001
  ```

### Backend Not Starting

**Problem:** Backend fails to start

**Check:**
1. Virtual environment is activated
2. Dependencies are installed: `pip install -r requirements.txt`
3. `.env` file exists in backend directory
4. Database file is writable

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload
```

### Frontend Not Connecting to Backend

**Problem:** Frontend shows errors or uses mock data

**Check:**
1. Backend is running on port 8000
2. `VITE_API_BASE_URL` in frontend `.env` is correct
3. CORS is configured correctly
4. Browser console for errors

**Solution:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check frontend .env
cat frontend/.env

# Check browser console (F12)
```

### Worker Not Polling

**Problem:** No market data being collected

**Check:**
1. `ENABLE_WORKER=true` in backend `.env`
2. Backend logs show worker starting
3. Markets are pinned
4. `CLAUDE_API_KEY` is set (for insights)

**Solution:**
```bash
# Check .env
grep ENABLE_WORKER backend/.env

# Check logs
tail -f backend.log | grep worker

# Restart backend
```

## Production Deployment

For production, consider:

1. **Use production server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Build frontend:**
   ```bash
   cd frontend
   npm run build
   # Serve dist/ directory with nginx or similar
   ```

3. **Set production environment variables:**
   - Use secure key management
   - Set proper CORS origins
   - Use PostgreSQL instead of SQLite
   - Enable proper logging

4. **Use process manager:**
   - systemd (Linux)
   - PM2 (Node.js)
   - Supervisor

See [Documentation](documentation.md) for more details on production considerations.

