#!/usr/bin/env python3
"""
Test HuggingFace hub to check available inference models
"""

import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app.core.config import settings

token = settings.hf_access_token
model_name = settings.hf_model_name

print("="*70)
print("HuggingFace Hub API - Model Availability Check")
print("="*70)

# Check if model exists on HuggingFace Hub
headers = {"Authorization": f"Bearer {token}"}

print(f"\n1️⃣ Checking if model exists on Hub: {model_name}")

hub_url = f"https://huggingface.co/api/models/{model_name}"
response = requests.get(hub_url, headers=headers)

if response.status_code == 200:
    model_info = response.json()
    print(f"   ✅ Model exists")
    print(f"   Pipeline: {model_info.get('pipeline_tag', 'N/A')}")
    print(f"   Tags: {model_info.get('tags', [])}")
    print(f"   Private: {model_info.get('private', False)}")
else:
    print(f"   ❌ Model not found ({response.status_code})")

# Try the inference API v2 (newer endpoint)
print(f"\n2️⃣ Trying HuggingFace Inference API v2 (new format)")

api_v2_urls = [
    f"https://api-inference.huggingface.co/models/{model_name}",
    f"https://huggingface.co/inference-api/models/{model_name}",
]

for url in api_v2_urls:
    print(f"\n   Testing: {url}")
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"inputs": "test"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ WORKS!")
    except Exception as e:
        print(f"   Error: {e}")

# Check langchain_huggingface approach
print(f"\n3️⃣ Testing LangChain HuggingFace integration")

try:
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
    
    print("   LangChain imports: OK")
    
    # Test HuggingFaceEndpoint (newer approach)
    try:
        llm = HuggingFaceEndpoint(
            repo_id=model_name,
            huggingfacehub_api_token=token,
            temperature=0.3,
            max_new_tokens=100
        )
        response = llm.invoke("Hello, how are you?")
        print(f"   ✅ HuggingFaceEndpoint works!")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ HuggingFaceEndpoint failed: {e}")
        
except ImportError as e:
    print(f"   ⚠️ LangChain HuggingFace not available: {e}")

print("\n" + "="*70)
print("\n📌 Recommendation:")
print("   The HuggingFace Inference API endpoints appear to be unavailable.")
print("   Consider switching to:")
print()
print("   Option 1: Use Ollama (Local & Fastest)")
print("   ✅ No dependencies on external APIs")
print("   ✅ Works offline")
print("   ✅ Free")
print()
print("   Option 2: Use HuggingFace Inference Endpoints (Paid)")
print("   ✅ Better performance")
print("   ✅ Need to set up at https://huggingface.co/inference-endpoints")
print()
print("   Option 3: Use different model provider (Groq, Anthropic, etc)")
print("   ✅ More reliable")
print("   ✅ Better models")
print("="*70)
