# Chronicles of Documents - API Documentation

## Base URL
```
http://localhost:8000
```

## Interactive API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Endpoints

### 1. Create Case

Create a new case and its folder structure.

**Endpoint:** `POST /api/cases`

**Request Body:**
```json
{
  "case_number": "CASE-2024-001",
  "title": "Contract Dispute - ABC Corp",
  "description": "Optional description"
}
```

**Validations:**
- `case_number`: Required, unique, alphanumeric with hyphens/underscores
- `title`: Required, 1-500 characters
- `description`: Optional, max 2000 characters

**Response:** `201 Created`
```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "case_number": "CASE-2024-001",
  "title": "Contract Dispute - ABC Corp",
  "folder_path": "./documents/550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00Z",
  "status": "active"
}
```

**Errors:**
- `400`: Case number already exists
- `400`: Invalid case number format
- `500`: Server error

---

### 2. Upload Documents

Upload multiple documents to a case in batch.

**Endpoint:** `POST /api/cases/{case_id}/documents`

**Parameters:**
- `case_id` (path): Case ID from create case API

**Request:** `multipart/form-data`
- `files`: Array of files (max 100 files per request)

**Supported File Types:**
- PDF (.pdf)
- Word (.docx, .doc)
- Images (.png, .jpg, .jpeg)

**Validations:**
- Case must exist
- Max file size: 50MB per file
- Max files per upload: 100
- Duplicate detection by file hash
- File type validation

**Response:** `200 OK`
```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "uploaded_files": [
    {
      "document_id": "660e8400-e29b-41d4-a716-446655440001",
      "file_name": "invoice.pdf",
      "file_size": 1024000,
      "status": "pending"
    }
  ],
  "failed_files": [
    {
      "file_name": "large_file.pdf",
      "error": "File size exceeds limit (50MB)"
    }
  ],
  "total_uploaded": 1,
  "total_failed": 1
}
```

**Errors:**
- `400`: No files provided
- `400`: Too many files (>100)
- `404`: Case not found
- `500`: Upload failed

---

### 3. Start Scan

Start scanning and analyzing all documents in a case.

**Endpoint:** `POST /api/cases/{case_id}/scan`

**Parameters:**
- `case_id` (path): Case ID to scan

**Process:**
1. Validates case exists
2. Checks for pending documents
3. Starts background processing:
   - Extracts text (OCR for images/scanned PDFs)
   - Classifies document types
   - Analyzes content
   - Generates summaries
   - Extracts timeline events
   - Creates chronological story

**Response:** `200 OK`
```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "case_number": "CASE-2024-001",
  "total_documents": 5,
  "status": "started",
  "message": "Scan started for 5 documents"
}
```

**Validations:**
- Case must exist
- Case must have at least one pending document

**Errors:**
- `400`: No documents found
- `400`: No pending documents
- `404`: Case not found
- `500`: Scan failed

---

### 4. Get Scan Status

Get scan status and results for a case.

**Endpoint:** `GET /api/cases/{case_id}/scan/status`

**Parameters:**
- `case_id` (path): Case ID

**Response:** `200 OK`
```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "case_number": "CASE-2024-001",
  "status": "completed",
  "total_documents": 5,
  "processed_documents": 5,
  "failed_documents": 0,
  "pending_documents": 0,
  "results": [
    {
      "document_id": "660e8400-e29b-41d4-a716-446655440001",
      "file_name": "invoice.pdf",
      "document_type": "invoice",
      "confidence": 0.95,
      "summary": "Invoice for professional services dated 2024-01-15...",
      "timeline_events": [
        {
          "date": "2024-01-15",
          "event": "Invoice issued",
          "type": "created",
          "source": "invoice.pdf"
        }
      ],
      "errors": []
    }
  ],
  "timeline_story": "TIMELINE STORY - Case: CASE-2024-001\n..."
}
```

**Status Values:**
- `not_started`: No documents processed yet
- `in_progress`: Some documents still pending
- `completed`: All documents processed

**Errors:**
- `404`: Case not found
- `500`: Server error

---

### 5. Health Check

Check API health status.

**Endpoint:** `GET /api/health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "Chronicles of Documents API"
}
```

---

## Usage Flow

```
1. Create Case
   POST /api/cases
   → Get case_id

2. Upload Documents
   POST /api/cases/{case_id}/documents
   → Upload files in batch

3. Start Scan
   POST /api/cases/{case_id}/scan
   → Processing starts in background

4. Check Status (poll)
   GET /api/cases/{case_id}/scan/status
   → Get results and timeline story
```

---

## Example: Complete Workflow

```bash
# 1. Create case
curl -X POST http://localhost:8000/api/cases \
  -H "Content-Type: application/json" \
  -d '{
    "case_number": "CASE-2024-001",
    "title": "Contract Dispute"
  }'

# Response: {"case_id": "550e8400-...", ...}

# 2. Upload documents
curl -X POST http://localhost:8000/api/cases/550e8400-.../documents \
  -F "files=@invoice.pdf" \
  -F "files=@contract.docx" \
  -F "files=@letter.pdf"

# 3. Start scan
curl -X POST http://localhost:8000/api/cases/550e8400-.../scan

# 4. Check status (wait a few seconds, then check)
curl http://localhost:8000/api/cases/550e8400-.../scan/status
```

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

Currently no rate limiting. For production, consider:
- Max 100 requests/minute per IP
- Max 10 concurrent scans per user
- Max 1000 documents per case

---

## File Storage

- Documents stored in: `./documents/{case_id}/`
- Metadata stored in: MongoDB
- Analysis results stored in: MongoDB
- Timeline stories stored in: MongoDB (case document)

---

## Performance

**Expected Processing Times:**
- Text PDF: 1-2 seconds
- Scanned PDF (vision): 5-10 seconds per page
- Images (vision): 3-5 seconds
- DOCX: <1 second

**Recommendations:**
- Upload files in batches of 10-20
- Poll status every 5-10 seconds
- For large cases (>50 docs), expect 5-10 minutes total
