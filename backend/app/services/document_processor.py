"""
Document processing service for chunking and text extraction.
Handles PDF, TXT, and Markdown files with configurable chunking strategy.
"""
import re
from typing import List, Tuple
from pathlib import Path
import logging

import PyPDF2
from docx import Document as DocxDocument
import markdown

from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processes documents by extracting text and creating overlapping chunks.
    Implements intelligent chunking to preserve context.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize document processor with chunking parameters.

        Args:
            chunk_size: Number of characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

        # Validate parameters
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extract text from a file based on its type.

        Args:
            file_path: Path to the file
            file_type: Type of file (pdf, txt, md, docx)

        Returns:
            str: Extracted text content

        Raises:
            ValueError: If file type is not supported
            Exception: If text extraction fails
        """
        try:
            file_type = file_type.lower().replace(".", "")

            if file_type == "pdf":
                return self._extract_from_pdf(file_path)
            elif file_type == "txt":
                return self._extract_from_txt(file_path)
            elif file_type in ["md", "markdown"]:
                return self._extract_from_markdown(file_path)
            elif file_type in ["docx", "doc"]:
                return self._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text_parts = []
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")

        if not text_parts:
            raise ValueError("No text could be extracted from PDF")

        return "\n\n".join(text_parts)

    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from plain text file."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            return file.read()

    def _extract_from_markdown(self, file_path: str) -> str:
        """Extract text from Markdown file (preserving structure)."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            md_content = file.read()

        # Convert markdown to plain text while preserving structure
        html = markdown.markdown(md_content)
        # Remove HTML tags but keep the text
        text = re.sub(r"<[^>]+>", "", html)
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = DocxDocument(file_path)
        text_parts = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
        return "\n\n".join(text_parts)

    def create_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation.

        Uses sentence-aware chunking to avoid breaking sentences when possible.

        Args:
            text: Input text to chunk

        Returns:
            List[str]: List of text chunks

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Cannot chunk empty text")

        # Clean and normalize text
        text = self._clean_text(text)

        # Split into sentences for better chunking
        sentences = self._split_into_sentences(text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If single sentence is longer than chunk_size, split it
            if sentence_length > self.chunk_size:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0

                # Split long sentence
                chunks.extend(self._split_long_sentence(sentence))
                continue

            # Check if adding this sentence exceeds chunk_size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(" ".join(current_chunk))

                # Start new chunk with overlap
                overlap_text = " ".join(current_chunk)
                if len(overlap_text) > self.chunk_overlap:
                    # Keep only the last part for overlap
                    overlap_sentences = []
                    overlap_length = 0
                    for s in reversed(current_chunk):
                        if overlap_length + len(s) <= self.chunk_overlap:
                            overlap_sentences.insert(0, s)
                            overlap_length += len(s)
                        else:
                            break
                    current_chunk = overlap_sentences
                    current_length = overlap_length
                else:
                    current_chunk = []
                    current_length = 0

            current_chunk.append(sentence)
            current_length += sentence_length

        # Add the last chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        logger.info(f"Created {len(chunks)} chunks from text of length {len(text)}")
        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove excessive newlines
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return text.strip()

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex.
        Handles common sentence endings and abbreviations.
        """
        # Simple sentence splitter (can be improved with spaCy/NLTK for production)
        sentence_pattern = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s"
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split a sentence that's longer than chunk_size."""
        chunks = []
        words = sentence.split()
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Overlap for long sentences
                overlap_words = current_chunk[-5:] if len(current_chunk) > 5 else current_chunk
                current_chunk = overlap_words + [word]
                current_length = sum(len(w) + 1 for w in current_chunk)
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def process_document(self, file_path: str, file_type: str) -> Tuple[str, List[str]]:
        """
        Complete document processing pipeline.

        Args:
            file_path: Path to the document
            file_type: Type of document

        Returns:
            Tuple[str, List[str]]: Full text and list of chunks
        """
        logger.info(f"Processing document: {file_path} (type: {file_type})")

        # Extract text
        full_text = self.extract_text(file_path, file_type)

        # Create chunks
        chunks = self.create_chunks(full_text)

        logger.info(f"Document processed: {len(chunks)} chunks created")
        return full_text, chunks
