# Project Structure

Complete file tree of the Simple RAG System.

```
simple_rag/
│
├── README.md                      # Main documentation
├── QUICKSTART.md                  # 5-minute setup guide
├── PROJECT_SUMMARY.md             # Project overview and deliverables
├── VALIDATION_CHECKLIST.md        # Testing and validation checklist
├── LICENSE                        # MIT License
├── .gitignore                     # Git ignore rules
├── .dockerignore                  # Docker ignore rules
├── docker-compose.yml             # Multi-container Docker setup
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md            # System architecture and design
│   ├── SETUP.md                   # Detailed setup instructions
│   ├── API.md                     # API reference documentation
│   └── DEVELOPER_NOTES.md         # Internal development docs
│
├── backend/                       # Python FastAPI Backend
│   ├── Dockerfile                 # Backend container image
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment variables template
│   ├── .flake8                    # Linter configuration
│   ├── pyproject.toml             # Black and mypy config
│   ├── pytest.ini                 # Test configuration
│   │
│   ├── uploads/                   # Uploaded files directory
│   │   └── .gitkeep               # Keep directory in git
│   │
│   └── app/                       # Main application package
│       ├── __init__.py            # Package initialization
│       ├── main.py                # FastAPI application entry point
│       │
│       ├── core/                  # Core application components
│       │   ├── __init__.py
│       │   ├── config.py          # Configuration management (Pydantic)
│       │   └── database.py        # Database connection and session
│       │
│       ├── models/                # Database models
│       │   ├── __init__.py
│       │   └── document.py        # Document and DocumentChunk models
│       │
│       ├── services/              # Business logic layer
│       │   ├── __init__.py
│       │   ├── document_processor.py    # Text extraction and chunking
│       │   ├── embedding_service.py     # Vector embedding generation
│       │   ├── llm_service.py           # LLM integration (Gemini)
│       │   └── retrieval_service.py     # Similarity search
│       │
│       ├── api/                   # API layer
│       │   ├── __init__.py
│       │   └── routes.py          # REST API endpoints
│       │
│       └── tests/                 # Test suite
│           ├── __init__.py
│           ├── conftest.py        # Test fixtures and configuration
│           ├── test_document_processor.py   # Document processing tests
│           ├── test_embedding_service.py    # Embedding tests
│           └── test_api.py        # API integration tests
│
└── frontend/                      # Next.js Frontend
    ├── Dockerfile                 # Frontend container image
    ├── package.json               # Node dependencies
    ├── package-lock.json          # Locked dependencies
    ├── tsconfig.json              # TypeScript configuration
    ├── next.config.js             # Next.js configuration
    ├── postcss.config.js          # PostCSS configuration
    ├── tailwind.config.js         # Tailwind CSS configuration
    ├── .env.local.example         # Environment variables template
    ├── .eslintrc.json             # ESLint configuration
    │
    └── src/                       # Source code
        ├── app/                   # Next.js App Router
        │   ├── layout.tsx         # Root layout component
        │   ├── page.tsx           # Main page (orchestrates components)
        │   └── globals.css        # Global styles
        │
        ├── components/            # React components
        │   ├── FileUpload.tsx     # Document upload component
        │   ├── DocumentList.tsx   # Document management component
        │   └── ChatInterface.tsx  # Q&A chat component
        │
        └── lib/                   # Utilities and libraries
            └── api.ts             # API client for backend communication
```

## File Count Summary

**Backend**:
- Python files: 15
- Test files: 4
- Configuration files: 5
- Total lines: ~2,500

**Frontend**:
- TypeScript/TSX files: 7
- Configuration files: 6
- Total lines: ~1,200

**Documentation**:
- Markdown files: 10
- Total words: ~10,000

**Total Files**: 48 files across backend, frontend, and documentation

## Key Directories Explained

### `/backend/app/`
Core application code following clean architecture:
- `core/`: Configuration and database setup
- `models/`: SQLAlchemy database models
- `services/`: Business logic (processing, embeddings, retrieval, LLM)
- `api/`: REST API endpoints and request handling
- `tests/`: Comprehensive test suite

### `/frontend/src/`
Next.js 14 application with App Router:
- `app/`: Pages and layouts (App Router structure)
- `components/`: Reusable React components
- `lib/`: Utility functions and API client

### `/docs/`
Complete project documentation:
- Architecture and design decisions
- Setup and deployment guides
- API reference
- Developer notes

## Configuration Files

**Backend**:
- `.env`: Environment variables (not in git)
- `.env.example`: Template for environment setup
- `.flake8`: Python linting rules
- `pyproject.toml`: Black formatter and mypy config
- `pytest.ini`: Test configuration and coverage

**Frontend**:
- `.env.local`: Environment variables (not in git)
- `.env.local.example`: Template for environment setup
- `tsconfig.json`: TypeScript compiler options
- `next.config.js`: Next.js build configuration
- `tailwind.config.js`: Tailwind CSS customization
- `.eslintrc.json`: ESLint rules

**Docker**:
- `docker-compose.yml`: Multi-container orchestration
- `backend/Dockerfile`: Backend container build
- `frontend/Dockerfile`: Frontend container build
- `.dockerignore`: Files to exclude from builds

## Import Paths

**Backend** (Python):
```python
from app.core.config import settings
from app.core.database import get_db
from app.models.document import Document, DocumentChunk
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import get_embedding_service
from app.services.llm_service import get_llm_service
from app.services.retrieval_service import get_retrieval_service
```

**Frontend** (TypeScript):
```typescript
import FileUpload from '@/components/FileUpload';
import DocumentList from '@/components/DocumentList';
import ChatInterface from '@/components/ChatInterface';
import { uploadDocument, askQuestion, getDocuments } from '@/lib/api';
```

## Database Schema

**Tables**:
1. `documents` - Metadata for uploaded documents
2. `document_chunks` - Text chunks with vector embeddings

**Indexes**:
- Primary keys on id columns
- Foreign key index on document_chunks.document_id
- IVFFlat index on document_chunks.embedding (vector similarity)

## API Endpoints

```
GET  /                              # Root endpoint with API info
GET  /api/v1/health                 # Health check
POST /api/v1/upload                 # Upload document
POST /api/v1/ask                    # Ask question
GET  /api/v1/documents              # List all documents
GET  /api/v1/documents/{id}         # Get specific document
DELETE /api/v1/documents/{id}       # Delete document
```

## External Dependencies

**Backend** (Key):
- `fastapi`: Web framework
- `sqlalchemy`: ORM and database toolkit
- `pgvector`: PostgreSQL vector extension
- `sentence-transformers`: Embedding generation
- `google-generativeai`: Gemini LLM integration
- `pytest`: Testing framework

**Frontend** (Key):
- `next`: React framework
- `react`: UI library
- `typescript`: Type safety
- `tailwindcss`: Utility-first CSS
- `axios`: HTTP client
- `react-markdown`: Markdown rendering

## Environment Variables

**Backend** (`.env`):
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
GEMINI_API_KEY=your_api_key
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
DEBUG=True
```

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Build Artifacts (Gitignored)

**Backend**:
- `venv/`, `.venv/`: Virtual environment
- `__pycache__/`: Python bytecode
- `.pytest_cache/`: Test cache
- `htmlcov/`: Coverage reports
- `uploads/*`: Uploaded files

**Frontend**:
- `node_modules/`: NPM packages
- `.next/`: Next.js build output
- `out/`: Export output
- `build/`: Production build

## Size Estimates

**Source Code**:
- Backend: ~100KB
- Frontend: ~80KB
- Documentation: ~150KB
- Total: ~330KB

**Dependencies**:
- Backend (venv): ~1.5GB (includes PyTorch)
- Frontend (node_modules): ~500MB
- Total: ~2GB

**Runtime**:
- Embedding model: ~150MB RAM
- Backend process: ~200MB RAM
- Frontend process: ~100MB RAM
- PostgreSQL: ~100MB RAM
- Total: ~550MB RAM

**Database**:
- Per document: ~1KB metadata
- Per chunk: ~2KB (text + embedding)
- Example (100 docs, 50 chunks each): ~10MB

This structure follows best practices for:
- ✅ Separation of concerns
- ✅ Testability
- ✅ Maintainability
- ✅ Scalability
- ✅ Documentation
