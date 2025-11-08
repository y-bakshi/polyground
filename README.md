# ASU Hacks Project

A monorepo containing frontend and backend applications.

## Quick Start

### Frontend (React)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser to `http://localhost:5173`

### Backend (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

6. Visit the API docs at `http://localhost:8000/docs`

## Project Structure

```
asuHacks/
├── frontend/         # React app (Vite + React 19)
├── backend/          # FastAPI backend
├── CLAUDE.md         # Guide for Claude Code
└── README.md         # This file
```

## Available Commands

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Backend
- `uvicorn main:app --reload` - Start development server

## Tech Stack

**Frontend:**
- React 19
- Vite 7
- ESLint

**Backend:**
- FastAPI
- Uvicorn
- Pydantic
- Python Dotenv
