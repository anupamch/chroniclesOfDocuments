# System Architecture

## Docker Compose Stack

### Development Environment
```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   MongoDB    │  │  ChromaDB    │  │   Backend    │ │
│  │   :27017     │  │   :8001      │  │   :8000      │ │
│  │              │  │              │  │              │ │
│  │  Metadata    │  │  Vectors     │  │  Vision OCR  │ │
│  │  Storage     │  │  Storage     │  │  + Agents    │ │
│  └──────────────┘  └──────────────┘  └──────┬───────┘ │
│                                              │          │
└──────────────────────────────────────────────┼──────────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │  Ollama (on host)   │
                                    │  llama3.2-vision    │
                                    │  :11434             │
                                    └─────────────────────┘
```

### Production Environment
```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   MongoDB    │  │  ChromaDB    │  │   Backend    │ │
│  │   :27017     │  │   :8001      │  │   :8000      │ │
│  │              │  │              │  │              │ │
│  │  Metadata    │  │  Vectors     │  │  Tesseract   │ │
│  │  + GridFS    │  │  + Search    │  │  OCR         │ │
│  │              │  │              │  │  + Agents    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  Persistent Volumes:                                     │
│  • mongodb_data (document metadata)                      │
│  • chromadb_data (vector embeddings)                     │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

### Document Processing Pipeline

```
1. Upload
   ↓
┌──────────────────────────────────────────┐
│  documents/ folder                        │
│  • invoice.pdf                           │
│  • contract.docx                         │
│  • scanned_doc.jpg                       │
└──────────────┬───────────────────────────┘
               ↓
2. Extraction Agent
   ↓
┌──────────────────────────────────────────┐
│  Extract text, tables, metadata          │
│  • PDF → pypdf + pdfplumber              │
│  • DOCX → python-docx                    │
│  • Images → Tesseract/Vision OCR         │
└──────────────┬───────────────────────────┘
               ↓
3. Classifier Agent
   ↓
┌──────────────────────────────────────────┐
│  Classify document type                  │
│  • Invoice, Contract, Letter, etc.       │
│  • Uses Ollama LLM                       │
└──────────────┬───────────────────────────┘
               ↓
4. Analyzer Agent
   ↓
┌──────────────────────────────────────────┐
│  Type-specific analysis                  │
│  • Extract key fields                    │
│  • Identify important data               │
│  • Uses Ollama LLM                       │
└──────────────┬───────────────────────────┘
               ↓
5. Synthesizer Agent
   ↓
┌──────────────────────────────────────────┐
│  Generate summary & timeline             │
│  • Create document summary               │
│  • Extract timeline events               │
│  • Uses Ollama LLM                       │
└──────────────┬───────────────────────────┘
               ↓
6. Storage
   ↓
┌──────────────┬───────────────────────────┐
│              │                            │
│   MongoDB    │      ChromaDB             │
│   • Metadata │      • Embeddings         │
│   • Analysis │      • Semantic search    │
│              │                            │
└──────────────┴───────────────────────────┘
               ↓
7. Output
   ↓
┌──────────────────────────────────────────┐
│  output/ folder                          │
│  • analysis_TIMESTAMP.json               │
│  • timeline_story_TIMESTAMP.txt          │
└──────────────────────────────────────────┘
```

## Agent Workflow (LangGraph)

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                    │
│                                                          │
│  START                                                   │
│    ↓                                                     │
│  ┌──────────────────┐                                   │
│  │ Extractor Agent  │  Extract text, tables, metadata   │
│  └────────┬─────────┘                                   │
│           ↓                                              │
│  ┌──────────────────┐                                   │
│  │ Classifier Agent │  Determine document type          │
│  └────────┬─────────┘                                   │
│           ↓                                              │
│  ┌──────────────────┐                                   │
│  │  Analyzer Agent  │  Type-specific analysis           │
│  └────────┬─────────┘                                   │
│           ↓                                              │
│  ┌──────────────────┐                                   │
│  │Synthesizer Agent │  Summary + timeline events        │
│  └────────┬─────────┘                                   │
│           ↓                                              │
│  END                                                     │
└─────────────────────────────────────────────────────────┘
```

## MongoDB Collections

### documents
```json
{
  "_id": "ObjectId",
  "document_id": "uuid",
  "case_id": "uuid",
  "user_id": "uuid",
  "file_hash": "sha256",
  "file_type": "pdf",
  "category": "invoice",
  "status": "completed",
  "uploaded_at": "ISODate",
  "expires_at": "ISODate"
}
```

### analysis_results
```json
{
  "_id": "ObjectId",
  "document_id": "uuid",
  "case_id": "uuid",
  "category": "invoice",
  "confidence": 0.95,
  "extracted_data": {
    "total_amount": 1500.00,
    "date": "2024-01-15"
  },
  "summary": "Invoice for services...",
  "timeline_events": [
    {"date": "2024-01-15", "event": "Invoice issued"}
  ],
  "created_at": "ISODate"
}
```

## ChromaDB Collections

### document_embeddings
- Stores vector embeddings of document text
- Metadata: `{document_id, case_id, user_id}`
- Used for semantic search and similarity

## Scaling Strategy

### Phase 1: Single Server (Current)
```
1 Backend Container + MongoDB + ChromaDB
Handles: ~100 documents/hour
```

### Phase 2: Horizontal Scaling
```
Load Balancer
    ↓
┌───┴───┬───────┬───────┐
│       │       │       │
Backend Backend Backend Backend
  #1      #2      #3      #4
    ↓       ↓       ↓       ↓
    └───────┴───┬───┴───────┘
                ↓
        MongoDB Cluster
```

### Phase 3: Kubernetes
```
Ingress Controller
    ↓
Service (Load Balancer)
    ↓
Deployment (10+ Pods)
    ↓
StatefulSet (MongoDB)
    ↓
PersistentVolumes
```

## Security Layers

1. **Network Isolation**: Docker network isolation
2. **Data Encryption**: MongoDB encryption at rest
3. **TTL Cleanup**: Auto-delete after retention period
4. **No PII Storage**: Only anonymized metadata
5. **Access Control**: MongoDB authentication (production)

## Performance Optimization

### Current Setup
- Sequential document processing
- Single worker per container
- In-memory processing

### Optimized Setup
- Parallel processing with worker pool
- Multiple backend containers
- Redis queue for job distribution
- Caching layer for repeated documents

## Monitoring Points

1. **Backend Container**
   - Processing time per document
   - OCR success rate
   - Memory usage
   - CPU usage

2. **MongoDB**
   - Query performance
   - Storage usage
   - Connection pool

3. **ChromaDB**
   - Vector search latency
   - Index size
   - Query throughput

## Backup Strategy

### Development
- Docker volumes (local)
- No backup needed

### Production
- MongoDB: Daily backups to S3
- ChromaDB: Weekly snapshots
- Retention: 30 days
