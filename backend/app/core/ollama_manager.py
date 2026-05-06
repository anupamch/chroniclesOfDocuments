"""
Model Manager - Check and load models on startup

Handles both Ollama (local) and HuggingFace (API) providers.
"""

import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model availability for both Ollama and HuggingFace"""

    # Required models for the application
    REQUIRED_MODELS = {
        "default": settings.ollama_model,
        "vision": settings.ollama_vision_model,
    }

    # Fallback priority order for Ollama
    FALLBACK_MODELS = {
        "default": [
            "deepseek-coder:latest",
            "llama3.2",
            "llama3.1",
            "llama3",
            "mistral",
            "phi3",
            "qwen2.5",
        ],
        "vision": [
            "llama3.2-vision",
            "llava",
            "llama3.2",
        ]
    }

    @staticmethod
    def get_available_models() -> list[str]:
        """Get list of available models from Ollama"""
        try:
            response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.warning(f"Failed to get Ollama models: {e}")
        return []

    @staticmethod
    def is_model_available(model_name: str) -> bool:
        """Check if a specific model is available"""
        available = ModelManager.get_available_models()
        # Check exact match or if the base name matches
        for avail in available:
            if model_name == avail or model_name.split(":")[0] == avail.split(":")[0]:
                return True
        return False

    @staticmethod
    def check_and_load_models() -> dict[str, bool]:
        """
        Check available models and use fallbacks if needed.
        Returns dict of model_name -> is_available
        """
        results = {}
        available = ModelManager.get_available_models()
        logger.info(f"Available Ollama models: {available}")

        if not available:
            logger.error("No Ollama models available!")
            return {"default": False, "vision": False}

        # Check and configure default model
        default_model = settings.ollama_model
        if not ModelManager.is_model_available(default_model):
            logger.warning(f"Model '{default_model}' not found. Looking for fallback...")
            fallback = ModelManager._find_fallback_model("default", available)
            if fallback:
                logger.info(f"Using fallback default model: {fallback}")
                settings.ollama_model = fallback
                default_model = fallback
            else:
                logger.error("No fallback available for default model")
                results[default_model] = False

        results[default_model] = True

        # Check and configure vision model
        vision_model = settings.ollama_vision_model
        if not ModelManager.is_model_available(vision_model):
            logger.warning(f"Vision model '{vision_model}' not found. Looking for fallback...")
            fallback = ModelManager._find_fallback_model("vision", available)
            if fallback:
                logger.info(f"Using fallback vision model: {fallback}")
                settings.ollama_vision_model = fallback
                vision_model = fallback
            else:
                logger.warning("No vision model available, will use default")
                # Use default model as fallback for vision
                settings.ollama_vision_model = settings.ollama_model
                results[vision_model] = False

        if vision_model != settings.ollama_model:
            results[vision_model] = True

        logger.info(f"Using models: default={settings.ollama_model}, vision={settings.ollama_vision_model}")
        return results

    @staticmethod
    def _find_fallback_model(model_type: str, available: list[str]) -> str | None:
        """Find a fallback model if the preferred one is not available"""
        if not available:
            return None

        # Get fallback list for this model type
        fallback_list = ModelManager.FALLBACK_MODELS.get(model_type, [])

        for fallback in fallback_list:
            for avail in available:
                if fallback.lower() in avail.lower():
                    logger.info(f"Found fallback: {avail} for {model_type}")
                    return avail

        # Return first available if no fallback found
        logger.warning(f"No specific fallback found, using first available: {available[0]}")
        return available[0]


def check_ollama_on_startup():
    """Function to call on FastAPI startup"""
    if settings.model_provider == "api":
        # Using HuggingFace API - no local model check needed
        logger.info(f"Using HuggingFace API with model: {settings.hf_model_name}")
        if not settings.hf_access_token:
            logger.warning("HuggingFace access token not configured!")
        return {"provider": "huggingface", "model": settings.hf_model_name}
    else:
        # Using local Ollama - check models
        logger.info("Checking Ollama models on startup...")
        results = ModelManager.check_and_load_models()

        all_available = all(results.values())
        if all_available:
            logger.info("All required Ollama models are available")
        else:
            missing = [k for k, v in results.items() if not v]
            logger.warning(f"Using fallback for models: {missing}")

        return results
