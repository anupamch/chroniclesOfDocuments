"""
HuggingFace API Client Integration

This module provides utilities to work with HuggingFace API when MODEL_CALL is set to "api".
The configuration reads from environment variables:
- HUGGINGFACE_ACCESS_TOKEN: Your HuggingFace API token
- MODEL_NAME: Model to use (e.g., meta-llama/Llama-3.2-3B-Instruct)
- MODEL_CALL: Set to "api" to use HuggingFace API
"""

import logging
from typing import Optional, Any
from app.core.config import settings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_huggingface import ChatHuggingFace

logger = logging.getLogger(__name__)


class HuggingFaceClient:
    """
    Client for HuggingFace API integration
    """

    def __init__(self, temperature: float = 0.3):
        self.temperature = temperature
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize HuggingFace client with proper configuration"""
        if not settings.hf_access_token:
            logger.error("HUGGINGFACE_ACCESS_TOKEN not configured")
            raise ValueError("HuggingFace access token is required but not configured in .env")

        try:
            self.client = ChatHuggingFace(
                llm=settings.hf_model_name,
                token=settings.hf_access_token,
                temperature=self.temperature
            )
            logger.info(f"✓ HuggingFace API client initialized")
            logger.info(f"  Model: {settings.hf_model_name}")
            logger.info(f"  Token: {'*' * 10}...{settings.hf_access_token[-5:]}")
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace client: {e}")
            raise

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using HuggingFace API

        Args:
            prompt: The user prompt/question
            system_prompt: Optional system context

        Returns:
            Generated text response
        """
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))

            response = self.client.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")
            raise

    def generate_streaming(self, prompt: str, system_prompt: Optional[str] = None):
        """
        Generate text using HuggingFace API with streaming

        Args:
            prompt: The user prompt/question
            system_prompt: Optional system context

        Yields:
            Chunks of generated text
        """
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))

            for chunk in self.client.stream(messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f"HuggingFace streaming error: {e}")
            raise

    def batch_generate(self, prompts: list[str], system_prompt: Optional[str] = None) -> list[str]:
        """
        Generate text for multiple prompts

        Args:
            prompts: List of prompts to process
            system_prompt: Optional system context

        Returns:
            List of generated responses
        """
        results = []
        for prompt in prompts:
            try:
                result = self.generate(prompt, system_prompt)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch generation error for prompt '{prompt[:50]}...': {e}")
                results.append(f"Error: {str(e)}")
        return results


def get_huggingface_client(temperature: float = 0.3) -> HuggingFaceClient:
    """
    Factory function to create a HuggingFace client

    Args:
        temperature: Sampling temperature (0.0-1.0)

    Returns:
        HuggingFaceClient instance
    """
    return HuggingFaceClient(temperature=temperature)


def should_use_huggingface() -> bool:
    """
    Check if we should use HuggingFace API based on configuration

    Returns:
        True if MODEL_CALL is "api", False otherwise
    """
    return settings.model_provider == "api"


def get_active_provider() -> str:
    """
    Get the active LLM provider

    Returns:
        "huggingface" if using HuggingFace API, "ollama" if using local Ollama
    """
    return "huggingface" if should_use_huggingface() else "ollama"
