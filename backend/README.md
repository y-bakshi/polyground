# Backend - Polymarket Analytics API

FastAPI backend for the Polymarket Analytics project. Track markets, receive alerts on significant probability changes, and get AI-driven insights from Claude.

## Quick Start (Automated Setup)

### Linux/Mac

```bash
# One-time setup (creates venv, installs dependencies, sets up database)
./setup.sh

# Start the development server
./start.sh
```

### Windows

```cmd
REM One-time setup (creates venv, installs dependencies, sets up database)
setup.bat

REM Start the development server
start.bat
```

The API will be available at:
- **API:** `http://localhost:8000`
- **Interactive docs (Swagger):** `http://localhost:8000/docs`
- **Alternative docs (ReDoc):** `http://localhost:8000/redoc`

---

## Manual Setup (Alternative)

If you prefer to set up manually:

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to add your Claude API key (required later for insights).

5. **Initialize the database with test data:**
   ```bash
   python init_db.py --seed
   ```

6. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy database models
├── database.py          # Database configuration and connection
├── schemas.py           # Pydantic request/response models
├── routes.py            # API endpoint implementations
├── init_db.py           # Database initialization script
├── setup.sh             # Automated setup script (Linux/Mac)
├── setup.bat            # Automated setup script (Windows)
├── start.sh             # Start server script (Linux/Mac)
├── start.bat            # Start server script (Windows)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── API.md              # Full API documentation
└── README.md           # This file
```

## Setup Scripts

**`setup.sh` / `setup.bat`** - Automated setup script that:
- Creates Python virtual environment
- Installs all dependencies
- Creates `.env` file from template
- Initializes database with test data
- Provides option to reset existing database

**`start.sh` / `start.bat`** - Convenient server start script that:
- Verifies virtual environment exists
- Starts FastAPI development server with auto-reload
- Shows API URLs

## Database

The project uses **SQLite** for the MVP (easily switchable to PostgreSQL later).

### Tables
- `users` - User accounts
- `pinned_markets` - User's pinned markets
- `market_history` - Time-series market data (probability, price, volume)
- `alerts` - Triggered alerts with Claude insights

### Database Commands

```bash
# Create tables only
python init_db.py

# Create tables + add test data
python init_db.py --seed

# Reset database (drop all tables and recreate)
python init_db.py --reset --seed
```

## API Endpoints

### Pin Management
- `POST /api/pin` - Pin a market for a user
- `DELETE /api/pin` - Unpin a market

### Market Data
- `GET /api/pinned?userId={id}` - Get user's pinned markets with latest data
- `GET /api/market/{marketId}?hours={hours}` - Get market snapshot and history

### Alerts
- `GET /api/alerts?userId={id}` - Get user's alerts with insights
- `PATCH /api/alerts/{id}/mark-seen` - Mark alert as read

### Health
- `GET /health` - Health check

See [API.md](./API.md) for detailed endpoint documentation with examples.

## Test Data

When initialized with `--seed`, the database includes:
- 1 test user (test@example.com, ID: 1)
- 2 pinned markets with sample IDs
- 12 data points per market (2 hours of history)
- 1 sample alert with mock Claude insight

## Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./polymarket_analytics.db

# Claude API (for generating insights)
CLAUDE_API_KEY=your_claude_api_key_here

# Polling & Alerts (for future worker)
POLL_INTERVAL_SEC=300
ALERT_THRESHOLD_PCT=10.0
```

## Next Steps

1. ✅ Database setup
2. ✅ API endpoints
3. 🔄 Polymarket integration (fetch real market data)
4. 🔄 Polling worker (detect changes and trigger alerts)
5. 🔄 Claude integration (generate insights)
6. 🔄 Chrome extension
7. 🔄 React dashboard

## Development

The FastAPI server auto-reloads on code changes when run with `--reload` flag.

Use the interactive Swagger UI at `/docs` to test endpoints directly in your browser.
