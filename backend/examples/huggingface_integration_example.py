"""
HuggingFace API Integration Examples

This file demonstrates how to use the HuggingFace API when MODEL_CALL="api"
in your .env file.

Usage:
  - Set MODEL_CALL=api in .env
  - Set HUGGINGFACE_ACCESS_TOKEN with your HF token
  - Set MODEL_NAME to your desired model
  - Run this file: python -m examples.huggingface_integration_example
"""

import logging
from app.core.config import settings
from app.core.huggingface_client import (
    get_huggingface_client,
    should_use_huggingface,
    get_active_provider,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_generation():
    """Example 1: Basic text generation"""
    logger.info("\n" + "="*60)
    logger.info("Example 1: Basic Text Generation")
    logger.info("="*60)

    if not should_use_huggingface():
        logger.warning("MODEL_CALL is not set to 'api'. Skipping HuggingFace example.")
        return

    client = get_huggingface_client(temperature=0.3)

    prompt = "What is artificial intelligence?"
    logger.info(f"Prompt: {prompt}")

    try:
        response = client.generate(prompt)
        logger.info(f"Response: {response}")
    except Exception as e:
        logger.error(f"Error: {e}")


def example_with_system_prompt():
    """Example 2: Generation with system context"""
    logger.info("\n" + "="*60)
    logger.info("Example 2: Generation with System Prompt")
    logger.info("="*60)

    if not should_use_huggingface():
        logger.warning("MODEL_CALL is not set to 'api'. Skipping HuggingFace example.")
        return

    client = get_huggingface_client(temperature=0.5)

    system_prompt = "You are a legal expert. Answer questions about contract law."
    prompt = "What is consideration in contract law?"

    logger.info(f"System Prompt: {system_prompt}")
    logger.info(f"User Prompt: {prompt}")

    try:
        response = client.generate(prompt, system_prompt=system_prompt)
        logger.info(f"Response: {response}")
    except Exception as e:
        logger.error(f"Error: {e}")


def example_streaming_generation():
    """Example 3: Streaming generation"""
    logger.info("\n" + "="*60)
    logger.info("Example 3: Streaming Generation")
    logger.info("="*60)

    if not should_use_huggingface():
        logger.warning("MODEL_CALL is not set to 'api'. Skipping HuggingFace example.")
        return

    client = get_huggingface_client(temperature=0.3)

    prompt = "List 5 key points about machine learning in bullet format"

    logger.info(f"Prompt: {prompt}")
    logger.info("Response (streaming):")

    try:
        for chunk in client.generate_streaming(prompt):
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        logger.error(f"Error: {e}")


def example_batch_generation():
    """Example 4: Batch processing multiple prompts"""
    logger.info("\n" + "="*60)
    logger.info("Example 4: Batch Generation")
    logger.info("="*60)

    if not should_use_huggingface():
        logger.warning("MODEL_CALL is not set to 'api'. Skipping HuggingFace example.")
        return

    client = get_huggingface_client(temperature=0.3)

    prompts = [
        "Summarize: Machine learning is a subset of AI",
        "Explain: What is a neural network?",
        "Define: Natural Language Processing",
    ]

    logger.info(f"Processing {len(prompts)} prompts in batch...")

    try:
        responses = client.batch_generate(prompts)
        for i, (prompt, response) in enumerate(zip(prompts, responses), 1):
            logger.info(f"\nPrompt {i}: {prompt}")
            logger.info(f"Response: {response[:200]}...")
    except Exception as e:
        logger.error(f"Error: {e}")


def example_check_configuration():
    """Example 5: Check current configuration"""
    logger.info("\n" + "="*60)
    logger.info("Example 5: Configuration Check")
    logger.info("="*60)

    logger.info(f"Active Provider: {get_active_provider()}")
    logger.info(f"Model Provider Setting: {settings.model_provider}")
    logger.info(f"HuggingFace Model: {settings.hf_model_name}")
    logger.info(f"HuggingFace Token Configured: {'Yes' if settings.hf_access_token else 'No'}")

    if settings.model_provider == "local":
        logger.info(f"Ollama Base URL: {settings.ollama_base_url}")
        logger.info(f"Ollama Model: {settings.ollama_model}")


if __name__ == "__main__":
    logger.info("\n" + "="*60)
    logger.info("HuggingFace API Integration Examples")
    logger.info("="*60)

    # Check configuration
    example_check_configuration()

    # Run examples only if HuggingFace is configured
    if should_use_huggingface():
        example_basic_generation()
        example_with_system_prompt()
        example_streaming_generation()
        example_batch_generation()
    else:
        logger.warning(
            "\n⚠️  MODEL_CALL is not set to 'api'"
        )
        logger.info("To use HuggingFace API, set MODEL_CALL=api in your .env file")
