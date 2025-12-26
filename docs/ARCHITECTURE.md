# Architecture Documentation

## System Overview

The Simple RAG System is built on a modern, scalable architecture that separates concerns and enables independent scaling of components.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Browser                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Port 3000)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ FileUpload   │  │ DocumentList │  │    Chat      │     │
│  │ Component    │  │  Component   │  │  Interface   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                         │                                     │
│                    ┌────▼─────┐                              │
│                    │ API Client│                             │
│                    └────┬─────┘                              │
└─────────────────────────┼─────────────────────────────────┘
                          │ HTTP/REST
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Port 8000)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    API Layer                          │  │
│  │  /upload  /ask  /documents  /health                  │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │              Service Layer                            │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │  Document    │  │  Embedding   │  │    LLM     │ │  │
│  │  │  Processor   │  │   Service    │  │  Service   │ │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │         Retrieval Service                     │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │              Data Layer                               │  │
│  │     SQLAlchemy ORM + Database Models                 │  │
│  └────────────────────┬─────────────────────────────────┘  │
└─────────────────────────┼─────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│             PostgreSQL + pgvector (Port 5432)                │
│  ┌──────────────┐  ┌─────────────────────────────────┐     │
│  │  documents   │  │    document_chunks              │     │
│  │  table       │  │    + vector embeddings          │     │
│  └──────────────┘  └─────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘

                    External Services
┌─────────────────────┐       ┌──────────────────────┐
│  Sentence           │       │   Google Gemini      │
│  Transformers       │       │   API                │
│  (Local)            │       │   (Cloud)            │
└─────────────────────┘       └──────────────────────┘
```

## Component Details

### 1. Frontend (Next.js)

**Technology**: Next.js 14 with TypeScript, Tailwind CSS

**Components**:
- `FileUpload`: Handles document uploads with validation
- `DocumentList`: Displays and manages uploaded documents
- `ChatInterface`: Q&A interface with message history
- `API Client`: Centralized HTTP communication layer

**Key Features**:
- Server-side rendering for better SEO
- Type-safe API communication
- Responsive design
- Real-time feedback for long operations

**Design Patterns**:
- Component composition
- Custom hooks for state management
- API client abstraction

### 2. Backend (FastAPI)

**Technology**: Python 3.11+, FastAPI, SQLAlchemy

#### API Layer (`app/api/`)

Handles HTTP requests and responses:
- Request validation using Pydantic models
- Response serialization
- Error handling and status codes
- CORS configuration

**Endpoints**:
```python
POST /api/v1/upload          # Upload and process document
POST /api/v1/ask             # Ask question
GET  /api/v1/documents       # List all documents
GET  /api/v1/documents/{id}  # Get specific document
DELETE /api/v1/documents/{id} # Delete document
GET  /api/v1/health          # Health check
```

#### Service Layer (`app/services/`)

**DocumentProcessor**:
- Extracts text from PDF, TXT, MD files
- Implements intelligent chunking with overlap
- Preserves context across chunk boundaries

```python
# Chunking Algorithm
1. Extract full text from document
2. Clean and normalize text
3. Split into sentences
4. Group sentences into chunks of ~chunk_size
5. Add overlap from previous chunk
6. Handle long sentences by word-splitting
```

**EmbeddingService**:
- Generates 384-dimensional vectors using all-MiniLM-L6-v2
- Batch processing for efficiency
- Singleton pattern for model reuse
- Normalized embeddings for cosine similarity

**RetrievalService**:
- Queries pgvector for similar chunks
- Filters by similarity threshold
- Supports document-specific or global search
- Returns ranked results with scores

**LLMService**:
- Integrates with Google Gemini API
- Constructs prompts with retrieved context
- Ensures grounded answers
- Handles API errors gracefully

#### Data Layer (`app/models/`)

**Database Models**:

```python
Document:
    - id (PK)
    - filename
    - file_type
    - file_size
    - chunk_count
    - upload_date

DocumentChunk:
    - id (PK)
    - document_id (FK)
    - chunk_index
    - content (TEXT)
    - embedding (VECTOR(384))
    - created_at
```

**Indexes**:
- Primary keys on id columns
- Foreign key index on document_id
- IVFFlat index on embedding vector for fast similarity search

### 3. Database (PostgreSQL + pgvector)

**pgvector Extension**:
- Enables efficient vector similarity search
- Supports cosine distance, L2 distance, inner product
- IVFFlat index for approximate nearest neighbor search

**Vector Operations**:
```sql
-- Similarity search (cosine distance)
SELECT * FROM document_chunks
ORDER BY embedding <=> query_vector
LIMIT 5;

-- Distance operators
<=> : Cosine distance
<-> : L2 distance
<#> : Inner product
```

### 4. External Services

**Sentence Transformers**:
- Model: all-MiniLM-L6-v2
- Dimension: 384
- Speed: ~1000 sentences/sec on CPU
- Quality: Balance of speed and accuracy

**Google Gemini**:
- Model: gemini-pro
- Free tier: 60 requests/minute
- Context window: 30K tokens
- Temperature: 0.7 for balanced creativity

## Data Flow

### Document Upload Flow

```
1. User uploads file (Frontend)
   └─> FileUpload component validates and sends

2. Backend receives file (API Layer)
   └─> Validates file type, size
   └─> Saves to disk

3. Document Processing (Service Layer)
   └─> DocumentProcessor extracts text
   └─> Creates overlapping chunks

4. Embedding Generation (Service Layer)
   └─> EmbeddingService generates vectors
   └─> Batch processing for efficiency

5. Database Storage (Data Layer)
   └─> Creates Document record
   └─> Creates DocumentChunk records with embeddings
   └─> Transaction ensures atomicity

6. Response (API Layer)
   └─> Returns document metadata to frontend
```

### Question Answering Flow

```
1. User asks question (Frontend)
   └─> ChatInterface sends question to backend

2. Query Embedding (Service Layer)
   └─> EmbeddingService generates query vector

3. Similarity Search (Data Layer)
   └─> pgvector finds similar chunks
   └─> Returns top K results with scores

4. Context Preparation (Service Layer)
   └─> RetrievalService formats chunks
   └─> Filters by threshold

5. Answer Generation (Service Layer)
   └─> LLMService constructs prompt
   └─> Calls Gemini API with context
   └─> Receives grounded answer

6. Response (API Layer)
   └─> Returns answer + sources to frontend
   └─> ChatInterface displays in conversation
```

## Design Decisions

### 1. Why Local Embeddings?

**Decision**: Use sentence-transformers locally instead of OpenAI API

**Rationale**:
- Cost: Free vs. $0.0001 per 1K tokens
- Speed: No network latency for embedding generation
- Privacy: Documents don't leave the server
- Reliability: No dependency on external API availability

**Trade-offs**:
- Slightly lower quality than OpenAI embeddings
- Requires more CPU/memory on server
- Model download on first run

### 2. Why pgvector?

**Decision**: PostgreSQL + pgvector vs. specialized vector DBs (Pinecone, Weaviate)

**Rationale**:
- Simplicity: Single database for relational + vector data
- Cost: Free and open-source
- Reliability: PostgreSQL's proven stability
- Ecosystem: Rich tooling and monitoring

**Trade-offs**:
- Slower than specialized vector DBs at scale (>1M vectors)
- Limited advanced features (filtering, metadata)

### 3. Chunking Strategy

**Decision**: Sentence-aware chunking with overlap

**Rationale**:
- Preserves sentence boundaries for better context
- Overlap prevents information loss at boundaries
- Configurable for different document types

**Parameters**:
- chunk_size=500: Balance between context and granularity
- chunk_overlap=50: ~10% overlap for continuity

### 4. Free LLM (Gemini)

**Decision**: Google Gemini free tier vs. paid APIs

**Rationale**:
- Cost: Free for development and testing
- Quality: Comparable to GPT-3.5
- Rate limits: 60 req/min sufficient for demo

**Trade-offs**:
- Rate limits for production use
- Potentially lower quality than GPT-4

## Security Architecture

### Input Validation

```python
# File upload validation
- File type whitelist: [.pdf, .txt, .md]
- Maximum size: 10MB
- Filename sanitization

# Request validation
- Pydantic models for type checking
- Field constraints (min/max length)
- SQL injection prevention via ORM
```

### Authentication & Authorization

**Current**: No authentication (single-user demo)

**Production Considerations**:
```python
# Add JWT authentication
- User registration/login
- Token-based access control
- Per-user document isolation
- Rate limiting per user
```

### Data Protection

- Sensitive data in environment variables
- No logging of document content
- HTTPS in production
- Database connection encryption

## Scalability Considerations

### Current Limitations

1. **Single-instance deployment**
   - No horizontal scaling
   - In-memory model loading

2. **Synchronous processing**
   - File upload blocks until processing completes
   - No background job queue

3. **Database**
   - Single PostgreSQL instance
   - IVFFlat index limited to ~1M vectors

### Scaling Strategy

**Phase 1: Vertical Scaling (1K-10K documents)**
- Increase server resources (CPU, RAM)
- Optimize database queries
- Add connection pooling

**Phase 2: Horizontal Scaling (10K-100K documents)**
- Background job queue (Celery)
- Multiple API workers
- Read replicas for database
- Redis cache for embeddings

**Phase 3: Distributed System (100K+ documents)**
- Microservices architecture
- Dedicated vector database (Qdrant, Milvus)
- Distributed embeddings (model serving)
- Load balancer + API gateway

## Monitoring & Observability

### Health Checks

```python
/health endpoint checks:
- Database connectivity
- Embedding service availability
- LLM API accessibility
```

### Logging

```python
# Structured logging
logger.info("Document uploaded", extra={
    "document_id": doc.id,
    "filename": doc.filename,
    "chunk_count": doc.chunk_count
})
```

### Metrics to Monitor

- API request latency (p50, p95, p99)
- Document processing time
- Embedding generation rate
- Database query performance
- LLM API success rate
- Error rates by endpoint

## Testing Strategy

### Unit Tests
- Document processing logic
- Embedding generation
- Chunking algorithms
- Utility functions

### Integration Tests
- API endpoints
- Database operations
- External service mocking

### End-to-End Tests
- Complete upload flow
- Question answering flow
- Error handling scenarios

## Future Enhancements

1. **Advanced Retrieval**
   - Hybrid search (vector + keyword)
   - Re-ranking with cross-encoders
   - Query expansion

2. **Performance**
   - Async processing
   - Caching layer (Redis)
   - Connection pooling optimization

3. **Features**
   - Multi-document conversation
   - Streaming responses
   - Document summarization
   - Export functionality

4. **Enterprise**
   - Multi-tenancy
   - Role-based access control
   - Audit logging
   - Usage analytics
