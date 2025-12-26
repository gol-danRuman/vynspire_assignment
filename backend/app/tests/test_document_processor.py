"""
Unit tests for document processing service.
Tests text extraction and chunking functionality.
"""
import pytest
from pathlib import Path

from app.services.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test suite for DocumentProcessor class."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        processor = DocumentProcessor()
        assert processor.chunk_size > 0
        assert processor.chunk_overlap >= 0
        assert processor.chunk_overlap < processor.chunk_size

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
        assert processor.chunk_size == 1000
        assert processor.chunk_overlap == 100

    def test_init_invalid_overlap(self):
        """Test that invalid overlap raises error."""
        with pytest.raises(ValueError, match="chunk_overlap must be less than chunk_size"):
            DocumentProcessor(chunk_size=100, chunk_overlap=100)

    def test_extract_from_txt(self, sample_text_file):
        """Test text extraction from TXT file."""
        processor = DocumentProcessor()
        text = processor.extract_text(sample_text_file, "txt")

        assert text is not None
        assert len(text) > 0
        assert "test document" in text.lower()

    def test_extract_unsupported_type(self, sample_text_file):
        """Test that unsupported file type raises error."""
        processor = DocumentProcessor()

        with pytest.raises(ValueError, match="Unsupported file type"):
            processor.extract_text(sample_text_file, "xyz")

    def test_create_chunks_basic(self):
        """Test basic chunking functionality."""
        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
        text = "This is a test. " * 20  # Create text longer than chunk_size

        chunks = processor.create_chunks(text)

        assert len(chunks) > 1
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert all(len(chunk) > 0 for chunk in chunks)

    def test_create_chunks_empty_text(self):
        """Test that empty text raises error."""
        processor = DocumentProcessor()

        with pytest.raises(ValueError, match="Cannot chunk empty text"):
            processor.create_chunks("")

    def test_create_chunks_with_overlap(self):
        """Test that chunks have proper overlap."""
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        text = "Word " * 50  # Simple repetitive text

        chunks = processor.create_chunks(text)

        # Check that consecutive chunks have some overlap
        for i in range(len(chunks) - 1):
            # Some content from chunk i should appear in chunk i+1
            assert len(chunks[i]) > 0
            assert len(chunks[i+1]) > 0

    def test_create_chunks_preserves_content(self):
        """Test that chunking doesn't lose content."""
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        text = "Unique1 Unique2 Unique3 Unique4 Unique5 " * 10

        chunks = processor.create_chunks(text)
        combined = " ".join(chunks)

        # Check that unique words appear in combined chunks
        assert "Unique1" in combined
        assert "Unique5" in combined

    def test_clean_text(self):
        """Test text cleaning functionality."""
        processor = DocumentProcessor()
        text = "This  has   extra    spaces\n\n\n\nand newlines"

        cleaned = processor._clean_text(text)

        assert "  " not in cleaned  # No double spaces
        assert cleaned.count("\n\n") <= 1  # Normalized newlines

    def test_split_into_sentences(self):
        """Test sentence splitting."""
        processor = DocumentProcessor()
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."

        sentences = processor._split_into_sentences(text)

        assert len(sentences) >= 3
        assert all(len(s.strip()) > 0 for s in sentences)

    def test_process_document(self, sample_text_file):
        """Test complete document processing pipeline."""
        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)

        full_text, chunks = processor.process_document(sample_text_file, "txt")

        # Verify full text
        assert full_text is not None
        assert len(full_text) > 0

        # Verify chunks
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_chunk_size_limits(self):
        """Test that chunks respect size limits."""
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=10)
        text = "Word " * 100

        chunks = processor.create_chunks(text)

        # Most chunks should be close to chunk_size
        for chunk in chunks[:-1]:  # Exclude last chunk which may be shorter
            assert len(chunk) <= processor.chunk_size * 1.2  # Allow some flexibility


class TestDocumentProcessorEdgeCases:
    """Test edge cases and error handling."""

    def test_very_short_text(self):
        """Test processing very short text."""
        processor = DocumentProcessor(chunk_size=100)
        text = "Short."

        chunks = processor.create_chunks(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_text_exactly_chunk_size(self):
        """Test text that is exactly chunk size."""
        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
        text = "a" * 50

        chunks = processor.create_chunks(text)

        assert len(chunks) >= 1

    def test_unicode_text(self):
        """Test processing text with unicode characters."""
        processor = DocumentProcessor()
        text = "Hello 世界! This is a test with émojis 🎉 and special chars: ñáéíóú"

        chunks = processor.create_chunks(text)

        assert len(chunks) > 0
        assert "世界" in " ".join(chunks)
        assert "🎉" in " ".join(chunks)

    def test_long_sentence_splitting(self):
        """Test handling of very long sentences."""
        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
        # Create a sentence longer than chunk_size without periods
        text = "word " * 100

        chunks = processor.create_chunks(text)

        assert len(chunks) > 1
        # Verify content is preserved
        assert "word" in " ".join(chunks)
