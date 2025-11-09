@echo off
REM Backend Setup Script for Polymarket Analytics (Windows)
REM This script automates the setup process for the FastAPI backend

echo ================================================
echo   Polymarket Analytics - Backend Setup
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.11+ and try again
    exit /b 1
)

echo [1/5] Creating virtual environment...
if exist venv (
    echo   -^> Virtual environment already exists, skipping
) else (
    python -m venv venv
    echo   √ Virtual environment created
)
echo.

echo [2/5] Installing dependencies...
venv\Scripts\pip install --upgrade pip >nul 2>&1
venv\Scripts\pip install -r requirements.txt >nul 2>&1
echo   √ All dependencies installed
echo.

echo [3/5] Setting up environment variables...
if exist .env (
    echo   -^> .env file already exists, skipping
) else (
    copy .env.example .env >nul
    echo   √ .env file created from .env.example
)
echo.

echo [4/5] Initializing database...
if exist polymarket_analytics.db (
    set /p REPLY="  -^> Database already exists. Reset and seed with test data? (y/N): "
    if /i "%REPLY%"=="y" (
        venv\Scripts\python init_db.py --reset --seed
        echo   √ Database reset and seeded with test data
    ) else (
        echo   -^> Keeping existing database
    )
) else (
    venv\Scripts\python init_db.py --seed
    echo   √ Database created and seeded with test data
)
echo.

echo [5/5] Setup complete!
echo.
echo ================================================
echo   🎉 Backend setup successful!
echo ================================================
echo.
echo To start the development server:
echo   start.bat
echo.
echo Or manually:
echo   venv\Scripts\uvicorn main:app --reload
echo.
echo API will be available at:
echo   • http://localhost:8000
echo   • http://localhost:8000/docs (Swagger UI)
echo.

pause
