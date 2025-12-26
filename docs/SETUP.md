# Setup Guide

Complete guide for setting up the Simple RAG System from scratch.

## Prerequisites

### Required Software

1. **Python 3.11 or higher**
   ```bash
   python --version  # Should be 3.11+
   ```

2. **Node.js 18 or higher**
   ```bash
   node --version  # Should be 18+
   npm --version
   ```

3. **PostgreSQL 15 or higher**
   ```bash
   postgres --version  # Should be 15+
   ```

4. **Git**
   ```bash
   git --version
   ```

### API Keys

1. **Google Gemini API Key** (Free tier available)
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Save for later use

## Installation Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd simple_rag
```

### 2. Database Setup

#### Option A: Local PostgreSQL

**Install PostgreSQL and pgvector:**

**Ubuntu/Debian:**
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Install build dependencies
sudo apt-get install postgresql-server-dev-15 git build-essential

# Clone and install pgvector
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

**macOS:**
```bash
# Install PostgreSQL
brew install postgresql@15

# Install pgvector
brew install pgvector
```

**Create database:**
```bash
# Start PostgreSQL
sudo service postgresql start  # Linux
brew services start postgresql@15  # macOS

# Create database and user
sudo -u postgres psql
```

```sql
CREATE USER raguser WITH PASSWORD 'ragpassword';
CREATE DATABASE ragdb OWNER raguser;
\c ragdb
CREATE EXTENSION vector;
\q
```

#### Option B: Docker PostgreSQL

```bash
docker run -d \
  --name rag_postgres \
  -e POSTGRES_USER=raguser \
  -e POSTGRES_PASSWORD=ragpassword \
  -e POSTGRES_DB=ragdb \
  -p 5432:5432 \
  ankane/pgvector:latest
```

**Verify installation:**
```bash
psql -h localhost -U raguser -d ragdb -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required .env settings:**
```bash
DATABASE_URL=postgresql://raguser:ragpassword@localhost:5432/ragdb
GEMINI_API_KEY=your_actual_api_key_here
```

**Initialize database:**
```bash
# The application will auto-create tables on first run
# Or manually test connection:
python -c "from app.core.database import init_db, check_db_connection; init_db(); print('Success!' if check_db_connection() else 'Failed')"
```

**Download embedding model (optional - will auto-download on first use):**
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local

# Edit if needed (default should work)
nano .env.local
```

### 5. Verify Installation

**Test backend:**
```bash
cd backend
source venv/bin/activate
python -m pytest
```

**Test backend server:**
```bash
python -m app.main
# Should start on http://localhost:8000
# Visit http://localhost:8000/docs for API documentation
```

**Test frontend:**
```bash
cd frontend
npm run dev
# Should start on http://localhost:3000
```

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Production Mode

**Backend:**
```bash
cd backend
source venv/bin/activate
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

## Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Setup

1. **Set environment variables:**
```bash
# Create .env file in project root
cat > .env << EOF
GEMINI_API_KEY=your_actual_api_key_here
EOF
```

2. **Build and start services:**
```bash
docker-compose up -d
```

3. **Verify services:**
```bash
docker-compose ps
docker-compose logs -f
```

4. **Access application:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

### Docker Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Restart services
docker-compose restart backend

# Stop services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build
```

## Troubleshooting

### Database Connection Issues

**Error: "connection refused"**
```bash
# Check PostgreSQL is running
sudo service postgresql status  # Linux
brew services list  # macOS

# Check connection
psql -h localhost -U raguser -d ragdb

# Check firewall
sudo ufw status  # Linux
```

**Error: "pgvector extension not found"**
```bash
# Verify pgvector is installed
psql -U raguser -d ragdb -c "\dx"

# Reinstall if needed
cd /tmp/pgvector
sudo make install
```

### Backend Issues

**Error: "No module named 'app'"**
```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Verify installation
pip list | grep fastapi
```

**Error: "Gemini API key not found"**
```bash
# Check .env file exists
ls -la backend/.env

# Verify key is set
grep GEMINI_API_KEY backend/.env

# Test API key
curl https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY
```

**Error: "Embedding model download failed"**
```bash
# Manual download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Check disk space
df -h

# Check internet connection
ping huggingface.co
```

### Frontend Issues

**Error: "Cannot find module"**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error: "Port 3000 already in use"**
```bash
# Find and kill process
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

**Error: "API connection failed"**
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Verify CORS settings
# Check backend/.env CORS_ORIGINS includes http://localhost:3000
```

### Docker Issues

**Error: "Cannot connect to Docker daemon"**
```bash
# Start Docker service
sudo systemctl start docker  # Linux
open -a Docker  # macOS
```

**Error: "Port already allocated"**
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :3000
sudo lsof -i :5432

# Stop conflicting services
docker-compose down
```

**Error: "Build failed"**
```bash
# Check Docker logs
docker-compose logs backend

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Testing

### Run Backend Tests

```bash
cd backend
source venv/bin/activate

# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest app/tests/test_document_processor.py

# Specific test
pytest app/tests/test_api.py::TestHealthEndpoint::test_health_check_success
```

### Manual Testing

1. **Upload a document:**
   - Create test.txt with some content
   - Upload via UI or API

2. **Ask questions:**
   - "What is this document about?"
   - "Summarize the main points"

3. **Verify responses:**
   - Check answer quality
   - Verify source citations
   - Test with different documents

## Development Workflow

### Code Quality

```bash
# Format code
cd backend
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Database Migrations

If you modify database models:

```bash
cd backend
source venv/bin/activate

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Environment Variables

**Backend (.env):**
- `DATABASE_URL`: PostgreSQL connection string
- `GEMINI_API_KEY`: Google Gemini API key
- `CHUNK_SIZE`: Characters per chunk (default: 500)
- `CHUNK_OVERLAP`: Overlap size (default: 50)
- `TOP_K_RESULTS`: Number of chunks to retrieve (default: 5)
- `DEBUG`: Enable debug mode (default: True)

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000/api/v1)

## Next Steps

1. ✅ Verify installation
2. ✅ Upload a test document
3. ✅ Ask questions and verify responses
4. 📖 Read [ARCHITECTURE.md](ARCHITECTURE.md) for system details
5. 🚀 Deploy to production (see deployment guides)
6. 📊 Set up monitoring
7. 🔒 Configure authentication (if needed)

## Support

If you encounter issues not covered here:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review GitHub issues
3. Contact: support@example.com
