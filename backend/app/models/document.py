"""
Database models for document and chunk storage.
Uses pgvector for efficient similarity search.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Document(Base):
    """
    Represents an uploaded document.
    Stores metadata and relationships to document chunks.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, txt, md
    file_size = Column(Integer, nullable=False)  # Size in bytes
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    chunk_count = Column(Integer, default=0)

    # Relationship to chunks
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename='{self.filename}', chunks={self.chunk_count})>"


class DocumentChunk(Base):
    """
    Represents a chunk of a document with its embedding.
    Enables semantic search using pgvector.
    """
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position in original document
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)  # all-MiniLM-L6-v2 produces 384-dim vectors
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to parent document
    document = relationship("Document", back_populates="chunks")

    # Indexes for performance
    __table_args__ = (
        Index("idx_document_chunk", "document_id", "chunk_index"),
        Index("idx_embedding", "embedding", postgresql_using="ivfflat", postgresql_with={"lists": 100}),
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk={self.chunk_index})>"
