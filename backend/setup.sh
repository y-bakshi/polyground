#!/bin/bash

# Backend Setup Script for Polymarket Analytics
# This script automates the setup process for the FastAPI backend

set -e  # Exit on error

echo "================================================"
echo "  Polymarket Analytics - Backend Setup"
echo "================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.11+ and try again"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Step 1: Create virtual environment
echo "[1/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  → Virtual environment already exists, skipping"
else
    python3 -m venv venv
    echo "  ✓ Virtual environment created"
fi
echo ""

# Step 2: Install dependencies
echo "[2/5] Installing dependencies..."
./venv/bin/pip install --upgrade pip > /dev/null 2>&1
./venv/bin/pip install -r requirements.txt > /dev/null 2>&1
echo "  ✓ All dependencies installed"
echo ""

# Step 3: Create .env file
echo "[3/5] Setting up environment variables..."
if [ -f ".env" ]; then
    echo "  → .env file already exists, skipping"
else
    cp .env.example .env
    echo "  ✓ .env file created from .env.example"
fi
echo ""

# Step 4: Initialize database
echo "[4/5] Initializing database..."
if [ -f "polymarket_analytics.db" ]; then
    read -p "  → Database already exists. Reset and seed with test data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./venv/bin/python init_db.py --reset --seed
        echo "  ✓ Database reset and seeded with test data"
    else
        echo "  → Keeping existing database"
    fi
else
    ./venv/bin/python init_db.py --seed
    echo "  ✓ Database created and seeded with test data"
fi
echo ""

# Step 5: Done
echo "[5/5] Setup complete!"
echo ""
echo "================================================"
echo "  🎉 Backend setup successful!"
echo "================================================"
echo ""
echo "To start the development server:"
echo "  ./start.sh"
echo ""
echo "Or manually:"
echo "  ./venv/bin/uvicorn main:app --reload"
echo ""
echo "API will be available at:"
echo "  • http://localhost:8000"
echo "  • http://localhost:8000/docs (Swagger UI)"
echo ""
