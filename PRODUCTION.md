# Production Deployment Guide

## OCR Backend Comparison

| Backend | Speed | Accuracy | Cost | Scalability | Best For |
|---------|-------|----------|------|-------------|----------|
| **Tesseract** | ⚡⚡⚡ Fast | ✅ Good | 💰 Free | ⭐⭐⭐ Excellent | Production (self-hosted) |
| **Cloud OCR** | ⚡⚡ Medium | ✅✅ Excellent | 💰💰💰 Pay-per-use | ⭐⭐⭐ Excellent | Production (managed) |
| **Vision Model** | ⚡ Slow | ⚠️ Variable | 💰💰 GPU costs | ⭐ Limited | Development only |

## Production Recommendations

### Small-Medium Scale (< 1000 docs/day)

**Use Tesseract OCR:**
```bash
# Install on Ubuntu server
apt-get install tesseract-ocr poppler-utils

# Set in .env
OCR_METHOD=tesseract
```

**Pros:**
- Free and open source
- Fast (can process 100+ pages/minute)
- Reliable and battle-tested
- Easy to containerize (Docker)
- Can run parallel workers

**Deployment:**
```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Large Scale (> 1000 docs/day)

**Use Cloud OCR Services:**

**Option 1: AWS Textract**
- Best accuracy
- Handles complex layouts
- $1.50 per 1000 pages
- Auto-scaling

**Option 2: Google Cloud Vision**
- Good accuracy
- $1.50 per 1000 pages
- Easy integration

**Option 3: Azure Computer Vision**
- Good accuracy
- $1.00 per 1000 pages
- Enterprise features

```python
# Set in .env
OCR_METHOD=cloud
USE_CLOUD_OCR=true
AWS_REGION=us-east-1
```

### Architecture for Production

```
                    ┌─────────────┐
                    │   Load      │
                    │  Balancer   │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
       ┌────▼────┐    ┌────▼────┐   ┌────▼────┐
       │ Worker  │    │ Worker  │   │ Worker  │
       │   #1    │    │   #2    │   │   #3    │
       └────┬────┘    └────┬────┘   └────┬────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
                    ┌──────▼──────┐
                    │   MongoDB   │
                    │   Cluster   │
                    └─────────────┘
```

## Performance Benchmarks

### Tesseract (Production Server)
- Text PDF: 0.5s per page
- Scanned PDF: 2-3s per page
- Image: 1-2s per image
- Parallel: 10 workers = 10x throughput

### Cloud OCR (AWS Textract)
- Any document: 1-2s per page
- Batch processing: 1000 pages in 5 minutes
- Auto-scaling: handles spikes

### Vision Model (llama3.2-vision)
- Scanned PDF: 5-10s per page
- Image: 3-5s per image
- Sequential only
- ❌ Not recommended for production

## Cost Analysis (1 million pages/month)

| Backend | Cost | Infrastructure | Total |
|---------|------|----------------|-------|
| Tesseract | $0 | $500/month (servers) | $500/month |
| AWS Textract | $1,500 | $100/month (API) | $1,600/month |
| Vision Model | $0 | $2,000/month (GPU servers) | $2,000/month |

## Recommendation

**For Production:**
1. **Start with Tesseract** - Free, fast, reliable
2. **Scale with Cloud OCR** - When accuracy matters more than cost
3. **Never use Vision Models** - Only for development/testing

**Hybrid Approach (Best):**
- Use Tesseract for 90% of documents
- Use Cloud OCR for complex/critical documents
- Vision models only for development

## Implementation

Update `backend/app/agents/extractor.py`:

```python
from app.core.config import settings

# Production parser
if settings.use_cloud_ocr:
    from app.core.parsers_production import ProductionDocumentParser as DocumentParser
    DocumentParser.OCR_BACKEND = "cloud"
elif settings.ocr_method == "tesseract":
    from app.core.parsers_production import ProductionDocumentParser as DocumentParser
    DocumentParser.OCR_BACKEND = "tesseract"
else:
    # Development only
    from app.core.parsers_vision import VisionDocumentParser as DocumentParser
```

## Monitoring

**Key Metrics:**
- Processing time per document
- OCR accuracy rate
- Error rate
- Queue depth
- Cost per document

**Tools:**
- Prometheus + Grafana
- CloudWatch (AWS)
- Application Insights (Azure)

## Security

**For Production:**
- Encrypt files at rest (MongoDB GridFS encryption)
- TLS for all API calls
- Auto-delete after processing (TTL indexes)
- No PII in logs
- Audit trail for all operations
- Role-based access control (RBAC)
