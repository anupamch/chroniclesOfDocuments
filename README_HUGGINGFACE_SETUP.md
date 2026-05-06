# HuggingFace API Integration - Complete Setup Guide

## ✅ What's Ready to Go

Your backend has been fully configured to use HuggingFace API! Here's what was implemented:

### 1. **Environment Variable Mapping** ✅
Your `.env` file variables are now properly mapped:
- `MODEL_CALL=api` → `model_provider="api"`
- `HUGGINGFACE_ACCESS_TOKEN` → `hf_access_token`
- `MODEL_NAME` → `hf_model_name`

### 2. **Auto-Detecting LLM Client** ✅
The system automatically detects and uses the right provider:
```python
from app.core.llm_client import get_llm

# This works with BOTH Ollama and HuggingFace
llm = get_llm()
response = llm.invoke("Your prompt")
```

### 3. **HuggingFace API Client** ✅
New `app/core/huggingface_client.py` with:
- Basic generation
- Streaming responses
- Batch processing
- Provider detection utilities

### 4. **Startup Validation** ✅
Updated startup check validates both Ollama and HuggingFace configurations

### 5. **Comprehensive Documentation** ✅
- `HUGGINGFACE_QUICK_START.md` - Quick reference
- `HUGGINGFACE_INTEGRATION.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - What was changed

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
# or with uv:
uv sync
```

### Step 2: Verify Configuration
```bash
python validate_config.py
```

Expected output:
```
✅ Settings Object State:
  model_provider: api
  hf_access_token: hf_HRIlWngmTHxBqxbRSmYB...
  hf_model_name: meta-llama/Llama-3.2-3B-Instruct
✅ All validations passed!
```

### Step 3: Test the Integration
```bash
python test_huggingface_integration.py
```

---

## 💻 Usage Examples

### Basic Usage
```python
from app.core.llm_client import get_llm

llm = get_llm()
response = llm.invoke("What is machine learning?")
print(response)
```

### In LangGraph Agents
```python
from app.core.llm_client import get_llm

def extract_agent(state):
    llm = get_llm()
    prompt = f"Extract data from: {state['text']}"
    result = llm.invoke(prompt)
    state['result'] = result
    return state
```

### With System Context
```python
from app.core.huggingface_client import get_huggingface_client

client = get_huggingface_client()
response = client.generate(
    "What is a contract?",
    system_prompt="You are a legal expert"
)
```

### Streaming Response
```python
from app.core.huggingface_client import get_huggingface_client

client = get_huggingface_client()
for chunk in client.generate_streaming("List 5 points about AI:"):
    print(chunk, end="", flush=True)
```

### Batch Processing
```python
from app.core.huggingface_client import get_huggingface_client

client = get_huggingface_client()
prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
results = client.batch_generate(prompts)
```

---

## 🔄 Switching Between Providers

**To use HuggingFace API:**
```env
MODEL_CALL=api
```

**To use Ollama (local):**
```env
MODEL_CALL=local
```

No code changes needed! Same code works with both.

---

## 📁 New & Modified Files

### New Files Created:
1. `backend/app/core/huggingface_client.py` - HuggingFace API client
2. `backend/app/core/startup_check.py` - Configuration validation
3. `backend/examples/huggingface_integration_example.py` - Usage examples
4. `backend/validate_config.py` - Config validator
5. `backend/test_huggingface_integration.py` - Integration tests
6. `HUGGINGFACE_INTEGRATION.md` - Full documentation
7. `HUGGINGFACE_QUICK_START.md` - Quick reference
8. `IMPLEMENTATION_SUMMARY.md` - Implementation details

### Modified Files:
1. `backend/app/core/config.py` - Added Field aliases
2. `backend/app/main.py` - Updated startup check
3. `backend/requirements.txt` - Added langchain-huggingface
4. `backend/pyproject.toml` - Added langchain-huggingface

---

## 🎯 Current Setup Status

Your `.env` file is configured as:
```env
HUGGINGFACE_ACCESS_TOKEN=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
MODEL_NAME=meta-llama/Llama-3.2-3B-Instruct
MODEL_CALL=api
```

✅ **All settings are correct!** The system will use HuggingFace API.

---

## 🧪 Testing

### Run All Tests
```bash
python backend/test_huggingface_integration.py
```

### Test Configuration
```bash
python backend/validate_config.py
```

### Run Examples
```bash
python -m examples.huggingface_integration_example
```

### Manual Test in Python
```python
from app.core.llm_client import get_llm
from app.core.huggingface_client import should_use_huggingface

print(f"Using HuggingFace: {should_use_huggingface()}")
llm = get_llm()
print(f"Provider: {llm.provider}")
```

---

## 📊 Architecture

```
Your Application
       ↓
get_llm() [UnifiedLLM]
       ↓
  model_provider?
    /         \
  api         local
   ↓            ↓
HF API      Ollama
```

---

## 🆘 Troubleshooting

### Issue: "HuggingFace access token is required"
**Solution:** Ensure `HUGGINGFACE_ACCESS_TOKEN` is in `.env`

### Issue: "Model not found"
**Solution:** Check model name on https://huggingface.co

### Issue: "API token is invalid"
**Solution:** Generate new token from https://huggingface.co/settings/tokens

### Issue: Configuration shows wrong values
**Solution:** 
```bash
python validate_config.py  # Debug configuration
```

### Issue: ImportError for huggingface module
**Solution:**
```bash
pip install langchain-huggingface
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `HUGGINGFACE_QUICK_START.md` | Quick reference (this file structure) |
| `HUGGINGFACE_INTEGRATION.md` | Complete documentation |
| `IMPLEMENTATION_SUMMARY.md` | What was changed and why |
| `backend/examples/huggingface_integration_example.py` | 5 practical examples |

---

## 🎓 How It Works

### Configuration Flow
```
.env
 ↓
config.py (Settings)
 ├── MODEL_CALL → model_provider
 ├── HUGGINGFACE_ACCESS_TOKEN → hf_access_token
 └── MODEL_NAME → hf_model_name
 ↓
llm_client.py (UnifiedLLM)
 ├── if model_provider == "api" → HuggingFace
 └── else → Ollama
 ↓
Your Code (get_llm())
 ↓
Response
```

### Automatic Provider Selection
The `UnifiedLLM` class automatically:
1. Reads `model_provider` from settings
2. Initializes the appropriate client
3. Provides same interface for both
4. No code changes needed to switch!

---

## ⚡ Performance

| Provider | Speed | Setup | Cost |
|----------|-------|-------|------|
| **HuggingFace** | Medium | 2 minutes | $0-9/month |
| **Ollama** | Fast | 10 minutes | Free |

---

## 🔒 Security

- HuggingFace token is in `.env` and `.gitignore` (make sure!)
- Token is used only for API authentication
- No sensitive data is logged
- Requests are made over HTTPS

---

## 📝 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Validate config: `python validate_config.py`
3. ✅ Test integration: `python test_huggingface_integration.py`
4. ✅ Start backend: `uvicorn app.main:app --reload`
5. ✅ Use in your code: `llm = get_llm()`

---

## 🌟 Key Features

- ✅ **Automatic Provider Detection** - No hardcoding
- ✅ **Unified API** - Same code for both providers
- ✅ **Drop-in Replacement** - Works with existing code
- ✅ **Zero Breaking Changes** - Fully backwards compatible
- ✅ **Easy to Switch** - Just change `MODEL_CALL` in `.env`
- ✅ **Comprehensive Docs** - Examples and guides included
- ✅ **Validation Tools** - Catch config issues early
- ✅ **Streaming Support** - Real-time response generation
- ✅ **Batch Processing** - Process multiple prompts efficiently

---

## 📞 Support Resources

- **HuggingFace Docs:** https://huggingface.co/docs/hub/api
- **LangChain Docs:** https://python.langchain.com/
- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **Model Hub:** https://huggingface.co/models

---

## 🎉 You're All Set!

Your HuggingFace API integration is ready to use. The system will automatically call HuggingFace API whenever you use:

```python
from app.core.llm_client import get_llm
llm = get_llm()
response = llm.invoke("Your prompt")
```

Happy coding! 🚀
