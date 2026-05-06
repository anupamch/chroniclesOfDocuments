# Chronicles of Documents - Agentic System

Multi-agent document analyzer that processes documents from a folder and creates timeline stories.

## Setup

### Quick Start with Docker (Recommended)

**No Tesseract installation needed! Everything runs in containers.**

```bash
# Development (uses Ollama on host)
ollama pull llama3.2
ollama pull llama3.2-vision
docker-compose -f docker-compose.dev.yml up

# Production (uses Tesseract in container)
docker-compose up -d
```

Place documents in `backend/documents/`, check results in `backend/output/`.

See [DOCKER.md](../DOCKER.md) for detailed Docker deployment guide.

---

### Manual Setup (Without Docker)

### Option 1: Using Ollama Vision (Recommended - No OS dependencies!)

1. Install dependencies:
```bash
uv sync
```

2. Install Ollama and pull models:
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2
ollama pull llama3.2-vision  # For image/scan processing

# Verify GPU is being used (should show your RTX 5050)
ollama ps
```

3. Create `.env` file:
```bash
cp .env.example .env
# Set OCR_METHOD=vision (default)
```

4. Create folders:
```bash
mkdir documents output
```

### Option 2: Using Tesseract OCR (Faster, more accurate)

1. Install dependencies:
```bash
uv sync
```

2. Install Ollama:
```bash
ollama pull llama3.2
```

3. Install Tesseract OCR:
```bash
# Windows (using chocolatey)
choco install tesseract

# Or download from: https://github.com/UB-Mannheim/tesseract/wiki
```

4. Install Poppler (for scanned PDFs):
```bash
# Windows (using chocolatey)
choco install poppler

# Or download from: https://github.com/oschwartz10612/poppler-windows/releases
# Add poppler/bin to your PATH
```

5. Create `.env` file and set:
```bash
cp .env.example .env
# Set OCR_METHOD=tesseract
```

6. Create folders:
```bash
mkdir documents output
```

## Supported Document Types

| Type | Extensions | Processing Method |
|------|------------|-------------------|
| PDF (text) | .pdf | Direct text extraction |
| PDF (scanned) | .pdf | OCR (Tesseract or Vision model) |
| Word Documents | .docx, .doc | python-docx |
| Images | .png, .jpg, .jpeg | OCR (Tesseract or Vision model) |
| Scanned Documents | Any image format | OCR with preprocessing |

### OCR Methods

**Vision Model (Default):**
- Uses Ollama's `llama3.2-vision` model
- No OS-level dependencies needed
- Works out of the box
- Slower but more flexible
- Set `OCR_METHOD=vision` in `.env`

**Tesseract:**
- Traditional OCR engine
- Requires OS-level installation
- Faster and more accurate
- Better for batch processing
- Set `OCR_METHOD=tesseract` in `.env`

The system automatically detects scanned PDFs and applies the configured OCR method.

## Performance on Your Hardware (16GB RAM + RTX 5050)

**Expected Performance:**
- Text PDFs/DOCX: ~1-2 seconds per document
- Scanned PDFs (vision): ~5-10 seconds per page
- Images (vision): ~3-5 seconds per image
- GPU acceleration: Enabled automatically

**Tips for Best Performance:**
1. Ollama will automatically use your RTX 5050 GPU
2. Process documents in batches (the system handles this)
3. For large batches (>50 scanned pages), consider using Tesseract OCR method
4. Monitor GPU usage: `nvidia-smi` (should show ollama process)

**Memory Usage:**
- llama3.2: ~4GB RAM
- llama3.2-vision: ~8GB RAM (fits comfortably in your 16GB)
- Multiple documents processed sequentially to avoid memory issues

## Usage

1. Place your documents in the `documents/` folder
   - Supported formats: PDF, DOCX, DOC, PNG, JPG, JPEG

2. Run the analyzer:
```bash
uv run python app/main.py
```

3. Check results in `output/` folder:
   - `analysis_TIMESTAMP.json` - Detailed analysis results
   - `timeline_story_TIMESTAMP.txt` - Human-readable timeline story

## Agent Workflow

```
Document → Extractor → Classifier → Analyzer → Synthesizer → Timeline Story
```

1. **Extractor**: Extracts text, tables, and metadata
2. **Classifier**: Determines document type (invoice, contract, letter, etc.)
3. **Analyzer**: Performs type-specific analysis
4. **Synthesizer**: Creates summary and extracts timeline events

## Example Output

```
TIMELINE STORY
============================================================

Analyzed 3 documents:
  • invoice_jan.pdf (invoice)
  • contract.docx (contract)
  • letter.pdf (letter)

CHRONOLOGICAL TIMELINE:
------------------------------------------------------------

📅 2024-01-15
   Invoice issued for $1,500
   Source: invoice_jan.pdf

📅 2024-02-01
   Contract signed between parties
   Source: contract.docx

📅 2024-02-15
   Payment due date
   Source: invoice_jan.pdf
```
