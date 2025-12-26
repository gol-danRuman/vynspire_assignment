# API Documentation

Complete API reference for the Simple RAG System backend.

**Base URL**: `http://localhost:8000/api/v1`

## Authentication

Currently, no authentication is required. For production deployment, implement JWT or API key authentication.

## Endpoints

### Health Check

Check the health status of all system components.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "database": true,
  "embedding_service": true,
  "llm_service": true
}
```

**Status Codes**:
- `200 OK`: Health check completed
- `500 Internal Server Error`: System unhealthy

**Example**:
```bash
curl http://localhost:8000/api/v1/health
```

---

### Upload Document

Upload and process a document for RAG queries.

**Endpoint**: `POST /upload`

**Request**:
- Content-Type: `multipart/form-data`
- Body: Form data with file field

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | Document file (PDF, TXT, MD) |

**Supported File Types**:
- `.pdf` - PDF documents
- `.txt` - Plain text files
- `.md`, `.markdown` - Markdown files

**Size Limit**: 10MB

**Response**:
```json
{
  "id": 1,
  "filename": "example.pdf",
  "file_type": ".pdf",
  "file_size": 524288,
  "chunk_count": 25,
  "upload_date": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `201 Created`: Document uploaded successfully
- `400 Bad Request`: Invalid file type or format
- `413 Payload Too Large`: File exceeds size limit
- `500 Internal Server Error`: Processing failed

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@document.pdf"
```

**Python Example**:
```python
import requests

with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/v1/upload', files=files)
    print(response.json())
```

---

### Ask Question

Ask a question about uploaded documents.

**Endpoint**: `POST /ask`

**Request**:
- Content-Type: `application/json`

**Body Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| question | string | Yes | The question to ask (1-1000 chars) |
| document_id | integer | No | Specific document ID to query |
| top_k | integer | No | Number of chunks to retrieve (1-20, default: 5) |

**Request Example**:
```json
{
  "question": "What are the main points discussed in the document?",
  "document_id": 1,
  "top_k": 5
}
```

**Response**:
```json
{
  "answer": "The document discusses three main points: 1) Introduction to RAG systems...",
  "sources": [
    {
      "chunk_id": 15,
      "document_id": 1,
      "filename": "example.pdf",
      "content_preview": "Retrieval Augmented Generation (RAG) is a technique that...",
      "similarity": 0.892
    }
  ],
  "document_id": 1
}
```

**Status Codes**:
- `200 OK`: Question answered successfully
- `400 Bad Request`: Invalid question format
- `404 Not Found`: No relevant information found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Processing failed

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "top_k": 5
  }'
```

**Python Example**:
```python
import requests

data = {
    "question": "What are the key findings?",
    "document_id": 1,
    "top_k": 5
}

response = requests.post(
    'http://localhost:8000/api/v1/ask',
    json=data
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
```

---

### List Documents

Retrieve all uploaded documents.

**Endpoint**: `GET /documents`

**Response**:
```json
[
  {
    "id": 1,
    "filename": "example.pdf",
    "file_type": ".pdf",
    "file_size": 524288,
    "chunk_count": 25,
    "upload_date": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "filename": "notes.txt",
    "file_type": ".txt",
    "file_size": 2048,
    "chunk_count": 5,
    "upload_date": "2024-01-15T11:00:00Z"
  }
]
```

**Status Codes**:
- `200 OK`: Documents retrieved successfully
- `500 Internal Server Error`: Query failed

**Example**:
```bash
curl http://localhost:8000/api/v1/documents
```

---

### Get Document

Retrieve a specific document by ID.

**Endpoint**: `GET /documents/{document_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| document_id | integer | Document ID |

**Response**:
```json
{
  "id": 1,
  "filename": "example.pdf",
  "file_type": ".pdf",
  "file_size": 524288,
  "chunk_count": 25,
  "upload_date": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- `200 OK`: Document retrieved successfully
- `404 Not Found`: Document does not exist
- `500 Internal Server Error`: Query failed

**Example**:
```bash
curl http://localhost:8000/api/v1/documents/1
```

---

### Delete Document

Delete a document and all its chunks.

**Endpoint**: `DELETE /documents/{document_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| document_id | integer | Document ID |

**Response**: No content

**Status Codes**:
- `204 No Content`: Document deleted successfully
- `404 Not Found`: Document does not exist
- `500 Internal Server Error`: Deletion failed

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/v1/documents/1
```

---

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid file type, malformed request |
| 404 | Not Found | Document doesn't exist, no relevant chunks |
| 413 | Payload Too Large | File exceeds 10MB limit |
| 422 | Unprocessable Entity | Validation error (missing fields, invalid types) |
| 500 | Internal Server Error | Database error, LLM API error, processing error |

---

## Rate Limits

**Current**: No rate limiting implemented

**Recommended for Production**:
- 60 requests per minute per IP
- 10 document uploads per hour per IP
- 100 questions per hour per IP

---

## Interactive Documentation

The API includes automatically generated interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- View all endpoints
- Test API calls directly in the browser
- See request/response schemas
- Download OpenAPI specification

---

## OpenAPI Specification

Download the OpenAPI (Swagger) specification:

```bash
curl http://localhost:8000/openapi.json > api-spec.json
```

---

## SDK Examples

### JavaScript/TypeScript

```typescript
// Using fetch
async function askQuestion(question: string, documentId?: number) {
  const response = await fetch('http://localhost:8000/api/v1/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      document_id: documentId,
      top_k: 5
    })
  });

  return response.json();
}

// Upload document
async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/api/v1/upload', {
    method: 'POST',
    body: formData
  });

  return response.json();
}
```

### Python

```python
import requests
from typing import Optional, List, Dict

class RAGClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url

    def upload_document(self, file_path: str) -> Dict:
        """Upload a document for processing."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/upload", files=files)
            response.raise_for_status()
            return response.json()

    def ask_question(
        self,
        question: str,
        document_id: Optional[int] = None,
        top_k: int = 5
    ) -> Dict:
        """Ask a question about uploaded documents."""
        data = {
            "question": question,
            "top_k": top_k
        }
        if document_id:
            data["document_id"] = document_id

        response = requests.post(f"{self.base_url}/ask", json=data)
        response.raise_for_status()
        return response.json()

    def list_documents(self) -> List[Dict]:
        """Get all uploaded documents."""
        response = requests.get(f"{self.base_url}/documents")
        response.raise_for_status()
        return response.json()

    def delete_document(self, document_id: int) -> None:
        """Delete a document."""
        response = requests.delete(f"{self.base_url}/documents/{document_id}")
        response.raise_for_status()

# Usage
client = RAGClient()

# Upload
doc = client.upload_document("example.pdf")
print(f"Uploaded: {doc['filename']}")

# Ask
result = client.ask_question("What is this about?", document_id=doc['id'])
print(f"Answer: {result['answer']}")

# List
docs = client.list_documents()
print(f"Total documents: {len(docs)}")
```

---

## Webhooks (Future)

Planned webhook support for asynchronous processing:

```json
{
  "event": "document.processed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "document_id": 1,
    "status": "completed",
    "chunk_count": 25
  }
}
```

---

## Versioning

Current API version: `v1`

Future versions will be accessible via different URL paths:
- v1: `/api/v1/`
- v2: `/api/v2/` (future)

Breaking changes will be introduced in new versions only.
