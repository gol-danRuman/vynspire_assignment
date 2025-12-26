# Quick Start Guide

Get the Simple RAG System running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with pgvector
- Google Gemini API key ([Get one free](https://makersuite.google.com/app/apikey))

## Setup

### 1. Database Setup (30 seconds)

```bash
# Install and start PostgreSQL with pgvector
docker run -d \
  --name rag_postgres \
  -e POSTGRES_USER=raguser \
  -e POSTGRES_PASSWORD=ragpassword \
  -e POSTGRES_DB=ragdb \
  -p 5432:5432 \
  ankane/pgvector:latest
```

### 2. Backend Setup (2 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start server
python -m uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### 3. Frontend Setup (2 minutes)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

## Quick Test

1. Open http://localhost:3000
2. Upload a test document (PDF, TXT, or MD)
3. Wait for processing (~3-5 seconds)
4. Ask a question: "What is this document about?"
5. View the AI-generated answer with sources!

## Docker Alternative

### Development Mode with Auto-Reload (Recommended)

```bash
# Set your Gemini API key
export GEMINI_API_KEY=your_key_here

# Start all services with auto-reload enabled
docker-compose up --build

# View logs
docker-compose logs -f

# Access at http://localhost:3000
# Code changes will automatically reload!
```

**Features:**

- ✅ Backend auto-reloads on Python file changes
- ✅ Frontend hot-reloads on React/Next.js changes
- ✅ Debug mode enabled for better error messages
- ✅ Fast iteration during development

### Production Mode

```bash
# For production deployment (optimized, no auto-reload)
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

**Problem**: Database connection fails
```bash
# Check PostgreSQL is running
docker ps | grep postgres
# Or: pg_isready -h localhost -U raguser
```

**Problem**: Gemini API error
```bash
# Verify your API key
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"
```

**Problem**: Port already in use
```bash
# Backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Frontend (port 3000)
lsof -ti:3000 | xargs kill -9
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [docs/SETUP.md](docs/SETUP.md) for detailed setup
- Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- See [docs/API.md](docs/API.md) for API reference

## Support

Issues? Check [docs/SETUP.md](docs/SETUP.md) or create an issue on GitHub.
