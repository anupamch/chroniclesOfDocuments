# HuggingFace API Integration - Quick Reference

## 1. Setup (5 minutes)

### Step 1: Get HuggingFace Token
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Choose "Read" access
4. Copy the token

### Step 2: Update .env File
```env
MODEL_CALL=api
HUGGINGFACE_ACCESS_TOKEN=hf_YourTokenHere
MODEL_NAME=meta-llama/Llama-3.2-3B-Instruct
```

### Step 3: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
# or with uv:
uv sync
```

That's it! 🎉

---

## 2. Usage Examples

### In Your Code
```python
from app.core.llm_client import get_llm

# Get LLM (automatically uses HuggingFace)
llm = get_llm()

# Use it
response = llm.invoke("Your prompt here")
print(response)
```

### In LangGraph Agents
```python
def my_agent(state):
    llm = get_llm()  # Automatically uses HuggingFace
    result = llm.invoke(state['prompt'])
    return result
```

### Check Active Provider
```python
from app.core.huggingface_client import should_use_huggingface

if should_use_huggingface():
    print("Using HuggingFace API")
else:
    print("Using Ollama (local)")
```

---

## 3. Switching Between Ollama and HuggingFace

**Use HuggingFace:**
```env
MODEL_CALL=api
```

**Use Ollama:**
```env
MODEL_CALL=local
```

No code changes needed!

---

## 4. Recommended Models

| Model | Speed | Quality | Parameters |
|-------|-------|---------|-----------|
| `meta-llama/Llama-3.2-1B-Instruct` | ⚡⚡⚡ | ⭐⭐ | 1B |
| `meta-llama/Llama-3.2-3B-Instruct` | ⚡⚡ | ⭐⭐⭐ | 3B |
| `mistralai/Mistral-7B-Instruct-v0.1` | ⚡ | ⭐⭐⭐ | 7B |
| `mistralai/Mistral-Nemo-Instruct-2407` | ⚡ | ⭐⭐⭐⭐ | 12B |
| `google/gemma-7b-it` | ⚡ | ⭐⭐⭐ | 7B |

---

## 5. Configuration Flow

```
.env (MODEL_CALL, HUGGINGFACE_ACCESS_TOKEN, MODEL_NAME)
         ↓
config.py (Settings reads .env)
         ↓
llm_client.py (UnifiedLLM detects provider)
         ↓
Your Code (Uses get_llm() - works with both!)
```

---

## 6. Error Troubleshooting

| Error | Solution |
|-------|----------|
| `HuggingFace access token is required` | Add `HUGGINGFACE_ACCESS_TOKEN=hf_...` to .env |
| `Model not found` | Check model name on https://huggingface.co |
| `API token is invalid` | Generate new token from https://huggingface.co/settings/tokens |
| `Rate limit exceeded` | Upgrade HuggingFace plan or reduce API calls |
| `Connection error` | Check internet connection |

---

## 7. Key Files

| File | Purpose |
|------|---------|
| `app/core/config.py` | Configuration (reads .env) |
| `app/core/llm_client.py` | Unified LLM client (auto-selects provider) |
| `app/core/huggingface_client.py` | HuggingFace specific utilities |
| `app/core/startup_check.py` | Startup validation |
| `HUGGINGFACE_INTEGRATION.md` | Full documentation |

---

## 8. Example: Document Analysis with HuggingFace

```python
from app.core.llm_client import get_llm
from app.core.config import settings

# Initialize LLM (uses HuggingFace if MODEL_CALL=api)
llm = get_llm(temperature=0.3)

# Analyze document
document_text = "Your document content here..."
prompt = f"""Analyze this legal document and extract key terms:
{document_text}

Key terms:"""

response = llm.invoke(prompt)
print("Extracted terms:", response)
```

---

## 9. Cost Comparison

| Provider | Cost | Speed | Internet |
|----------|------|-------|----------|
| **Ollama (local)** | Free | Fast | Not needed |
| **HuggingFace (api)** | Free tier / $9/mo | Medium | Required |

---

## 10. Test It

```bash
cd backend
python -m examples.huggingface_integration_example
```

---

## Summary

✅ **Done in 3 steps:**
1. Get token from https://huggingface.co/settings/tokens
2. Add to `.env`: `MODEL_CALL=api`, `HUGGINGFACE_ACCESS_TOKEN=hf_...`, `MODEL_NAME=...`
3. Use `get_llm()` in your code (same as before!)

Need help? See `HUGGINGFACE_INTEGRATION.md` for detailed docs.
