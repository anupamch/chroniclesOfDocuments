# Chronicles of Documents - System Flow

This document provides a comprehensive overview of the document processing flow in the Chronicles of Documents system.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENT (Frontend)                                    │
│                        Next.js App + shadcn/ui + Tailwind CSS                         │
└─────────────────────────────────────┬───────────────────────────────────────────────────┘
                                      │
                                      │ HTTP/WebSocket
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  FASTAPI BACKEND                                       │
│                         Python 3.12+ with LangGraph Agents                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │   Auth &    │  │   Case      │  │  Document  │  │    Scan     │  │    Web     │ │
│  │   Admin     │  │   Service   │  │   Service   │  │   Service   │  │  Socket    │ │
│  │   Routes    │  │             │  │             │  │             │  │  Manager   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────┬───────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
            ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
            │   MongoDB    │  │    Local     │  │   ChromaDB   │
            │  Metadata   │  │   File       │  │  Vector      │
            │  Storage    │  │   Storage    │  │  Store       │
            └──────────────┘  └──────────────┘  └──────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              AI PROCESSING LAYER                                       │
│                              LangGraph Multi-Agent System                              │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                        AGENT WORKFLOW (4 Agents)                                  │ │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐                 │ │
│  │  │ Extractor │───▶│ Classifier│───▶│ Analyzer │───▶│Synthesizer│                 │ │
│  │  │  Agent   │    │   Agent   │    │   Agent  │    │   Agent   │                 │ │
│  │  └──────────┘    └──────────┘    └──────────┘    └──────────┘                 │ │
│  └────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                       │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                        LLM: Ollama (Local)                                       │ │
│  │                     Model: llama3.2 (configurable)                              │ │
│  └────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Complete Processing Flow

### 1. User Authentication Flow

```
User Login Request
       │
       ▼
┌──────────────┐
│  POST        │
│ /api/auth    │
│   /login    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│  Validate Credentials       │
│  (username + password)      │
└──────┬───────────────────────┘
       │
       ▼ (Success)
┌──────────────────────────────┐
│  Return JWT Token           │
│  { user_id, role, token }  │
└──────────────────────────────┘
       │
       ▼
All subsequent requests include:
Authorization: Bearer <token>
```

### 2. Case Management Flow

```
Create New Case
       │
       ▼
┌─────────────────────────────────────┐
│  POST /api/cases                    │
│  { case_number, title, description }│
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  CaseService.create_case()          │
│  • Generate UUID for case_id        │
│  • Generate case_number (auto)      │
│  • Create folder in backend/        │
│     documents/{case_id}/            │
│  • Insert into MongoDB: cases       │
│     collection                      │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Return:                           │
│  { case_id, case_number,           │
│    folder_path, status }           │
└─────────────────────────────────────┘
```

### 3. Document Upload Flow

```
Upload Documents to Case
       │
       ▼
┌─────────────────────────────────────┐
│  POST /api/cases/{case_id}/         │
│  documents (multipart/form-data)     │
│  files: [file1.pdf, file2.docx]    │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  DocumentService.upload_documents() │
│  • Validate file type (pdf, docx,   │
│    doc, png, jpg, jpeg)             │
│  • Generate UUID for document_id     │
│  • Save file to:                    │
│    documents/{case_id}/{doc_id}.ext │
│  • Calculate SHA256 hash            │
│  • Insert into MongoDB: documents   │
│    collection with status="pending" │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Return:                           │
│  { documents: [                    │
│    { document_id, file_name,       │
│      file_type, status }           │
│  ]}                                │
└─────────────────────────────────────┘
```

### 4. Document Analysis Flow (Core Processing)

```
Start Document Scan
       │
       ▼
┌─────────────────────────────────────┐
│  POST /api/cases/{case_id}/scan    │
│  (Background task triggered)        │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  ScanService.start_scan()           │
│  • Get all documents with          │
│    status="pending"                │
│  • Return scan initiation info      │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Background:                       │
│  ScanService.process_case_         │
│  documents(case_id)                │
└─────────────────┬───────────────────┘
                  │
                  ▼
         ┌────────┴────────┐
         │ For each document│
         └────────┬────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           LANGGRAPH WORKFLOW                                         │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐│
│  │ STEP 1: EXTRACTOR AGENT                                                        ││
│  │ ┌─────────────────────────────────────────────────────────────────────────┐  ││
│  │ │ • Input: file_path (local PDF/DOCX/Image)                               │  ││
│  │ │ • Detect file type and call appropriate parser:                         │  ││
│  │ │   - PDF → pypdf (text) + pdfplumber (tables)                           │  ││
│  │ │   - DOCX → python-docx                                                  │  ││
│  │ │   - Image → OCR (tesseract/cloud/vision based on config)               │  ││
│  │ │ • If PDF has < 50 chars → scanned PDF → trigger OCR                    │  ││
│  │ │ • Output: { extracted_text, tables }                                   │  ││
│  │ └─────────────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────────────┘│
│                                      │                                                │
│                                      ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐│
│  │ STEP 2: CLASSIFIER AGENT                                                     ││
│  │ ┌─────────────────────────────────────────────────────────────────────────┐  ││
│  │ │ • Input: extracted_text (first 2000 chars)                            │  ││
│  │ │ • LLM Prompt: Classify document into ONE category:                   │  ││
│  │ │   invoice | contract | letter | chat | receipt | legal_document |     │  ││
│  │ │   generic                                                                │  ││
│  │ │ • Output: { document_type, classification_confidence }                │  ││
│  │ └─────────────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────────────┘│
│                                      │                                                │
│                                      ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐│
│  │ STEP 3: ANALYZER AGENT (Type-Specific)                                     ││
│  │ ┌─────────────────────────────────────────────────────────────────────────┐  ││
│  │ │ • Input: extracted_text + document_type                                │  ││
│  │ │ • Type-specific prompts:                                               │  ││
│  │ │   ┌─────────────────────────────────────────────────────────────────┐ │  ││
│  │ │   │ invoice: Extract invoice number, date, amount, currency,         │ │  ││
│  │ │   │            vendor, line items, payment terms                    │ │  ││
│  │ │   ├─────────────────────────────────────────────────────────────────┤ │  ││
│  │ │   │ contract: Extract contract type, parties, effective date,       │ │  ││
│  │ │   │            expiration, key terms, payment terms                 │ │  ││
│  │ │   ├─────────────────────────────────────────────────────────────────┤ │  ││
│  │ │   │ letter: Extract date, subject, key points, action items, tone  │ │  ││
│  │ │   ├─────────────────────────────────────────────────────────────────┤ │  ││
│  │ │   │ chat: Extract participants, date range, topics, decisions      │ │  ││
│  │ │   ├─────────────────────────────────────────────────────────────────┤ │  ││
│  │ │   │ generic: Extract main topic, key points, dates, actions        │ │  ││
│  │ │   └─────────────────────────────────────────────────────────────────┘ │  ││
│  │ │ • Output: { analysis_results: { type, raw_analysis } }              │  ││
│  │ └─────────────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────────────┘│
│                                      │                                                │
│                                      ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐│
│  │ STEP 4: SYNTHESIZER AGENT                                                  ││
│  │ ┌─────────────────────────────────────────────────────────────────────────┐  ││
│  │ │ • Input: analysis_results + document_type                             │  ││
│  │ │ • Generate summary (2-3 sentences):                                  │  ││
│  │ │   "Invoice #INV-2024-001 for $1,500 from ABC Corp..."                │  ││
│  │ │ • Extract timeline events:                                            │  ││
│  │ │   - Parse dates from document                                         │  ││
│  │ │   - Categorize: created | signed | payment_due | deadline |        │  ││
│  │ │     meeting | other                                                  │  ││
│  │ │ • Output: { summary, timeline_events: [] }                         │  ││
│  │ └─────────────────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────────────┘│
│                                      │                                                │
│                                      ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐│
│  │ SAVE RESULTS                                                               ││
│  │ • Update document status to "completed"                                   ││
│  │ • Insert into MongoDB: analysis_results collection                        ││
│  │ • Broadcast via WebSocket: document_processed                             ││
│  └─────────────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 5. Timeline Generation Flow

```
After All Documents Processed
       │
       ▼
┌─────────────────────────────────────┐
│  ScanService.generate_              │
│  timeline_story()                  │
└─────────────────┬───────────────────┘
                  │
                  ▼
         ┌────────┴────────┐
         │ Collect all     │
         │ timeline_events │
         │ from documents  │
         └────────┬────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Sort events by date               │
│  • Known dates → chronological     │
│  • Unknown dates → separate        │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Generate narrative:               │
│  "TIMELINE STORY - Case: XXX"      │
│  ==============================     │
│  Analyzed N documents:             │
│  • doc1.pdf (invoice)             │
│  • doc2.docx (contract)           │
│                                     │
│  CHRONOLOGICAL TIMELINE:           │
│  📅 2024-01-15                     │
│     Invoice issued                 │
│     Source: doc1.pdf              │
│                                     │
│  DOCUMENT SUMMARIES:               │
│  doc1.pdf: Invoice for...         │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Save to MongoDB: cases            │
│  collection (timeline_story field) │
│  Update last_scan_at timestamp     │
└─────────────────────────────────────┘
```

### 6. Status & Results Retrieval Flow

```
Get Scan Status
       │
       ▼
┌─────────────────────────────────────┐
│  GET /api/cases/{case_id}/         │
│  scan/status                       │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  ScanService.get_scan_status()     │
│  • Count documents by status:      │
│    - pending                       │
│    - processing                    │
│    - completed                     │
│    - failed                        │
│  • Query MongoDB: analysis_results │
│  • Return timeline_story           │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Return:                           │
│  {                                 │
│    status: "in_progress" |         │
│             "completed",            │
│    total_documents: 5,             │
│    processed_documents: 3,         │
│    results: [...],                 │
│    timeline_story: "..."           │
│  }                                 │
└─────────────────────────────────────┘
```

---

## Data Models

### AgentState (Passed Between Agents)

```python
class AgentState(TypedDict):
    document_id: str           # UUID
    case_id: str              # UUID
    user_id: str              # UUID
    file_path: str            # Local path to file
    file_type: str            # pdf|docx|image
    extracted_text: str       # Raw text from extraction
    tables: list[dict]        # Extracted tables
    document_type: str        # invoice|contract|letter|chat|...
    classification_confidence: float  # 0.0-1.0
    analysis_results: dict    # Type-specific analysis
    summary: str              # 2-3 sentence summary
    timeline_events: list     # Extracted events with dates
    errors: list[str]         # Accumulated errors
    current_agent: str        # Current agent name
```

### Document Status Lifecycle

```
pending → processing → completed
              ↓
            failed
```

---

## WebSocket Events

| Event | Description |
|-------|-------------|
| `document_processed` | Single document analysis complete |
| `scan_complete` | All documents in case processed |
| `keepalive` | Connection keepalive ping |

---

## Error Handling

1. **Extraction Errors**: Logged to `errors` list, document marked as `failed`
2. **Classification Errors**: Default to `generic` type, confidence 0.0
3. **Analysis Errors**: Logged, continue with empty results
4. **Synthesis Errors**: Default summary "Error generating summary"

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama API endpoint |
| `OLLAMA_MODEL` | llama3.2 | LLM model to use |
| `MONGODB_URI` | mongodb://localhost:27017 | MongoDB connection |
| `MONGODB_DB` | chronicles | Database name |
| `OCR_METHOD` | tesseract | OCR backend: tesseract/cloud/vision |
| `FILE_RETENTION_HOURS` | 24 | Auto-delete uploaded files after N hours |

---

## File Storage Structure

```
backend/
├── documents/
│   ├── {case_id}/
│   │   ├── {document_id}.pdf
│   │   ├── {document_id}.docx
│   │   └── {document_id}.png
```

---

## API Quick Reference

### Cases
- `POST /api/cases` - Create case
- `GET /api/cases` - List cases
- `GET /api/cases/{case_id}` - Get case details
- `DELETE /api/cases/{case_id}` - Delete case

### Documents
- `POST /api/cases/{case_id}/documents` - Upload documents
- `GET /api/cases/{case_id}/documents` - List documents
- `GET /api/cases/{case_id}/documents/{document_id}/view` - View/download
- `DELETE /api/cases/{case_id}/documents/{document_id}` - Delete

### Analysis
- `POST /api/cases/{case_id}/scan` - Start analysis
- `GET /api/cases/{case_id}/scan/status` - Get status/results

### WebSocket
- `WS /ws/{client_id}` - Real-time updates
