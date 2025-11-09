#!/bin/bash

# Development startup script for asuHacks project
# Runs both frontend and backend services concurrently

set -e

echo "🚀 Starting asuHacks Development Environment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "${YELLOW}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Check if backend dependencies are installed
if [ ! -d "backend/venv" ]; then
    echo "${YELLOW}⚠️  Backend virtual environment not found. Setting up...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo "${GREEN}✓ Backend virtual environment found${NC}"
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "${YELLOW}⚠️  Frontend dependencies not found. Installing...${NC}"
    cd frontend
    npm install
    cd ..
    echo "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo "${GREEN}✓ Frontend dependencies found${NC}"
fi

# Check if backend .env exists
if [ ! -f "backend/.env" ]; then
    echo "${YELLOW}⚠️  Backend .env not found. Please configure backend/.env${NC}"
    exit 1
fi

echo ""
echo "${BLUE}════════════════════════════════════════${NC}"
echo "${BLUE}  Starting Services${NC}"
echo "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Start backend
echo "${GREEN}[Backend]${NC} Starting FastAPI server on http://localhost:8000"
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 2

# Start frontend
echo "${GREEN}[Frontend]${NC} Starting Vite dev server on http://localhost:5173"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "${BLUE}════════════════════════════════════════${NC}"
echo "${GREEN}✓ Services Started Successfully!${NC}"
echo "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo "${GREEN}Frontend:${NC}   http://localhost:5173"
echo "${GREEN}Backend:${NC}    http://localhost:8000"
echo "${GREEN}API Docs:${NC}   http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""
echo "${YELLOW}View logs:${NC}"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""

# Wait for background processes
wait
