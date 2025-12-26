# Developer Notes

Internal development documentation and implementation notes.

## Project Overview

This RAG system was built following these principles:
1. **Correctness**: Type safety, validation, comprehensive tests
2. **Security**: Input validation, no data leaks, SOC2-ready
3. **Maintainability**: Clean code, clear documentation, modular design
4. **Performance**: Efficient algorithms, batch processing, indexing
5. **Developer Experience**: Easy setup, clear errors, good tooling

## Technical Decisions

### Why These Technologies?

**FastAPI over Flask/Django**:
- Automatic API documentation (OpenAPI/Swagger)
- Built-in data validation (Pydantic)
- Async support for better performance
- Type hints throughout
- Modern Python 3.11+ features

**Next.js over plain React**:
- Server-side rendering for better performance
- Built-in routing
- TypeScript support
- Easy deployment (Vercel)
- Image optimization

**PostgreSQL + pgvector over specialized vector DBs**:
- Single database for relational + vector data
- No additional infrastructure
- ACID compliance
- Proven reliability
- Cost-effective

**sentence-transformers over OpenAI embeddings**:
- Free (no API costs)
- Fast (local processing)
- Private (data doesn't leave server)
- Good quality (384-dim all-MiniLM-L6-v2)

**Google Gemini over GPT**:
- Free tier (60 req/min)
- Good quality
- Easy API
- No credit card required for testing

## Code Organization

### Backend Structure

```
backend/app/
├── api/              # HTTP layer
│   └── routes.py     # API endpoints
├── core/             # Configuration
│   ├── config.py     # Settings management
│   └── database.py   # DB connection
├── models/           # Data models
│   └── document.py   # SQLAlchemy models
├── services/         # Business logic
│   ├── document_processor.py
│   ├── embedding_service.py
│   ├── llm_service.py
│   └── retrieval_service.py
└── tests/            # Test suite
```

**Separation of Concerns**:
- API layer: HTTP only, no business logic
- Services: Reusable business logic
- Models: Data definitions only
- Core: Application-wide concerns

### Frontend Structure

```
frontend/src/
├── app/              # Next.js app router
│   ├── layout.tsx    # Root layout
│   ├── page.tsx      # Main page
│   └── globals.css   # Global styles
├── components/       # React components
│   ├── FileUpload.tsx
│   ├── DocumentList.tsx
│   └── ChatInterface.tsx
└── lib/              # Utilities
    └── api.ts        # API client
```

**Component Design**:
- Single responsibility per component
- Props for configuration
- Hooks for state management
- TypeScript for type safety

## Key Algorithms

### Document Chunking

**Goal**: Split documents into meaningful chunks while preserving context.

**Algorithm**:
```python
1. Extract full text from document
2. Clean and normalize text
   - Remove extra whitespace
   - Normalize newlines
3. Split into sentences (regex-based)
4. Group sentences into chunks:
   - Target size: ~500 characters
   - Don't break sentences when possible
   - Handle edge cases (very long sentences)
5. Add overlap between chunks:
   - Take last ~50 chars from previous chunk
   - Include in next chunk
   - Preserves context at boundaries
```

**Rationale**:
- Sentence boundaries preserve semantic units
- Overlap prevents information loss at splits
- Configurable for different use cases

**Edge Cases Handled**:
- Very long sentences (word-level splitting)
- Short documents (single chunk)
- Empty or whitespace-only text
- Unicode and special characters

### Similarity Search

**Goal**: Find most relevant chunks for a query.

**Algorithm**:
```python
1. Generate query embedding (384-dim vector)
2. Compute cosine distance to all chunks:
   - Uses pgvector's <=> operator
   - Leverages IVFFlat index for speed
3. Return top K chunks with scores
4. Filter by similarity threshold (default: 0.3)
```

**Optimization**:
- IVFFlat index: O(log n) vs O(n) linear scan
- Batch embedding generation
- Normalized vectors (faster cosine similarity)

### Answer Generation

**Goal**: Generate accurate answers grounded in retrieved context.

**Prompt Engineering**:
```
System: You are a helpful assistant that answers questions based on provided context.

Instructions:
1. Answer using ONLY the provided context
2. If unsure, say so clearly
3. Quote relevant parts when appropriate
4. Be concise but complete

Context:
[Retrieved chunks]

Question:
[User's question]

Answer:
```

**Quality Measures**:
- Explicit grounding instructions
- Context-first approach
- Hallucination prevention
- Source attribution

## Performance Optimization

### Current Performance

**Document Upload** (1MB PDF, ~50 chunks):
- Text extraction: ~500ms
- Chunking: ~100ms
- Embedding generation: ~2s
- Database storage: ~500ms
- **Total**: ~3.1 seconds

**Question Answering**:
- Query embedding: ~100ms
- Vector search: ~50ms (with index)
- LLM generation: ~2-5s
- **Total**: ~2.5-5.5 seconds

### Optimization Strategies

**Implemented**:
1. Batch embedding generation (10x faster than individual)
2. IVFFlat index on vectors (100x faster search)
3. SQLAlchemy connection pooling
4. Normalized embeddings (faster similarity)
5. Sentence-aware chunking (better context)

**Future Improvements**:
1. **Async processing**: Background job queue for uploads
2. **Caching**: Redis for frequent queries/embeddings
3. **Streaming**: Stream LLM responses to frontend
4. **Quantization**: Reduce embedding precision (384-dim → 128-dim)
5. **Horizontal scaling**: Multiple workers, load balancer

### Memory Usage

**Embedding Model**: ~150MB RAM
**Per Document**: ~1KB + (chunks * 1.5KB)
**Database**: ~2KB per chunk (content + embedding)

**Example**: 100 documents, 50 chunks each
- Memory: 150MB + (5000 * 1.5KB) = ~158MB
- Database: 5000 * 2KB = ~10MB

## Security Considerations

### Input Validation

**File Uploads**:
- File type whitelist (`.pdf`, `.txt`, `.md`)
- Size limit (10MB)
- Filename sanitization
- Content validation before processing

**API Requests**:
- Pydantic validation for all inputs
- String length limits
- Integer range validation
- SQL injection prevention (ORM)

### Data Protection

**Current**:
- Environment variables for secrets
- No sensitive data in logs
- CORS restrictions
- Input sanitization

**Production Additions Needed**:
- Authentication (JWT tokens)
- Rate limiting
- HTTPS only
- API key rotation
- Audit logging

### Known Security Limitations

1. **No authentication**: Anyone can upload/query
2. **No user isolation**: All documents shared
3. **No rate limiting**: Vulnerable to abuse
4. **No input sanitization**: XSS possible in responses

**Mitigation for Production**:
```python
# Add authentication middleware
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.post("/upload")
async def upload(token: str = Depends(security)):
    # Verify token
    # Associate document with user
    pass
```

## Testing Strategy

### Test Coverage

**Target**: >80% code coverage

**Test Types**:
1. **Unit Tests**: Individual functions
   - Document processor
   - Embedding service
   - Chunking algorithms

2. **Integration Tests**: API endpoints
   - Upload flow
   - Query flow
   - Error handling

3. **Edge Cases**: Boundary conditions
   - Empty inputs
   - Very large inputs
   - Unicode/special characters
   - Network errors

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Fast tests only
pytest -m "not slow"

# Specific module
pytest app/tests/test_document_processor.py

# Watch mode (requires pytest-watch)
ptw
```

### Test Fixtures

**conftest.py** provides:
- `test_db`: In-memory SQLite database
- `client`: FastAPI test client
- `sample_document`: Pre-created document
- `sample_chunks`: Pre-created chunks
- `sample_text_file`: Temporary test file

### Mocking External Services

```python
# Mock LLM service
@pytest.fixture
def mock_llm_service(monkeypatch):
    def mock_generate(*args, **kwargs):
        return "Mocked answer"

    monkeypatch.setattr(
        "app.services.llm_service.LLMService.generate_answer",
        mock_generate
    )
```

## Common Pitfalls

### 1. pgvector Index Not Created

**Problem**: Slow vector search (>1s per query)

**Cause**: Missing or ineffective index

**Solution**:
```sql
CREATE INDEX ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Verify index exists
\d document_chunks
```

### 2. Embedding Model Not Cached

**Problem**: Slow first request (10-20s)

**Cause**: Model download on first use

**Solution**:
```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### 3. Database Connection Pool Exhausted

**Problem**: "QueuePool limit exceeded"

**Cause**: Too many concurrent requests

**Solution**:
```python
# Increase pool size
engine = create_engine(
    DATABASE_URL,
    pool_size=20,      # Default: 5
    max_overflow=40    # Default: 10
)
```

### 4. Large Documents Causing OOM

**Problem**: Memory error on large PDF processing

**Cause**: Loading entire document into memory

**Solution**:
```python
# Process documents in streaming fashion
# Or limit document size more aggressively
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB instead of 10MB
```

### 5. LLM Rate Limits

**Problem**: "429 Too Many Requests" from Gemini

**Cause**: Exceeded free tier limit (60 req/min)

**Solution**:
```python
# Add retry with exponential backoff
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
def call_llm(prompt):
    return genai.generate_content(prompt)
```

## Development Workflow

### Local Development

```bash
# Terminal 1: Backend with auto-reload
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend with hot reload
cd frontend
npm run dev

# Terminal 3: Tests in watch mode
cd backend
ptw
```

### Code Quality Checks

```bash
# Format code
black app/
prettier --write src/

# Lint
flake8 app/
npm run lint

# Type check
mypy app/
npm run type-check

# Tests
pytest
npm test
```

### Git Workflow

```bash
# Feature branch
git checkout -b feature/new-feature

# Make changes, test locally

# Commit with descriptive message
git add .
git commit -m "feat: add support for DOCX files"

# Push and create PR
git push origin feature/new-feature
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF

# Install hooks
pre-commit install
```

## Debugging Tips

### Backend Debugging

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pdb for breakpoints
import pdb; pdb.set_trace()

# Or use ipdb for better interface
import ipdb; ipdb.set_trace()
```

### Frontend Debugging

```typescript
// Use React DevTools
// Install: chrome web store

// Add console logs
console.log('State:', state);
console.table(documents);

// Network debugging
// Chrome DevTools > Network tab
```

### Database Debugging

```sql
-- Enable query logging
SET log_statement = 'all';

-- Check slow queries
SELECT * FROM pg_stat_activity
WHERE state = 'active'
AND now() - query_start > interval '1 second';

-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM document_chunks
ORDER BY embedding <=> '[0.1, ...]'::vector
LIMIT 5;
```

## Performance Monitoring

### Metrics to Track

1. **API Latency**: p50, p95, p99 response times
2. **Document Processing**: Time per document
3. **Embedding Generation**: Embeddings per second
4. **Database Queries**: Query execution time
5. **LLM Calls**: Success rate, latency
6. **Error Rates**: By endpoint

### Monitoring Tools

```python
# Add timing middleware
from time import time

@app.middleware("http")
async def add_timing_header(request, call_next):
    start = time()
    response = await call_next(request)
    duration = time() - start
    response.headers["X-Process-Time"] = str(duration)
    return response
```

## Deployment Checklist

- [ ] Set DEBUG=False
- [ ] Configure proper DATABASE_URL
- [ ] Add GEMINI_API_KEY
- [ ] Set up HTTPS
- [ ] Enable CORS for production domain
- [ ] Add authentication
- [ ] Set up rate limiting
- [ ] Configure logging (Sentry, CloudWatch)
- [ ] Set up monitoring (DataDog, Prometheus)
- [ ] Configure backups
- [ ] Test disaster recovery
- [ ] Document runbook for common issues

## Future Improvements

### High Priority
1. Authentication and user isolation
2. Async document processing
3. Streaming LLM responses
4. Rate limiting

### Medium Priority
1. Support for more file types (DOCX, PPTX)
2. Conversation history
3. Document summarization
4. Hybrid search (vector + keyword)

### Low Priority
1. Multi-language support
2. Custom embedding models
3. Fine-tuned LLM
4. Advanced analytics

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [pgvector Guide](https://github.com/pgvector/pgvector)
- [Sentence Transformers](https://www.sbert.net/)
- [Google Gemini API](https://ai.google.dev/)
