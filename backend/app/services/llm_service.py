"""
LLM service for generating answers using Google Gemini or DeepSeek.
Handles prompt construction and response generation with retrieved context.
"""
from typing import List, Dict, Optional
import logging

import google.generativeai as genai
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with LLM providers (Google Gemini or DeepSeek).
    Generates contextually grounded answers based on retrieved documents.
    """

    def __init__(self, provider: str = None, api_key: str = None):
        """
        Initialize LLM service with specified provider.

        Args:
            provider: LLM provider ('gemini' or 'deepseek')
            api_key: API key for the selected provider
        """
        self.provider = provider or settings.llm_provider

        if self.provider == "gemini":
            self.api_key = api_key or settings.gemini_api_key
            if not self.api_key:
                raise ValueError("Gemini API key is required")

            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)

            # Generation config for Gemini
            self.generation_config = {
                "temperature": settings.temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": settings.max_tokens,
            }

            logger.info(f"LLM service initialized with Gemini model: {settings.gemini_model}")

        elif self.provider == "deepseek":
            self.api_key = api_key or settings.deepseek_api_key
            if not self.api_key:
                raise ValueError("DeepSeek API key is required")

            self.client = OpenAI(
                api_key=self.api_key,
                base_url=settings.deepseek_base_url
            )
            self.model_name = settings.deepseek_model

            logger.info(f"LLM service initialized with DeepSeek model: {settings.deepseek_model}")

        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}. Use 'gemini' or 'deepseek'.")

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

            logger.info(f"Generating answer for question: {question[:100]}...")

            if self.provider == "gemini":
                # Generate response using Gemini
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )

                # Extract text from response (handle different API versions)
                if hasattr(response, 'text'):
                    try:
                        answer = response.text.strip()
                    except ValueError:
                        # If response.text fails, use parts accessor
                        answer = response.candidates[0].content.parts[0].text.strip()
                else:
                    answer = response.candidates[0].content.parts[0].text.strip()

            elif self.provider == "deepseek":
                # Generate response using DeepSeek (OpenAI-compatible)
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens
                )
                answer = response.choices[0].message.content.strip()

            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

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
        Check if the LLM API is accessible and working.

        Returns:
            bool: True if API is working, False otherwise
        """
        try:
            if self.provider == "gemini":
                # Simple test generation for Gemini
                test_response = self.model.generate_content(
                    "Say 'OK' if you can read this.",
                    generation_config={"max_output_tokens": 10}
                )
                # Try different ways to access the response
                try:
                    # Try the simple accessor first
                    text = test_response.text
                    return bool(text)
                except (ValueError, AttributeError):
                    # Fall back to parts accessor
                    if hasattr(test_response, 'candidates') and test_response.candidates:
                        parts = test_response.candidates[0].content.parts
                        return bool(parts and len(parts) > 0)
                    return False

            elif self.provider == "deepseek":
                # Simple test generation for DeepSeek
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
                    max_tokens=10
                )
                return bool(response.choices[0].message.content)

            else:
                return False

        except Exception as e:
            logger.error(f"{self.provider.upper()} API check failed: {e}")
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
