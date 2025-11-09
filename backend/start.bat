@echo off
REM Start the FastAPI development server (Windows)

if not exist venv (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first
    exit /b 1
)

echo Starting Polymarket Analytics API...
echo Server will be available at http://localhost:8000
echo Interactive docs at http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.

venv\Scripts\uvicorn main:app --reload
