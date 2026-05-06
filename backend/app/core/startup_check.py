"""
Startup Configuration Checker

Validates LLM configuration (Ollama or HuggingFace) on application startup
"""

import logging
from app.core.config import settings
from app.core.huggingface_client import should_use_huggingface

logger = logging.getLogger(__name__)


def check_configuration_on_startup():
    """
    Check and validate LLM configuration based on MODEL_CALL setting
    """
    logger.info("\n" + "="*70)
    logger.info("LLM Configuration Check")
    logger.info("="*70)

    if should_use_huggingface():
        check_huggingface_configuration()
    else:
        check_ollama_configuration()

    logger.info("="*70 + "\n")


def check_huggingface_configuration():
    """Check HuggingFace API configuration"""
    logger.info("\n✓ Using HuggingFace API (MODEL_CALL=api)")

    # Check access token
    if not settings.hf_access_token:
        logger.error(
            "\n❌ HUGGINGFACE_ACCESS_TOKEN is not configured!"
        )
        logger.error(
            "   Add to your .env file: HUGGINGFACE_ACCESS_TOKEN=hf_YourTokenHere"
        )
        logger.error(
            "   Get token from: https://huggingface.co/settings/tokens"
        )
        raise ValueError("HuggingFace access token required but not configured")

    logger.info(f"  • Access Token: Configured ✓")
    logger.info(f"  • Token: {'*' * 15}...{settings.hf_access_token[-5:]}")

    # Check model name
    if not settings.hf_model_name:
        logger.error("\n❌ MODEL_NAME is not configured!")
        raise ValueError("HuggingFace model name required but not configured")

    logger.info(f"  • Model: {settings.hf_model_name}")

    # Provide recommended models
    logger.info("\n  Recommended models:")
    recommended = [
        "meta-llama/Llama-3.2-3B-Instruct",
        "meta-llama/Llama-3.2-1B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.1",
        "google/gemma-7b-it",
    ]
    for model in recommended:
        logger.info(f"    - {model}")

    logger.info("\n✓ HuggingFace API configuration is valid")


def check_ollama_configuration():
    """Check Ollama local configuration"""
    logger.info("\n✓ Using Ollama (Local) - MODEL_CALL=local")

    # Check Ollama URL
    if not settings.ollama_base_url:
        logger.warning("  ⚠ Ollama base URL not configured, using default")
        settings.ollama_base_url = "http://localhost:11434"

    logger.info(f"  • Ollama URL: {settings.ollama_base_url}")

    # Check model
    if not settings.ollama_model:
        logger.warning("  ⚠ Ollama model not configured, using default")
        settings.ollama_model = "deepseek-coder:latest"

    logger.info(f"  • Model: {settings.ollama_model}")
    logger.info(f"  • Vision Model: {settings.ollama_vision_model}")

    # Note: Don't fail on Ollama configuration, as it might be set up later
    logger.info(
        "\n  ⓘ Make sure Ollama is running: docker run -d -p 11434:11434 ollama/ollama"
    )


def get_provider_info() -> dict:
    """
    Get information about the current LLM provider

    Returns:
        Dictionary with provider information
    """
    info = {
        "provider": "huggingface" if should_use_huggingface() else "ollama",
        "model_call": settings.model_provider,
    }

    if should_use_huggingface():
        info.update({
            "model": settings.hf_model_name,
            "has_token": bool(settings.hf_access_token),
        })
    else:
        info.update({
            "model": settings.ollama_model,
            "vision_model": settings.ollama_vision_model,
            "base_url": settings.ollama_base_url,
        })

    return info


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_configuration_on_startup()
    
    # Print provider info
    info = get_provider_info()
    logger.info(f"\nProvider Info: {info}")
