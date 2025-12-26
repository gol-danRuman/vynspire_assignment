# Simple RAG System

A production-ready Retrieval Augmented Generation (RAG) system for document-based question answering. Upload documents and ask questions using AI-powered semantic search and natural language generation.

![System Architecture](docs/architecture-diagram.png)

## Features

- **Document Upload**: Support for PDF, TXT, and Markdown files
- **Intelligent Chunking**: Context-aware text segmentation with overlap
- **Semantic Search**: Vector-based similarity search using pgvector
- **AI-Powered Answers**: Natural language responses using Google Gemini or DeepSeek
- **Modern UI**: Clean, responsive Next.js interface
- **Production Ready**: Comprehensive tests, Docker support, and monitoring

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with pgvector extension
- LLM API key (choose one):
  - Google Gemini API key (free tier available)
  - DeepSeek API key (recommended, better rate limits)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd simple_rag
```

2. **Set up the backend**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and configure your LLM provider:
# - Set LLM_PROVIDER=deepseek (recommended) or gemini
# - Add your DeepSeek API key or Gemini API key
# - Update database URL if needed
```

3. **Set up PostgreSQL with pgvector**
```bash
# Install PostgreSQL and pgvector extension
# See docs/database-setup.md for detailed instructions

# Create database
createdb ragdb

# The application will automatically enable pgvector extension
```

4. **Set up the frontend**
```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local if needed (default: http://localhost:8000/api/v1)
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m app.main
# Or: uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Docker Deployment

For easier deployment, use Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application at http://localhost:3000

## Usage

### 1. Upload a Document

- Click "Click to upload" or drag and drop a file
- Supported formats: PDF, TXT, MD (max 10MB)
- Wait for processing (chunking + embedding generation)

### 2. Ask Questions

- Type your question in the chat interface
- Optionally select a specific document to query
- View AI-generated answers with source citations

### 3. Manage Documents

- View all uploaded documents
- Select documents for targeted queries
- Delete documents when no longer needed

## Architecture

### System Components

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI    │─────▶│ PostgreSQL  │
│  Frontend   │      │   Backend    │      │  + pgvector │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├─────▶ Sentence Transformers
                            │       (Embeddings)
                            │
                            └─────▶ Google Gemini / DeepSeek
                                    (LLM)
```

### Technology Stack

**Backend:**
- FastAPI (Python web framework)
- PostgreSQL + pgvector (vector database)
- Sentence Transformers (embeddings)
- Google Gemini or DeepSeek API (LLM)
- SQLAlchemy (ORM)

**Frontend:**
- Next.js 14 (React framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Axios (HTTP client)

### Key Design Decisions

1. **Local Embeddings**: Using sentence-transformers for cost-effective, fast embeddings
2. **Pgvector**: PostgreSQL extension for efficient vector similarity search
3. **Chunking Strategy**: Context-aware chunking with overlap to preserve meaning
4. **Multiple LLM Providers**: Support for both Google Gemini and DeepSeek APIs
5. **Modular Architecture**: Clean separation of concerns for maintainability

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design documentation.

## Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ragdb

# LLM Provider (choose 'gemini' or 'deepseek')
LLM_PROVIDER=deepseek

# Google Gemini API (required if LLM_PROVIDER=gemini)
GEMINI_API_KEY=your_gemini_api_key_here

# DeepSeek API (required if LLM_PROVIDER=deepseek)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Document Processing
CHUNK_SIZE=500              # Characters per chunk
CHUNK_OVERLAP=50            # Overlap between chunks
TOP_K_RESULTS=5             # Number of chunks to retrieve

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:3000
```

### Getting Your API Keys

**DeepSeek (Recommended):**

1. Visit <https://platform.deepseek.com/>
2. Sign up for an account
3. Go to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

**Google Gemini:**

1. Visit <https://makersuite.google.com/app/apikey>
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

**Why DeepSeek?**

- Better rate limits for free tier
- Faster response times
- More generous quota
- OpenAI-compatible API

### Frontend Configuration

Edit `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/upload` | Upload document |
| POST | `/api/v1/ask` | Ask question |
| GET | `/api/v1/documents` | List documents |
| GET | `/api/v1/documents/{id}` | Get document |
| DELETE | `/api/v1/documents/{id}` | Delete document |

See [API.md](docs/API.md) for detailed API documentation with examples.

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_document_processor.py

# Run specific test class
pytest app/tests/test_api.py::TestHealthEndpoint
```

### Test Coverage

The test suite includes:
- Unit tests for document processing
- Unit tests for embedding generation
- Integration tests for API endpoints
- Edge case and error handling tests

Target coverage: >80%

## Development

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/

# Run all checks
./scripts/check.sh
```

### Project Structure

```
simple_rag/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Config and database
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   └── tests/            # Test suite
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   ├── components/       # React components
│   │   └── lib/              # API client
│   ├── package.json
│   └── .env.local
├── docs/                     # Documentation
└── docker-compose.yml
```

## Performance Considerations

### Optimization Strategies

1. **Chunking**: Configurable chunk size and overlap for optimal retrieval
2. **Embedding Model**: Fast, lightweight all-MiniLM-L6-v2 (384 dimensions)
3. **Vector Index**: IVFFlat index on pgvector for fast similarity search
4. **Batch Processing**: Efficient batch embedding generation
5. **Connection Pooling**: SQLAlchemy connection pool for database efficiency

### Monitoring

- Health check endpoint for service status
- Structured logging throughout the application
- Database connection monitoring
- API response time tracking (via FastAPI middleware)

## Security & Compliance

### Security Measures

- Input validation on all endpoints
- File type and size restrictions
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration for frontend access
- Environment variable for sensitive data
- No sensitive data in logs or responses

### SOC2 Considerations

- Audit logging for security-relevant actions
- Data encryption in transit (HTTPS in production)
- Access control via API authentication (add as needed)
- Regular dependency updates
- Secure default configurations

See [SECURITY.md](docs/SECURITY.md) for security best practices.

## Troubleshooting

### Common Issues

**1. Database connection fails**
```bash
# Check PostgreSQL is running
pg_isready

# Verify database exists
psql -l | grep ragdb

# Check pgvector extension
psql ragdb -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

**2. Embedding model download fails**
```bash
# Download model manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

**3. LLM API errors**
```bash
# For Gemini - verify API key
echo $GEMINI_API_KEY

# For DeepSeek - verify API key
echo $DEEPSEEK_API_KEY

# Test Gemini API access
curl https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY

# If you hit rate limits with Gemini, switch to DeepSeek:
# Edit .env and change LLM_PROVIDER=deepseek
```

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more solutions.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- **Sentence Transformers**: Efficient embedding generation
- **pgvector**: Vector similarity search in PostgreSQL
- **Google Gemini & DeepSeek**: Free-tier LLM APIs
- **FastAPI**: Modern Python web framework
- **Next.js**: React framework for production

## Support

- **Issues**: https://github.com/your-repo/issues
- **Documentation**: [docs/](docs/)
- **Email**: support@example.com

## Roadmap

Future enhancements:

- [ ] Multi-user support with authentication
- [ ] Conversation history persistence
- [ ] Advanced retrieval strategies (hybrid search)
- [ ] Support for more document types (DOCX, PPTX)
- [ ] Streaming responses from LLM
- [ ] Document summarization
- [ ] Export Q&A history
- [ ] API rate limiting
- [ ] Redis caching for embeddings
- [ ] Monitoring dashboard

---

**Built with ❤️ for Vynspire AI Labs Technical Assessment**
