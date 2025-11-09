from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import asyncio
import logging

# Import database initialization
from database import init_db

# Import routes
from routes import router as api_router

# Import worker
from services.worker import get_worker

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Polymarket Analytics API",
    description="Backend API for Polymarket Analytics - Track markets, get alerts, and AI insights",
    version="1.0.0"
)

# CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Background task reference
background_tasks = set()


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables and start background worker"""
    init_db()
    print("✓ Database initialized")

    # Start the polling worker in the background
    enable_worker = os.getenv("ENABLE_WORKER", "true").lower() == "true"

    if enable_worker:
        logger.info("Starting market polling worker...")
        worker = get_worker()

        # Create background task
        task = asyncio.create_task(worker.start())
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

        print("✓ Market polling worker started")
    else:
        print("⊗ Worker disabled (ENABLE_WORKER=false)")


# Include API routes
app.include_router(api_router)


# Root endpoints
@app.get("/")
async def root():
    return {
        "message": "Polymarket Analytics API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
