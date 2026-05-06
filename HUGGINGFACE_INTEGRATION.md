# HuggingFace API Integration Guide

## Overview

The Chronicles of Documents backend now supports HuggingFace API as an alternative to the local Ollama setup. When `MODEL_CALL=api` is set in your `.env` file, the system automatically routes all LLM calls to the HuggingFace API.

## Environment Configuration

### Required Environment Variables

Add these to your `.env` file:

```env
# Use "api" for HuggingFace, "local" for Ollama
MODEL_CALL=api

# Your HuggingFace API token (get from https://huggingface.co/settings/tokens)
HUGGINGFACE_ACCESS_TOKEN=hf_YourTokenHere

# Model name to use
MODEL_NAME=meta-llama/Llama-3.2-3B-Instruct
```

### Alternative Model Names

You can use any model available on HuggingFace that supports text generation:

- `meta-llama/Llama-3.2-3B-Instruct` - Good for most tasks
- `meta-llama/Llama-3.2-1B-Instruct` - Smaller, faster
- `mistralai/Mistral-7B-Instruct-v0.1` - Fast and efficient
- `mistralai/Mistral-Nemo-Instruct-2407` - Latest Mistral
- `google/gemma-7b-it` - Google's model
- `google/gemma-2-9b-it` - Latest Gemma

## How It Works

### Configuration Flow

```
.env variables
    ↓
config.py (Settings class reads .env)
    ├── MODEL_CALL → model_provider
    ├── HUGGINGFACE_ACCESS_TOKEN → hf_access_token
    └── MODEL_NAME → hf_model_name
    ↓
llm_client.py (UnifiedLLM class)
    ├── if model_provider == "api" → Use HuggingFace
    └── else → Use Ollama (local)
    ↓
Your Application Code
```

### Automatic Provider Selection

The system automatically selects the correct provider based on `MODEL_CALL`:

```python
from app.core.llm_client import get_llm

# Get LLM - automatically uses HuggingFace if MODEL_CALL=api
llm = get_llm()

# Use it
result = llm.invoke("Your prompt here")
```

## Usage in Your Code

### Method 1: Using the Unified LLM Client (Recommended)

```python
from app.core.llm_client import get_llm

# Initialize (automatically detects provider)
llm = get_llm(temperature=0.3)

# Invoke
response = llm.invoke("What is AI?")
print(response)
```

### Method 2: Using HuggingFace Directly

```python
from app.core.huggingface_client import get_huggingface_client, should_use_huggingface

# Check if HuggingFace is active
if should_use_huggingface():
    client = get_huggingface_client(temperature=0.3)
    
    # Basic generation
    response = client.generate("Your prompt")
    
    # With system context
    response = client.generate(
        "What is a contract?",
        system_prompt="You are a legal expert"
    )
    
    # Streaming
    for chunk in client.generate_streaming("List 5 points..."):
        print(chunk, end="", flush=True)
    
    # Batch processing
    responses = client.batch_generate([
        "Prompt 1",
        "Prompt 2",
        "Prompt 3"
    ])
```

### Method 3: Check Active Provider

```python
from app.core.huggingface_client import get_active_provider

provider = get_active_provider()
if provider == "huggingface":
    print("Using HuggingFace API")
else:
    print("Using Ollama (local)")
```

## In LangGraph Agents

When using LangGraph agents, the UnifiedLLM automatically adapts:

```python
from langgraph.graph import StateGraph
from app.core.llm_client import get_llm

def extract_agent(state):
    """Automatically uses HuggingFace if MODEL_CALL=api"""
    llm = get_llm()
    
    extraction_prompt = f"Extract key data from: {state['document_text']}"
    result = llm.invoke(extraction_prompt)
    
    state['extraction_result'] = result
    return state

# Create graph with agent
builder = StateGraph(AgentState)
builder.add_node("extract", extract_agent)
```

## Getting a HuggingFace API Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Select "Read" access (sufficient for inference)
4. Copy the token and add to `.env`:
   ```env
   HUGGINGFACE_ACCESS_TOKEN=hf_YourCopiedTokenHere
   ```

## Switching Between Ollama and HuggingFace

Simply change `MODEL_CALL` in your `.env`:

```env
# Use HuggingFace
MODEL_CALL=api

# Use Local Ollama
MODEL_CALL=local
```

No code changes needed! The system automatically adapts.

## Cost Considerations

### HuggingFace API (When MODEL_CALL=api)
- Free tier: Limited inference time
- Pro tier: $9/month - Unlimited inference
- Paid based on usage for larger deployments
- See: https://huggingface.co/pricing

### Local Ollama (When MODEL_CALL=local)
- Free - runs on your machine
- Uses your local GPU/CPU
- No API costs
- Requires Ollama installation

## Dependencies

All required dependencies are included in `requirements.txt`:

```
langchain-huggingface>=0.0.1
langchain>=0.3.0
langchain-core>=0.1.0
```

Install with:
```bash
pip install -r requirements.txt
```

## Error Handling

If HuggingFace is not configured but MODEL_CALL=api:

```
ERROR: HuggingFace access token is required but not configured in .env
```

**Solution:** Add `HUGGINGFACE_ACCESS_TOKEN=hf_...` to `.env`

## Troubleshooting

### Token Error
```
API token is invalid
```
**Solution:** Ensure your token is correct and not expired. Generate a new one from https://huggingface.co/settings/tokens

### Model Not Found
```
Model 'model-name' not found on HuggingFace
```
**Solution:** Check the model name on HuggingFace Hub. It should be in format `owner/model-name`

### Rate Limiting
```
You have exceeded your API rate limit
```
**Solution:** Upgrade HuggingFace plan or reduce API call frequency

### Connection Error
```
Failed to connect to HuggingFace API
```
**Solution:** Check internet connection and ensure API is not blocked by firewall

## Performance Notes

- **HuggingFace API**: Faster for small inference, depends on API servers
- **Ollama Local**: Lower latency if GPU available, suitable for production
- **Temperature**: Adjust 0.0-1.0 for more/less creative responses

## Advanced Configuration

### Custom Temperature per Agent

```python
from app.core.llm_client import get_llm

# Creative responses (higher temperature)
creative_llm = get_llm(temperature=0.8)

# Deterministic responses (lower temperature)
precise_llm = get_llm(temperature=0.2)
```

### Fallback Strategy

```python
from app.core.config import settings

# Set fallback in .env if needed
if settings.model_provider == "api":
    print(f"Primary: HuggingFace ({settings.hf_model_name})")
else:
    print(f"Primary: Ollama ({settings.ollama_model})")
```

## Examples

Run the integration examples:

```bash
cd backend
python -m examples.huggingface_integration_example
```

This demonstrates:
- Basic generation
- Generation with system prompts
- Streaming responses
- Batch processing
- Configuration checking

## Summary

| Feature | Ollama (local) | HuggingFace (api) |
|---------|---|---|
| Setup | Requires Ollama installed | Needs API token |
| Cost | Free | Paid/limited free tier |
| Speed | Fast (local) | Medium (API) |
| Internet | Not needed | Required |
| Configuration | MODEL_CALL=local | MODEL_CALL=api |

---

For more info, see `app/core/huggingface_client.py` and `app/core/llm_client.py`
