from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import database initialization
from database import init_db

# Import routes
from routes import router as api_router

load_dotenv()

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

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    init_db()
    print("✓ Database initialized")


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
