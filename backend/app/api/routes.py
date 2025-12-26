"""
API routes for the RAG system.
Handles document upload, processing, and question answering.
"""
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging
import os
from pathlib import Path
import shutil

from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document, DocumentChunk
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import get_embedding_service
from app.services.llm_service import get_llm_service
from app.services.retrieval_service import get_retrieval_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    document_id: Optional[int] = Field(None, description="Optional document ID to query")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")


class QuestionResponse(BaseModel):
    """Response model for question answers."""
    answer: str = Field(..., description="Generated answer")
    sources: List[dict] = Field(..., description="Source chunks used for answer")
    document_id: Optional[int] = Field(None, description="Document queried")


class DocumentResponse(BaseModel):
    """Response model for document information."""
    id: int
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    upload_date: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    database: bool
    embedding_service: bool
    llm_service: bool


# Helper functions
def save_upload_file(upload_file: UploadFile) -> str:
    """
    Save uploaded file to disk.

    Args:
        upload_file: Uploaded file object

    Returns:
        str: Path to saved file

    Raises:
        HTTPException: If file save fails
    """
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        file_path = upload_dir / upload_file.filename

        # If file exists, add counter
        counter = 1
        while file_path.exists():
            stem = Path(upload_file.filename).stem
            suffix = Path(upload_file.filename).suffix
            file_path = upload_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        # Save file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        logger.info(f"File saved: {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


def validate_file_type(filename: str) -> str:
    """
    Validate and extract file type.

    Args:
        filename: Name of the file

    Returns:
        str: File extension

    Raises:
        HTTPException: If file type is not supported
    """
    supported_types = {".pdf", ".txt", ".md", ".markdown"}
    file_ext = Path(filename).suffix.lower()

    if file_ext not in supported_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Supported types: {supported_types}"
        )

    return file_ext


# API Endpoints

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify all services are operational.
    """
    try:
        # Check database
        from app.core.database import check_db_connection
        db_status = check_db_connection()

        # Check embedding service
        embedding_service = get_embedding_service()
        embedding_status = embedding_service.model is not None

        # Check LLM service
        llm_service = get_llm_service()
        llm_status = llm_service.check_api_status()

        overall_status = "healthy" if all([db_status, embedding_status, llm_status]) else "degraded"

        return HealthResponse(
            status=overall_status,
            database=db_status,
            embedding_service=embedding_status,
            llm_service=llm_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database=False,
            embedding_service=False,
            llm_service=False
        )


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document.
    Extracts text, creates chunks, generates embeddings, and stores in database.
    """
    try:
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.max_upload_size} bytes"
            )

        # Validate file type
        file_type = validate_file_type(file.filename)

        # Save file
        file_path = save_upload_file(file)

        # Process document
        logger.info(f"Processing document: {file.filename}")
        processor = DocumentProcessor()
        full_text, chunks = processor.process_document(file_path, file_type)

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        embedding_service = get_embedding_service()
        embeddings = embedding_service.embed_batch(chunks)

        # Store in database
        logger.info("Storing document in database")
        document = Document(
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            chunk_count=len(chunks)
        )
        db.add(document)
        db.flush()  # Get document ID

        # Store chunks with embeddings
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=idx,
                content=chunk_text,
                embedding=embedding
            )
            db.add(chunk)

        db.commit()
        db.refresh(document)

        logger.info(f"Document uploaded successfully: ID={document.id}")

        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            upload_date=document.upload_date.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about uploaded documents.
    Retrieves relevant chunks and generates an answer using LLM.
    """
    try:
        # Retrieve relevant chunks
        logger.info(f"Processing question: {request.question[:100]}")
        retrieval_service = get_retrieval_service()

        chunks = retrieval_service.retrieve_relevant_chunks(
            query=request.question,
            db=db,
            top_k=request.top_k,
            document_id=request.document_id
        )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant information found. Please upload a document first."
            )

        # Extract chunk texts for LLM
        chunk_texts = [chunk["content"] for chunk in chunks]

        # Generate answer
        logger.info("Generating answer with LLM")
        llm_service = get_llm_service()
        answer = llm_service.generate_answer(
            question=request.question,
            context_chunks=chunk_texts
        )

        # Format sources
        sources = [
            {
                "chunk_id": chunk["id"],
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "content_preview": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                "similarity": round(chunk["similarity"], 3)
            }
            for chunk in chunks
        ]

        return QuestionResponse(
            answer=answer,
            sources=sources,
            document_id=request.document_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    """
    List all uploaded documents.
    """
    try:
        documents = db.query(Document).order_by(Document.upload_date.desc()).all()

        return [
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                chunk_count=doc.chunk_count,
                upload_date=doc.upload_date.isoformat()
            )
            for doc in documents
        ]
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a document and all its chunks.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )

        # Delete from database (cascades to chunks)
        db.delete(document)
        db.commit()

        logger.info(f"Document {document_id} deleted successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific document.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )

        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            upload_date=document.upload_date.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )
