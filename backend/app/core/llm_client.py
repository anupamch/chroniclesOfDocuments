"""
Unified LLM Client - Supports both Ollama and HuggingFace

Based on settings:
- model_provider = "local" -> uses Ollama
- model_provider = "api" -> uses HuggingFace
"""

import logging
import requests
from typing import Optional, Any
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class HuggingFaceAPIChat(BaseChatModel):
    """Custom ChatModel wrapper for HuggingFace Inference API"""

    model_name: str
    temperature: float = 0.3
    max_tokens: int = 2048
    token: str

    @property
    def _llm_type(self) -> str:
        return "huggingface_api"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        **kwargs,
    ) -> ChatResult:
        # Convert messages to prompt
        prompt = self._messages_to_prompt(messages)

        # Call HF Inference API - use serverless endpoint
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": self.temperature,
                "max_new_tokens": self.max_tokens,
                "return_full_text": False
            },
            "options": {
                "use_cache": False
            }
        }

        # Use the configured model name in the API URL
        api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"

        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code != 200:
                # Log the error details before failing
                error_msg = f"HF API error ({response.status_code}): {response.text}"
                logger.error(f"Failed to call {api_url}: {error_msg}")
                raise Exception(error_msg)

            result = response.json()

            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                text = result[0].get("generated_text", "")
                # Remove the prompt from the response
                if text.startswith(prompt):
                    text = text[len(prompt):].strip()
            else:
                text = str(result)

            message = AIMessage(content=text)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])

        except Exception as e:
            # Fallback: return a simple response
            logger.warning(f"HF API failed, using fallback: {e}")
            text = "I'm having trouble connecting to the AI service. Please try again later."
            message = AIMessage(content=text)
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])

    def _messages_to_prompt(self, messages: list[BaseMessage]) -> str:
        prompt_parts = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                prompt_parts.append(f"User: {msg.content}")
            elif hasattr(msg, 'content'):
                prompt_parts.append(f"Assistant: {msg.content}")
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)


class UnifiedLLM:
    """
    Unified LLM client that switches between Ollama and HuggingFace
    """

    def __init__(self, temperature: float = 0.3):
        self.temperature = temperature
        self._client = None
        self._provider = None

    def _get_ollama_client(self):
        """Get Ollama client"""
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=self.temperature
        )

    def _get_huggingface_client(self):
        """Get HuggingFace client"""
        if not settings.hf_access_token:
            raise ValueError("HuggingFace access token not configured")

        return HuggingFaceAPIChat(
            model_name=settings.hf_model_name,
            token=settings.hf_access_token,
            temperature=self.temperature,
            max_tokens=2048
        )

    @property
    def client(self):
        """Get the appropriate LLM client based on configuration"""
        if self._client is None:
            if settings.model_provider == "api" and settings.hf_access_token:
                logger.info(f"Using HuggingFace API with model: {settings.hf_model_name}")
                self._client = self._get_huggingface_client()
                self._provider = "huggingface"
            else:
                logger.info(f"Using Ollama with model: {settings.ollama_model}")
                self._client = self._get_ollama_client()
                self._provider = "ollama"
        return self._client

    @property
    def provider(self) -> str:
        """Get the current provider name"""
        if self._client is None:
            # Trigger client initialization
            _ = self.client
        return self._provider or "unknown"

    def invoke(self, prompt: str) -> Any:
        """Invoke the LLM with a prompt"""
        return self.client.invoke(prompt)

    def reset(self):
        """Reset the client to reinitialize on next use"""
        self._client = None
        self._provider = None


def get_llm(temperature: float = 0.3) -> UnifiedLLM:
    """Get a unified LLM instance"""
    return UnifiedLLM(temperature=temperature)


# For backward compatibility - create default instance
def get_default_llm(temperature: float = 0.3):
    """Get default LLM instance (backward compatible)"""
    return UnifiedLLM(temperature=temperature)
