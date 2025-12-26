"""
Retrieval service for semantic search using vector similarity.
Handles querying the vector database for relevant document chunks.
"""
from typing import List, Dict, Tuple, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.document import DocumentChunk, Document
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Service for retrieving relevant document chunks using vector similarity.
    Uses pgvector for efficient similarity search.
    """

    def __init__(self):
        """Initialize retrieval service with embedding service."""
        self.embedding_service = get_embedding_service()

    def retrieve_relevant_chunks(
        self,
        query: str,
        db: Session,
        top_k: int = 5,
        document_id: Optional[int] = None,
        similarity_threshold: float = 0.3
    ) -> List[Dict[str, any]]:
        """
        Retrieve the most relevant document chunks for a query.

        Args:
            query: Search query
            db: Database session
            top_k: Number of chunks to retrieve
            document_id: Optional document ID to filter results
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List[Dict]: List of relevant chunks with metadata

        Raises:
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            # Generate query embedding
            logger.info(f"Generating embedding for query: {query[:100]}...")
            query_embedding = self.embedding_service.embed_text(query)

            # Convert to list for SQL query
            embedding_list = query_embedding.tolist()

            # Build query with optional document filter
            sql_parts = [
                "SELECT c.id, c.document_id, c.chunk_index, c.content,",
                "       d.filename, d.file_type,",
                "       1 - (c.embedding <=> :query_embedding) as similarity",
                "FROM document_chunks c",
                "JOIN documents d ON c.document_id = d.id",
            ]

            # Add document filter if specified
            if document_id is not None:
                sql_parts.append("WHERE c.document_id = :document_id")

            sql_parts.extend([
                "ORDER BY c.embedding <=> :query_embedding",
                "LIMIT :top_k"
            ])

            sql = " ".join(sql_parts)

            # Execute query
            params = {
                "query_embedding": str(embedding_list),
                "top_k": top_k
            }
            if document_id is not None:
                params["document_id"] = document_id

            result = db.execute(text(sql), params)
            rows = result.fetchall()

            # Format results
            chunks = []
            for row in rows:
                similarity = row[6]  # similarity score

                # Filter by threshold
                if similarity < similarity_threshold:
                    logger.debug(f"Skipping chunk {row[0]} with low similarity: {similarity:.3f}")
                    continue

                chunk_data = {
                    "id": row[0],
                    "document_id": row[1],
                    "chunk_index": row[2],
                    "content": row[3],
                    "filename": row[4],
                    "file_type": row[5],
                    "similarity": float(similarity)
                }
                chunks.append(chunk_data)

            logger.info(f"Retrieved {len(chunks)} relevant chunks (threshold: {similarity_threshold})")
            return chunks

        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            raise

    def get_document_chunks(
        self,
        db: Session,
        document_id: int,
        limit: int = None
    ) -> List[DocumentChunk]:
        """
        Get all chunks for a specific document.

        Args:
            db: Database session
            document_id: Document ID
            limit: Optional limit on number of chunks

        Returns:
            List[DocumentChunk]: Document chunks
        """
        query = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index)

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_chunk_by_id(self, db: Session, chunk_id: int) -> Optional[DocumentChunk]:
        """
        Get a specific chunk by ID.

        Args:
            db: Database session
            chunk_id: Chunk ID

        Returns:
            Optional[DocumentChunk]: Chunk if found, None otherwise
        """
        return db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()

    def compute_query_document_similarity(
        self,
        query: str,
        db: Session,
        document_id: int
    ) -> float:
        """
        Compute overall similarity between a query and a document.
        Uses average similarity of top chunks.

        Args:
            query: Search query
            db: Database session
            document_id: Document ID

        Returns:
            float: Average similarity score (0-1)
        """
        chunks = self.retrieve_relevant_chunks(
            query=query,
            db=db,
            top_k=10,
            document_id=document_id,
            similarity_threshold=0.0
        )

        if not chunks:
            return 0.0

        # Average of top 5 similarities
        top_similarities = [c["similarity"] for c in chunks[:5]]
        return sum(top_similarities) / len(top_similarities)

    def search_across_documents(
        self,
        query: str,
        db: Session,
        top_k: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        Search across all documents and group results by document.

        Args:
            query: Search query
            db: Database session
            top_k: Number of chunks per document

        Returns:
            Dict[str, List[Dict]]: Results grouped by document
        """
        all_chunks = self.retrieve_relevant_chunks(
            query=query,
            db=db,
            top_k=top_k * 3,  # Get more chunks to ensure diversity
            document_id=None
        )

        # Group by document
        results_by_doc = {}
        for chunk in all_chunks:
            doc_id = chunk["document_id"]
            if doc_id not in results_by_doc:
                results_by_doc[doc_id] = {
                    "filename": chunk["filename"],
                    "file_type": chunk["file_type"],
                    "chunks": []
                }
            results_by_doc[doc_id]["chunks"].append(chunk)

        return results_by_doc


def get_retrieval_service() -> RetrievalService:
    """
    Get retrieval service instance.

    Returns:
        RetrievalService: Retrieval service
    """
    return RetrievalService()
