# Installation Guide

This guide covers installing and setting up the Polymarket Analytics project.

## Prerequisites

- **Python 3.12+** (for backend)
- **Node.js 18+** and **npm** (for frontend)
- **Git** (to clone the repository)

## Quick Setup

### Automated Setup (Recommended)

#### Linux/Mac
```bash
# Backend setup
cd backend
./setup.sh

# Frontend setup
cd ../frontend
npm install
```

#### Windows
```cmd
REM Backend setup
cd backend
setup.bat

REM Frontend setup
cd ..\frontend
npm install
```

## Manual Setup

### Backend Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

6. **Configure environment variables:**
   Edit `.env` file:
   ```bash
   # Server Configuration
   HOST=0.0.0.0
   PORT=8000

   # Database
   DATABASE_URL=sqlite:///./polymarket_analytics.db

   # Claude API (Required for insights)
   CLAUDE_API_KEY=your_claude_api_key_here

   # Polling & Alert Configuration
   POLL_INTERVAL_SEC=300           # Poll every 5 minutes
   ALERT_THRESHOLD_PCT=10.0        # Alert on 10% change
   ENABLE_WORKER=true              # Enable background polling worker

   # CORS (for production)
   CORS_ORIGINS=http://localhost:5173
   ```

7. **Initialize database:**
   ```bash
   python init_db.py --seed
   ```

   This creates:
   - User ID 1 (test@example.com)
   - 2 pinned markets with historical data
   - 1 test alert

### Frontend Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   # Create .env file
   echo "VITE_API_BASE_URL=http://localhost:8000" > .env
   echo "VITE_USE_MOCK=false" >> .env
   ```

   Or manually create `.env`:
   ```bash
   VITE_API_BASE_URL=http://localhost:8000
   VITE_USE_MOCK=false
   ```

## Database Setup

### Initialize Database

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create tables only
python init_db.py

# Create tables + add test data
python init_db.py --seed

# Reset database (drop all tables and recreate)
python init_db.py --reset --seed
```

### Database Schema

The project uses **SQLite** for the MVP (easily switchable to PostgreSQL later).

**Tables:**
- `users` - User accounts
- `pinned_markets` - User's pinned markets
- `market_history` - Time-series market data (probability, price, volume)
- `alerts` - Triggered alerts with Claude insights

## Environment Variables

### Backend (.env)

```bash
# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./polymarket_analytics.db

# Claude API (Required for insights)
CLAUDE_API_KEY=your_claude_api_key_here

# Polling & Alerts
POLL_INTERVAL_SEC=300              # How often to poll markets (seconds)
ALERT_THRESHOLD_PCT=10.0           # Percentage change to trigger alerts
ENABLE_WORKER=true                  # Enable background polling worker

# CORS (comma-separated for multiple origins)
CORS_ORIGINS=http://localhost:5173,https://your-production-domain.com
```

### Frontend (.env)

```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Set to 'true' to use mock data instead of real API
VITE_USE_MOCK=false
```

## Verification

### Check Backend Installation

```bash
cd backend
source venv/bin/activate
python -c "import fastapi, sqlalchemy, httpx; print('✓ All dependencies installed')"
```

### Check Frontend Installation

```bash
cd frontend
npm list --depth=0
```

### Test Database

```bash
cd backend
source venv/bin/activate
python -c "from database import init_db; init_db(); print('✓ Database initialized')"
```

## Troubleshooting

### Python Virtual Environment Issues

**Problem:** `python` command not found
**Solution:** Use `python3` instead, or install Python 3.12+

**Problem:** Virtual environment activation fails
**Solution:** 
- Windows: Use `venv\Scripts\activate.bat`
- Mac/Linux: Ensure you're using `source venv/bin/activate`

### Node.js Issues

**Problem:** `npm` command not found
**Solution:** Install Node.js from [nodejs.org](https://nodejs.org/)

**Problem:** Installation fails with permission errors
**Solution:** Use `npm install --legacy-peer-deps` or fix npm permissions

### Database Issues

**Problem:** Database file not created
**Solution:** Check file permissions in backend directory

**Problem:** Tables not created
**Solution:** Run `python init_db.py` manually

### Environment Variables

**Problem:** API key not working
**Solution:** 
- Verify `.env` file exists in backend directory
- Check that `CLAUDE_API_KEY` is set correctly
- Restart the server after changing `.env`

## Next Steps

After installation, see:
- [Running Guide](running.md) - How to start the application
- [Testing Guide](testing.md) - How to test the application
- [Documentation](documentation.md) - API documentation and architecture

