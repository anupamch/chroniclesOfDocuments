# Windows Native Setup (No Docker)

Since Docker is having network issues on your Windows machine, let's run everything natively.

## Prerequisites

1. **Python 3.12+**
   ```bash
   python --version
   ```

2. **Ollama**
   - Download from: https://ollama.ai
   - Install and run:
   ```bash
   ollama pull llama3.2
   ollama pull llama3.2-vision
   ```

3. **MongoDB** (Optional - we'll use file-based storage for now)
   - Download from: https://www.mongodb.com/try/download/community
   - Or skip it, we'll modify the code to work without it

## Quick Setup (5 minutes)

### Step 1: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Create Folders

```bash
mkdir documents
mkdir output
```

### Step 3: Create .env File

Create `backend/.env`:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_VISION_MODEL=llama3.2-vision
OCR_METHOD=vision
INPUT_FOLDER=./documents
OUTPUT_FOLDER=./output
```

### Step 4: Run the Application

```bash
cd backend
python app/main.py
```

### Step 5: Test It

1. Place some documents in `backend/documents/`
2. The system will process them automatically
3. Check results in `backend/output/`

## That's It!

No Docker, no Tesseract installation, no network issues. Everything runs locally with vision models.

## For Production Later

When you deploy to a Linux server, Docker will work fine there. The network issue is Windows-specific.

On Linux server:
```bash
docker-compose up -d
```

Works perfectly with Tesseract OCR.
