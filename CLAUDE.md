# Chronicles of Documents - Multi-Agentic AI Document Analyzer

## Project Overview

A comprehensive case management and document analysis system that processes various document formats (PDF, DOCX, DOC, images from WhatsApp/Facebook chats) using a multi-agentic AI architecture. Documents are organized by cases, with each case belonging to a system user.

**Tech Stack:**
- **Backend:** Python 3.12+, FastAPI, LangGraph, Ollama (local LLM)
- **Frontend:** Next.js 15+, TypeScript, shadcn/ui, Tailwind CSS
- **Infrastructure:** MongoDB (metadata + GridFS), ChromaDB (vector store)

## Architecture

### Multi-Agent System

The system uses 4 specialized AI agents orchestrated via LangGraph:

1. **Extractor Agent** - Extracts text, tables, and metadata from documents (includes OCR for images)
2. **Classifier Agent** - Classifies document category (invoice, contract, letter, chat, etc.) and routes to appropriate analyzer
3. **Analyzer Agent** - Performs deep analysis based on document type (specialized logic per type)
4. **Synthesizer Agent** - Generates summary and actionable recommendations

### Agent Workflow

```
Start → Extractor (text/tables/OCR) → Classifier (document type)
                                            ↓
                                    [Route by Type]
                                            ↓
        ┌───────────────────────────────────┼───────────────────────────────┐
        ↓                                   ↓                               ↓
    Invoice Analyzer              Contract Analyzer              Chat/Generic Analyzer
        ↓                                   ↓                               ↓
        └───────────────────────────────────┼───────────────────────────────┘
                                            ↓
                                    Synthesizer (summary + recommendations)
                                            ↓
                                          End
```

## Project Structure

```
chroniclesOfDocuments/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/routes/         # API endpoints
│   │   ├── agents/             # LangGraph agent definitions
│   │   ├── core/               # Config, Ollama client, parsers
│   │   ├── models/             # Pydantic models
│   │   ├── services/           # MongoDB, GridFS, vector store
│   │   └── utils/              # PII detection, encryption
│   └── pyproject.toml
├── frontend/                   # Next.js frontend
│   ├── app/                    # Next.js App Router pages
│   ├── components/             # React components
│   └── package.json
└── CLAUDE.md                   # This file
```

## Database Architecture

### MongoDB Collections

**1. users** - System users (minimal data)
```json
{
  "_id": "ObjectId",
  "user_id": "uuid",
  "username": "user@example.com",
  "role": "lawyer|admin|clerk",
  "created_at": "ISODate",
  "last_login": "ISODate"
}
```

**2. cases** - Case information
```json
{
  "_id": "ObjectId",
  "case_id": "uuid",
  "case_number": "CASE-2024-001",
  "user_id": "uuid",  // Owner of the case
  "title": "Contract Dispute - ABC Corp",
  "status": "open|closed|archived",
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "metadata": {
    "case_type": "civil|criminal|corporate",
    "priority": "high|medium|low"
  }
}
```

**3. documents** - Document metadata (NO PII)
```json
{
  "_id": "ObjectId",
  "document_id": "uuid",
  "case_id": "uuid",  // Links to case
  "user_id": "uuid",  // User who uploaded
  "file_hash": "sha256",
  "uploaded_at": "ISODate",
  "file_type": "pdf|docx|image",
  "file_size": 1024000,
  "category": "invoice|contract|chat|letter|generic",
  "status": "pending|processing|completed|failed",
  "processing_time_ms": 2500,
  "expires_at": "ISODate"  // TTL index for auto-deletion
}
```

**4. analysis_results** - Extracted insights (NO PII)
```json
{
  "_id": "ObjectId",
  "document_id": "uuid",
  "case_id": "uuid",
  "category": "invoice",
  "confidence": 0.95,
  "extracted_data": {
    "total_amount": 1500.00,
    "currency": "USD",
    "date": "2024-01-15",
    "line_items_count": 5,
    "payment_terms": "Net 30"
  },
  "summary": "Invoice for professional services...",
  "recommendations": ["Verify payment terms", "Check tax calculations"],
  "created_at": "ISODate",
  "expires_at": "ISODate"  // TTL index
}
```

**5. GridFS** - Temporary encrypted file storage
- Files stored encrypted with AES-256
- Automatic deletion after processing (configurable: 1h - 30 days)
- Used only during processing pipeline
- Chunked storage for large files (>16MB)

### Data Relationships

```
User (1) ──→ (N) Cases
Case (1) ──→ (N) Documents
Document (1) ──→ (1) Analysis Result
```

### Indexes for Performance

```python
# Users
db.users.create_index("user_id", unique=True)
db.users.create_index("username", unique=True)

# Cases
db.cases.create_index("case_id", unique=True)
db.cases.create_index("case_number", unique=True)
db.cases.create_index("user_id")  # Query cases by user
db.cases.create_index([("user_id", 1), ("status", 1)])  # Compound index

# Documents
db.documents.create_index("document_id", unique=True)
db.documents.create_index("case_id")  # Query documents by case
db.documents.create_index("user_id")  # Query documents by user
db.documents.create_index("expires_at", expireAfterSeconds=0)  # TTL

# Analysis Results
db.analysis_results.create_index("document_id", unique=True)
db.analysis_results.create_index("case_id")  # Query analysis by case
db.analysis_results.create_index("expires_at", expireAfterSeconds=0)  # TTL
```

### ChromaDB Collections

**document_embeddings** - Semantic search (anonymized)
- Sanitized text chunks (PII removed/redacted)
- Metadata: `{document_id, case_id, user_id}` for access control
- Used for similarity search within user's cases

### Privacy & Compliance

**PII Protection Strategy:**
1. **Upload Phase:** File encrypted and stored in GridFS temporarily
2. **Processing Phase:** Extract insights in-memory, detect and flag PII
3. **Storage Phase:** Store only anonymized metadata and structured insights
4. **Cleanup Phase:** Auto-delete original files via TTL indexes (default: 24 hours)

**Access Control:**
- Users can only access their own cases and documents
- Admin role can access all cases
- Case-based document isolation

**Data Retention:**
- Uploaded files: 24 hours (configurable)
- Analysis results: 30 days (configurable)
- Cases: Retained until manually archived/deleted
- No raw text with PII persisted
- User can request immediate deletion

**TTL Index Configuration:**
```python
# Auto-delete documents after 24 hours
db.documents.create_index("expires_at", expireAfterSeconds=0)
db.analysis_results.create_index("expires_at", expireAfterSeconds=0)
```

## Supported Document Types

| Type | Extensions | Processing |
|------|------------|-------------|
| PDF | .pdf | pypdf + pdfplumber for tables |
| Word | .docx, .doc | python-docx |
| Images | .png, .jpg, .jpeg | OCR via pytesseract |
| Chat Exports | Various | Image OCR + format detection |

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/logout` | User logout |
| GET | `/api/auth/me` | Get current user |

### Cases
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/cases` | Create new case |
| GET | `/api/cases` | List user's cases |
| GET | `/api/cases/{case_id}` | Get case details |
| PUT | `/api/cases/{case_id}` | Update case |
| DELETE | `/api/cases/{case_id}` | Delete case |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/cases/{case_id}/documents/upload` | Upload document to case |
| GET | `/api/cases/{case_id}/documents` | List case documents |
| GET | `/api/documents/{document_id}` | Get document metadata |
| DELETE | `/api/documents/{document_id}` | Delete document |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analysis/start/{document_id}` | Start document analysis |
| GET | `/api/analysis/status/{document_id}` | Get analysis status |
| GET | `/api/analysis/results/{document_id}` | Get analysis results |
| GET | `/api/cases/{case_id}/analysis` | Get all analysis for case |

## Development Commands

### Backend
```bash
cd backend
uv sync                           # Install dependencies
uv run fastapi dev app/main.py    # Run development server
uv run pytest                     # Run tests

# MongoDB setup (Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Frontend
```bash
cd frontend
npm install                       # Install dependencies
npm run dev                       # Run development server
```

## Environment Variables

### Backend (.env)
```
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=chronicles
MONGODB_MAX_POOL_SIZE=10

# File Storage
FILE_RETENTION_HOURS=24
MAX_FILE_SIZE_MB=50
ENCRYPTION_KEY=your-secret-key-here

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_data
```

## Agent State Schema

```python
class AgentState(TypedDict):
    document_id: str
    case_id: str
    user_id: str
    file_path: str
    file_type: str
    extracted_text: str
    tables: list[dict]
    document_type: str | None
    classification_confidence: float | None
    analysis_results: dict
    summary: str
    errors: list[str]
    current_agent: str
```

## Guidelines for Claude Code

- **Document parsing:** Use pdfplumber for PDFs with tables, pypdf for simple text extraction
- **OCR:** pytesseract requires tesseract-ocr to be installed on the system
- **LLM calls:** Use streaming for better UX in frontend progress updates
- **Error handling:** Agents should accumulate errors in `errors` list, not fail immediately
- **File storage:** Files stored encrypted in MongoDB GridFS with TTL-based auto-deletion
- **PII Protection:** Implement PII detection before storing any text; store only anonymized insights
- **MongoDB:** Use motor (async MongoDB driver) for FastAPI compatibility
- **Encryption:** Use cryptography library (Fernet) for file encryption before GridFS storage
- **TTL Cleanup:** Set `expires_at` field on all documents for automatic deletion