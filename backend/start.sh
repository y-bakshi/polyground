#!/bin/bash

# Start the FastAPI development server

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

echo "Starting Polymarket Analytics API..."
echo "Server will be available at http://localhost:8000"
echo "Interactive docs at http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

./venv/bin/uvicorn main:app --reload
