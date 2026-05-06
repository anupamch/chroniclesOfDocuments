# HuggingFace 404 Error Resolution Guide

## Problem Description

**Error Message:**
```
[Analyzer] Error: Client error '404 Not Found' for url 'https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct'
```

**Root Causes:**
1. ❌ **Hardcoded model URL** - The code was using a hardcoded model name instead of the configured one
2. ❌ **Model access issues** - The model may require special permissions or gating
3. ❌ **Insufficient token permissions** - HuggingFace token may not have access to this model
4. ❌ **Missing .env configuration** - No `.env` file exists in the backend directory

---

## ✅ Solution: Already Fixed!

### Fixed Issue
The `llm_client.py` has been updated to use the configured model name instead of hardcoding it:

**Before (Buggy):**
```python
api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"  # Hardcoded!
```

**After (Fixed):**
```python
api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"  # Uses configured model
```

---

## 📋 Setup Steps to Resolve 404 Error

### Step 1: Create `.env` File

Create `backend/.env` with the following configuration:

**Option A: Use HuggingFace API (Recommended for cloud/server)**
```env
# Use HuggingFace API
MODEL_CALL=api

# Get token from: https://huggingface.co/settings/tokens
HUGGINGFACE_ACCESS_TOKEN=hf_YOUR_TOKEN_HERE

# Pick ONE model from the list below
MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
```

**Option B: Use Ollama Local (Recommended for development)**
```env
# Use Ollama (local LLM)
MODEL_CALL=local

# Ollama configuration (if running locally)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:latest
```

### Step 2: Choose a Working Model

If using HuggingFace API (`MODEL_CALL=api`), choose a model from this list:

| Model | Status | Recommendation | Why |
|-------|--------|-----------------|-----|
| `mistralai/Mistral-7B-Instruct-v0.1` | ✅ Works | ⭐⭐⭐ Best | Most reliable, good quality |
| `mistralai/Mistral-Nemo-Instruct-2407` | ✅ Works | ⭐⭐⭐ Newer | Better performance, 12B params |
| `google/gemma-7b-it` | ✅ Works | ⭐⭐⭐ Good | Solid performance |
| `meta-llama/Llama-3.2-1B-Instruct` | ⚠️ May require gating | ⭐⭐ Fallback | Requires HuggingFace account approval |
| `meta-llama/Llama-3.2-3B-Instruct` | ⚠️ May require gating | ⭐⭐⭐ Fallback | Requires HuggingFace account approval |

### Step 3: Verify HuggingFace Access

If using a gated model (like Llama models):

1. Go to https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
2. Click "Request Access" and wait for approval
3. Accept the model card terms
4. Verify your token has read permissions

### Step 4: Verify Configuration

Run this to check your setup:
```bash
cd backend
uv run python -c "
from app.core.config import settings
from app.core.startup_check import check_configuration_on_startup
print('Provider:', settings.model_provider)
print('Model:', settings.hf_model_name if settings.model_provider == 'api' else settings.ollama_model)
try:
    check_configuration_on_startup()
except Exception as e:
    print('Error:', e)
"
```

---

## 🔧 Troubleshooting

### Still Getting 404 Error?

**Cause: Model doesn't exist or requires gating**

Solution:
1. Switch to a non-gated model (Mistral is easiest)
2. Update `.env`:
   ```env
   MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
   ```
3. Test with curl:
   ```bash
   curl -X POST https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1 \
     -H "Authorization: Bearer $HF_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"inputs": "Hello world", "parameters": {"temperature": 0.3, "max_new_tokens": 100}}'
   ```

### Token Rejected / 401 Unauthorized

**Cause: Invalid or expired token**

Solution:
1. Generate new token: https://huggingface.co/settings/tokens
2. Ensure "Read" permission is selected
3. Update `.env`: `HUGGINGFACE_ACCESS_TOKEN=hf_YOUR_NEW_TOKEN`
4. Restart backend

### Model Not Available in Your Region

**Cause: Regional restrictions on some models**

Solution:
1. Use VPN to US region (some models restricted)
2. Switch to universally available model: `mistralai/Mistral-7B-Instruct-v0.1`
3. Or use Ollama (local) instead

---

## 🚀 Quick Start After Fix

### Using HuggingFace
```bash
cd backend

# 1. Create .env
cat > .env << 'EOF'
MODEL_CALL=api
HUGGINGFACE_ACCESS_TOKEN=hf_YOUR_TOKEN_HERE
MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
EOF

# 2. Install dependencies
uv sync

# 3. Run server
uv run fastapi dev app/main.py
```

### Using Ollama (Easier!)
```bash
# 1. Start Ollama (if not running)
# Windows: Download from https://ollama.ai
# Or with Docker:
docker run -d -p 11434:11434 ollama/ollama

# 2. Pull a model
ollama pull deepseek-coder

# 3. Create .env
cat > backend/.env << 'EOF'
MODEL_CALL=local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-coder:latest
EOF

# 4. Run backend
cd backend
uv sync
uv run fastapi dev app/main.py
```

---

## 📊 Provider Comparison

| Aspect | Ollama (Local) | HuggingFace API |
|--------|---|---|
| **Setup Time** | 5 min | 10 min |
| **Cost** | Free | Free (with limits) |
| **Internet Required** | No | Yes |
| **Model Download** | Auto | Auto |
| **Speed** | Fast (local) | Variable (cloud) |
| **Best For** | Development, privacy | Cloud deployment |

---

## ✨ Code Changes Made

### File: `backend/app/core/llm_client.py`

**Line 60-74 (HuggingFaceAPIChat._generate method)**

Changed from hardcoded URLs to dynamic configuration:

```python
# ✅ FIXED: Now uses configured model name
api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"

try:
    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        error_msg = f"HF API error ({response.status_code}): {response.text}"
        logger.error(f"Failed to call {api_url}: {error_msg}")
        raise Exception(error_msg)
```

---

## 📚 Additional Resources

- HuggingFace Inference API Docs: https://huggingface.co/docs/api-inference
- Available Models: https://huggingface.co/models?library=transformers&sort=trending
- Token Settings: https://huggingface.co/settings/tokens
- Ollama Models: https://ollama.ai/library

---

## ✅ Verification Checklist

After following the steps above, verify:

- [ ] `.env` file exists in `backend/` directory
- [ ] `MODEL_CALL` is set to either `api` or `local`
- [ ] If `api`: `HUGGINGFACE_ACCESS_TOKEN` is set with a valid token
- [ ] If `api`: `MODEL_NAME` is set to a non-gated model
- [ ] If `local`: Ollama is running on `localhost:11434`
- [ ] Backend starts without configuration errors
- [ ] Document analysis completes without 404 errors

---

## 🆘 Still Having Issues?

1. Check backend logs: `uv run fastapi dev app/main.py` (look for initialization messages)
2. Verify .env is in correct directory: `backend/.env`
3. Try with Ollama first (easier to debug)
4. Check HuggingFace token permissions
5. Test model directly with curl command above
