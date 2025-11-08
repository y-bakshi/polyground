from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="ASU Hacks API",
    description="Backend API for ASU Hacks project",
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

@app.get("/")
async def root():
    return {"message": "Welcome to ASU Hacks API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Example API endpoint
@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI!"}
