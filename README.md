# Chronicles of Documents

A comprehensive **multi-agentic AI document analyzer** for intelligent case management and document processing. Built with modern AI, this system extracts insights from various document formats using specialized agents orchestrated with LangGraph.

## Features

✨ **Multi-Agent Architecture**
- **Extractor Agent**: Extracts text, tables, and metadata from documents with OCR support
- **Classifier Agent**: Categorizes documents (invoice, contract, letter, chat, etc.)
- **Analyzer Agent**: Performs deep analysis specific to document type
- **Synthesizer Agent**: Generates summaries and actionable recommendations

📄 **Supported Document Types**
- PDF documents with table extraction
- Word documents (.docx, .doc)
- Images with OCR (PNG, JPG, JPEG)
- Chat exports (WhatsApp, Facebook)

🔒 **Privacy & Compliance**
- Automatic PII detection and anonymization
- Encrypted file storage with TTL-based cleanup
- Access control by user and case
- GDPR-compliant data retention

⚖️ **Legal-Focused Features**
- Case management with document organization
- Contract analysis and risk assessment
- Invoice extraction and validation
- Chat analysis for context extraction

## Tech Stack

### Backend
- **Runtime**: Python 3.12+
- **Framework**: FastAPI
- **AI Orchestration**: LangGraph
- **Local LLM**: Ollama (llama3.2)
- **Database**: MongoDB with GridFS
- **Vector Store**: ChromaDB
- **Document Parsing**: pypdf, pdfplumber, pytesseract, python-docx

### Frontend
- **Framework**: Next.js 15+
- **Language**: TypeScript
- **UI**: shadcn/ui + Tailwind CSS
- **State**: React Context API

### Mobile
- **Framework**: React Native (Expo)
- **Language**: TypeScript
- **UI**: Custom components with Tailwind

## Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Ollama (for local LLM)
- MongoDB (or use Docker container)
- tesseract-ocr (for image processing)

## Quick Start

### Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Create .env file
# (Copy and update environment variables from CLAUDE.md)

# Start MongoDB (Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Download Ollama model
ollama pull llama3.2

# Run development server
uv run fastapi dev app/main.py
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs on `http://localhost:3000`

### Mobile Setup

```bash
cd mobile

# Install dependencies
npm install

# Start Expo development server
npx expo start
```

### Docker Compose (Full Stack)

```bash
# Development environment
docker-compose -f docker-compose.dev.yml up

# Simple setup
docker-compose -f docker-compose.simple.yml up
```

## Project Structure

```
chroniclesOfDocuments/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # REST API routes
│   │   ├── agents/            # LangGraph agents
│   │   ├── core/              # Config, Ollama client
│   │   ├── services/          # MongoDB, ChromaDB
│   │   ├── models/            # Pydantic models
│   │   └── schemas/           # API schemas
│   └── pyproject.toml
│
├── frontend/                   # Next.js web frontend
│   ├── app/                   # Next.js App Router
│   ├── components/            # React components
│   └── package.json
│
├── mobile/                     # React Native mobile app
│   ├── app/                   # Expo App Router
│   ├── components/            # React Native components
│   └── package.json
│
└── CLAUDE.md                  # Detailed architecture docs
```

## Database Architecture

### Collections

**users** - System users (minimal data)
- user_id, username, role, created_at

**cases** - Case information
- case_id, case_number, title, status, user_id

**documents** - Document metadata (NO PII)
- document_id, case_id, file_hash, category, status, expires_at

**analysis_results** - Extracted insights (NO PII)
- document_id, extracted_data, summary, recommendations, expires_at

**GridFS** - Encrypted temporary file storage
- Auto-cleanup via TTL indexes (default: 24 hours)

### ChromaDB Collections

**document_embeddings** - Semantic search with anonymized text

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Cases
- `POST /api/cases` - Create new case
- `GET /api/cases` - List user's cases
- `GET /api/cases/{case_id}` - Get case details
- `PUT /api/cases/{case_id}` - Update case
- `DELETE /api/cases/{case_id}` - Delete case

### Documents
- `POST /api/cases/{case_id}/documents/upload` - Upload document
- `GET /api/cases/{case_id}/documents` - List case documents
- `GET /api/documents/{document_id}` - Get document metadata
- `DELETE /api/documents/{document_id}` - Delete document

### Analysis
- `POST /api/analysis/start/{document_id}` - Start analysis
- `GET /api/analysis/status/{document_id}` - Get analysis status
- `GET /api/analysis/results/{document_id}` - Get results
- `GET /api/cases/{case_id}/analysis` - Get all case analysis

For detailed API documentation, see [API.md](API.md)

## Development

### Run Tests

```bash
# Backend
cd backend
uv run pytest

# Frontend
cd frontend
npm test

# Mobile
cd mobile
npm test
```

### Build for Production

```bash
# Backend
docker build -f backend/Dockerfile -t chronicles-backend .

# Frontend
cd frontend
npm run build

# Mobile
cd mobile
eas build
```

## Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# MongoDB
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

## Data Privacy

This system implements strict privacy controls:

1. **Encryption**: Files encrypted with AES-256 before storage
2. **PII Detection**: Automatic detection and anonymization
3. **TTL Cleanup**: Documents auto-deleted after configured retention period
4. **Access Control**: Users only access their own cases
5. **No Raw Storage**: Only anonymized insights persisted

For detailed privacy information, see [CLAUDE.md](CLAUDE.md)

## Documentation

- [CLAUDE.md](CLAUDE.md) - Complete architecture & design
- [API.md](API.md) - API reference
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [DOCKER.md](DOCKER.md) - Docker setup guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues

## Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# Restart MongoDB
docker restart mongodb
```

### Ollama Model Issues
```bash
# List available models
ollama list

# Pull the required model
ollama pull llama3.2

# Check Ollama service
curl http://localhost:11434/api/tags
```

### Frontend Build Issues
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more detailed solutions.

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

## License

This project is proprietary and confidential.

## Support

For issues and questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [CLAUDE.md](CLAUDE.md) architecture docs
3. Check existing issues/discussions

---

**Chronicles of Documents** - Intelligent document analysis for legal case management.
