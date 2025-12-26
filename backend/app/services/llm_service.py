"""
LLM service for generating answers using Google Gemini.
Handles prompt construction and response generation with retrieved context.
"""
from typing import List, Dict, Optional
import logging

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with Google Gemini LLM.
    Generates contextually grounded answers based on retrieved documents.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize LLM service with Gemini API.

        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

        # Generation config
        self.generation_config = {
            "temperature": settings.temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": settings.max_tokens,
        }

        logger.info(f"LLM service initialized with model: {settings.gemini_model}")

    def generate_answer(
        self,
        question: str,
        context_chunks: List[str],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate an answer to a question based on retrieved context.

        Args:
            question: User's question
            context_chunks: Retrieved document chunks for context
            conversation_history: Optional chat history for multi-turn conversations

        Returns:
            str: Generated answer

        Raises:
            ValueError: If question or context is invalid
            Exception: If LLM generation fails
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        if not context_chunks:
            return self._generate_no_context_response(question)

        try:
            # Construct prompt with context
            prompt = self._construct_prompt(question, context_chunks, conversation_history)

            # Generate response
            logger.info(f"Generating answer for question: {question[:100]}...")
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            answer = response.text.strip()
            logger.info(f"Answer generated successfully (length: {len(answer)})")

            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def _construct_prompt(
        self,
        question: str,
        context_chunks: List[str],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Construct a prompt with context and instructions for grounded answers.

        Args:
            question: User's question
            context_chunks: Retrieved document chunks
            conversation_history: Optional previous messages

        Returns:
            str: Formatted prompt
        """
        # Format context
        context = "\n\n".join([
            f"[Context {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])

        # Base prompt with instructions
        prompt_parts = [
            "You are a helpful assistant that answers questions based on the provided context.",
            "Your task is to provide accurate, relevant answers grounded in the given context.",
            "",
            "INSTRUCTIONS:",
            "1. Answer the question using ONLY information from the provided context",
            "2. If the context doesn't contain enough information to answer, say so clearly",
            "3. Do not make up information or use external knowledge",
            "4. Quote relevant parts of the context when appropriate",
            "5. Be concise but complete in your answer",
            "6. If the question is unclear, ask for clarification",
            "",
            "CONTEXT:",
            context,
            ""
        ]

        # Add conversation history if available
        if conversation_history:
            prompt_parts.extend([
                "PREVIOUS CONVERSATION:",
                *[f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history[-3:]],  # Last 3 turns
                ""
            ])

        # Add current question
        prompt_parts.extend([
            "QUESTION:",
            question,
            "",
            "ANSWER:"
        ])

        return "\n".join(prompt_parts)

    def _generate_no_context_response(self, question: str) -> str:
        """
        Generate a response when no relevant context is found.

        Args:
            question: User's question

        Returns:
            str: Polite response indicating lack of context
        """
        return (
            "I apologize, but I couldn't find relevant information in the uploaded document "
            "to answer your question. The document may not contain information about this topic, "
            "or the question may be outside the scope of the uploaded content. "
            "\n\nCould you please:"
            "\n1. Rephrase your question to be more specific"
            "\n2. Ensure the uploaded document contains relevant information"
            "\n3. Upload a different document if needed"
        )

    def check_api_status(self) -> bool:
        """
        Check if the Gemini API is accessible and working.

        Returns:
            bool: True if API is working, False otherwise
        """
        try:
            # Simple test generation
            test_response = self.model.generate_content(
                "Say 'OK' if you can read this.",
                generation_config={"max_output_tokens": 10}
            )
            return bool(test_response.text)
        except Exception as e:
            logger.error(f"Gemini API check failed: {e}")
            return False


# Global LLM service instance
_llm_service = None


def get_llm_service() -> LLMService:
    """
    Get or create the global LLM service instance.
    Implements singleton pattern for efficient API reuse.

    Returns:
        LLMService: Global LLM service instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
