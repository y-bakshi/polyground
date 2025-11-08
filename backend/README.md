# Backend - FastAPI

This is the FastAPI backend for the ASU Hacks project.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration.

## Running the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload

# Or specify host and port
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive docs (Swagger): `http://localhost:8000/docs`
- Alternative docs (ReDoc): `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Available Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /api/hello` - Example API endpoint
