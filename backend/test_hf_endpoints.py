#!/usr/bin/env python3
"""
Diagnostic tool to test HuggingFace Inference API endpoints and models
"""

import requests
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings

print("="*70)
print("HuggingFace Inference API - Endpoint Diagnostics")
print("="*70)

# Configuration
token = settings.hf_access_token
model_name = settings.hf_model_name

print(f"\n📋 Configuration:")
print(f"  Token: {token[:20]}...{token[-5:] if len(token) > 25 else ''}")
print(f"  Model: {model_name}")

if not token:
    print("❌ ERROR: No HuggingFace token configured!")
    sys.exit(1)

# Test different endpoint formats
endpoints = [
    f"https://api-inference.huggingface.co/models/{model_name}",
    f"https://huggingface.co/api/models/{model_name}",
    f"https://huggingface.co/api/inference/{model_name}",
]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "inputs": "Hello, how are you?",
    "parameters": {
        "temperature": 0.3,
        "max_new_tokens": 50,
        "return_full_text": False
    },
    "options": {
        "use_cache": False
    }
}

print(f"\n🧪 Testing different endpoint formats:\n")

for endpoint in endpoints:
    print(f"  URL: {endpoint}")
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        status = response.status_code
        if status == 200:
            print(f"  ✅ Status: {status} OK")
            print(f"  Response: {response.json()[:100]}...")
        elif status == 401:
            print(f"  ❌ Status: {status} Unauthorized (bad token)")
        elif status == 403:
            print(f"  ❌ Status: {status} Forbidden (token lacks permission)")
        elif status == 404:
            print(f"  ❌ Status: {status} Not Found")
        else:
            print(f"  ⚠️  Status: {status}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
    print()

# Test common public models
print("\n🔍 Testing common public models:\n")

public_models = [
    "mistralai/Mistral-7B-Instruct-v0.1",
    "mistralai/Mistral-Nemo-Instruct-2407",
    "google/gemma-7b-it",
    "meta-llama/Llama-2-7b-chat",
    "EleutherAI/gpt-j-6B",
]

for model in public_models:
    url = f"https://api-inference.huggingface.co/models/{model}"
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"  ✅ {model}")
        elif response.status_code == 404:
            print(f"  ❌ {model} (404 - not available via API)")
        elif response.status_code == 401:
            print(f"  ❌ {model} (401 - auth failed)")
        elif response.status_code == 403:
            print(f"  ❌ {model} (403 - forbidden)")
        else:
            print(f"  ⚠️  {model} ({response.status_code})")
    except Exception as e:
        print(f"  ⚠️  {model} (Connection error: {type(e).__name__})")

print("\n" + "="*70)
print("\n💡 If all models return 404, possible causes:")
print("  1. HuggingFace Inference API endpoint changed")
print("  2. Models not available via serverless inference API")
print("  3. Token doesn't have proper permissions")
print("  4. Your region is blocked")
print("\n💡 Solution: Use Ollama (local) instead:")
print("  MODEL_CALL=local")
print("="*70)
