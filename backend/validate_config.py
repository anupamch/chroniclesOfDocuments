"""
Configuration Validation Script

Validates that environment variables are correctly loaded and mapped
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
from dotenv import load_dotenv
load_dotenv()

# Import settings
from app.core.config import settings

print("\n" + "="*70)
print("Configuration Validation")
print("="*70)

print("\n📋 Environment Variables Read:")
print(f"  MODEL_CALL: {os.getenv('MODEL_CALL')}")
print(f"  HUGGINGFACE_ACCESS_TOKEN: {os.getenv('HUGGINGFACE_ACCESS_TOKEN', 'NOT SET')[:20]}...")
print(f"  MODEL_NAME: {os.getenv('MODEL_NAME')}")

print("\n✅ Settings Object State:")
print(f"  model_provider: {settings.model_provider}")
print(f"  hf_access_token: {settings.hf_access_token[:20] if settings.hf_access_token else 'NOT SET'}...")
print(f"  hf_model_name: {settings.hf_model_name}")

print("\n🔍 Mapped Values:")
print(f"  MODEL_CALL → model_provider: {settings.model_provider}")
print(f"  HUGGINGFACE_ACCESS_TOKEN → hf_access_token: {'✓ Set' if settings.hf_access_token else '✗ Not Set'}")
print(f"  MODEL_NAME → hf_model_name: {settings.hf_model_name}")

print("\n📊 Provider Configuration:")
if settings.model_provider == "api":
    print(f"  Active Provider: HuggingFace API")
    print(f"  Model: {settings.hf_model_name}")
    print(f"  Token Status: {'✓ Configured' if settings.hf_access_token else '✗ Missing'}")
else:
    print(f"  Active Provider: Ollama (Local)")
    print(f"  Base URL: {settings.ollama_base_url}")
    print(f"  Model: {settings.ollama_model}")

print("\n" + "="*70)

# Validation checks
errors = []
warnings = []

if settings.model_provider not in ["api", "local"]:
    errors.append(f"Invalid model_provider: '{settings.model_provider}' (must be 'api' or 'local')")

if settings.model_provider == "api":
    if not settings.hf_access_token:
        errors.append("HuggingFace API selected but HUGGINGFACE_ACCESS_TOKEN not configured")
    if not settings.hf_model_name:
        errors.append("HuggingFace API selected but MODEL_NAME not configured")

if errors:
    print("\n❌ ERRORS:")
    for error in errors:
        print(f"  • {error}")
else:
    print("\n✅ All validations passed!")

if warnings:
    print("\n⚠️  WARNINGS:")
    for warning in warnings:
        print(f"  • {warning}")

print("\n" + "="*70 + "\n")

sys.exit(0 if not errors else 1)
