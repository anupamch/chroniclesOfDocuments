# Quick Start Guide

## Prerequisites

1. **Docker Desktop** - Running
2. **Ollama** - Running on host
   ```bash
   ollama pull llama3.2
   ollama pull llama3.2-vision
   ```

## Step 1: Start the Services

```bash
# Start all services (MongoDB, ChromaDB, Backend API)
docker-compose -f docker-compose.dev.yml up --build
```

Wait for:
```
✓ MongoDB connected
✓ API started at http://localhost:8000
```

## Step 2: Verify API is Running

Open browser: http://localhost:8000/docs

You should see the Swagger UI with all API endpoints.

## Step 3: Run Tests

### Option A: Automated Test Script

**Windows:**
```bash
test_api.bat
```

**Linux/Mac:**
```bash
chmod +x test_api.sh
./test_api.sh
```

### Option B: Manual Testing

**1. Create a Case:**
```bash
curl -X POST http://localhost:8000/api/cases \
  -H "Content-Type: application/json" \
  -d "{\"case_number\": \"CASE-001\", \"title\": \"Test Case\"}"
```

Save the `case_id` from response.

**2. Upload Documents:**
```bash
curl -X POST http://localhost:8000/api/cases/{case_id}/documents \
  -F "files=@test_documents/invoice.txt" \
  -F "files=@test_documents/contract.txt" \
  -F "files=@test_documents/letter.txt"
```

**3. Start Scan:**
```bash
curl -X POST http://localhost:8000/api/cases/{case_id}/scan
```

**4. Check Status:**
```bash
curl http://localhost:8000/api/cases/{case_id}/scan/status
```

Wait a few seconds and check again until `status: "completed"`.

## Expected Results

After scan completes, you should see:

1. **Document Analysis:**
   - Invoice classified as "invoice"
   - Contract classified as "contract"
   - Letter classified as "letter"

2. **Timeline Events:**
   - January 1, 2024: Contract signed
   - January 15, 2024: Invoice issued
   - February 15, 2024: Payment due
   - February 20, 2024: Project completed

3. **Timeline Story:**
   - Chronological narrative of all events
   - Document summaries
   - Key dates and milestones

## Troubleshooting

### API not starting?
```bash
# Check logs
docker-compose -f docker-compose.simple.yml logs backend-simple

# Check if port 8000 is in use
netstat -ano | findstr :8000
```

### Ollama connection failed?
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check Docker can reach host
docker-compose -f docker-compose.simple.yml exec backend-simple ping host.docker.internal
```

### MongoDB connection failed?
```bash
# Check MongoDB is running
docker-compose -f docker-compose.simple.yml ps

# Restart services
docker-compose -f docker-compose.simple.yml restart
```

## Next Steps

1. **Try with real documents** - Upload PDFs, DOCX, images
2. **Create multiple cases** - Organize documents by case
3. **Review timeline stories** - See chronological narratives
4. **Check MongoDB** - View stored metadata
   ```bash
   docker-compose -f docker-compose.simple.yml exec mongodb-dev mongosh chronicles
   ```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Full API docs: See `API.md`

## Stop Services

```bash
docker-compose -f docker-compose.simple.yml down
```

To remove all data:
```bash
docker-compose -f docker-compose.simple.yml down -v
```
