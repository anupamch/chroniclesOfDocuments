# Docker Deployment Guide

## Why Docker for Production?

✅ **Solves the Tesseract Problem:**
- No manual OS-level installation needed
- Tesseract pre-installed in container
- Same environment everywhere (dev, staging, prod)

✅ **Easy Deployment:**
- One command to start everything
- Includes MongoDB, ChromaDB, Backend
- Automatic dependency management

✅ **Scalability:**
- Easy to run multiple workers
- Load balancing with Docker Swarm/Kubernetes
- Horizontal scaling

## Quick Start

### Development (with Ollama on host)

```bash
# Start Ollama on your host machine first
ollama pull llama3.2
ollama pull llama3.2-vision

# Run development container
docker-compose -f docker-compose.dev.yml up

# Place documents in backend/documents/
# Check results in backend/output/
```

### Production (with Tesseract OCR)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Place documents in backend/documents/
# Check results in backend/output/

# Stop services
docker-compose down
```

## Architecture

```
┌─────────────────────────────────────────┐
│           Docker Host                    │
│                                          │
│  ┌──────────────┐  ┌─────────────┐     │
│  │   MongoDB    │  │  ChromaDB   │     │
│  │   :27017     │  │   :8001     │     │
│  └──────────────┘  └─────────────┘     │
│                                          │
│  ┌──────────────────────────────────┐  │
│  │   Backend (Tesseract + Python)   │  │
│  │   - Document Processing          │  │
│  │   - Agent Workflow               │  │
│  │   - OCR (Tesseract built-in)     │  │
│  │   :8000                          │  │
│  └──────────────────────────────────┘  │
│           ↓                              │
│  ┌──────────────────────────────────┐  │
│  │   Ollama (on host)               │  │
│  │   :11434                         │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Container Details

### Backend Container
- **Base:** Python 3.12 slim
- **Includes:** Tesseract OCR, Poppler, system libs
- **Size:** ~500MB
- **OCR:** Tesseract (production) or Ollama vision (dev)

### MongoDB Container
- **Purpose:** Document metadata, analysis results
- **Persistent:** Volume mounted
- **Port:** 27017

### ChromaDB Container
- **Purpose:** Vector embeddings for semantic search
- **Persistent:** Volume mounted
- **Port:** 8001

## Scaling for Production

### Single Server (Small Scale)

```bash
# Run 3 backend workers
docker-compose up -d --scale backend=3

# Add nginx load balancer
docker-compose -f docker-compose.yml -f docker-compose.lb.yml up -d
```

### Multi-Server (Large Scale)

Use Docker Swarm or Kubernetes:

```bash
# Docker Swarm
docker swarm init
docker stack deploy -c docker-compose.yml chronicles

# Scale workers
docker service scale chronicles_backend=10
```

### Kubernetes (Enterprise)

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chronicles-backend
spec:
  replicas: 10
  selector:
    matchLabels:
      app: chronicles-backend
  template:
    metadata:
      labels:
        app: chronicles-backend
    spec:
      containers:
      - name: backend
        image: chronicles-backend:latest
        env:
        - name: OCR_METHOD
          value: "tesseract"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

## Performance Benchmarks

### Docker vs Native

| Setup | Speed | Overhead |
|-------|-------|----------|
| Native (no Docker) | 100% | 0% |
| Docker (Tesseract) | 95-98% | 2-5% |
| Docker (Vision) | 90-95% | 5-10% |

Docker overhead is minimal for production workloads.

## Resource Requirements

### Development
- **CPU:** 2 cores
- **RAM:** 4GB
- **Disk:** 10GB

### Production (per worker)
- **CPU:** 2-4 cores
- **RAM:** 4-8GB
- **Disk:** 20GB

### Production (10 workers)
- **CPU:** 20-40 cores
- **RAM:** 40-80GB
- **Disk:** 100GB

## Environment Variables

```bash
# Backend Container
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2
OCR_METHOD=tesseract  # or "vision" or "cloud"
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DB=chronicles

# For Cloud OCR
USE_CLOUD_OCR=true
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

## Monitoring

### Health Checks

```yaml
# Add to docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Logs

```bash
# View logs
docker-compose logs -f backend

# Export logs
docker-compose logs backend > backend.log

# Log rotation (production)
docker-compose logs --tail=1000 backend
```

### Metrics

```bash
# Container stats
docker stats

# Detailed metrics
docker-compose exec backend python -m cProfile app/main.py
```

## Troubleshooting

### Tesseract not found
```bash
# Check if Tesseract is installed in container
docker-compose exec backend tesseract --version

# Rebuild container
docker-compose build --no-cache backend
```

### Ollama connection failed
```bash
# Check if Ollama is running on host
curl http://localhost:11434/api/tags

# Check Docker network
docker-compose exec backend ping host.docker.internal
```

### Out of memory
```bash
# Increase container memory limit
docker-compose up -d --memory=8g backend

# Or in docker-compose.yml:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 8G
```

## Production Checklist

- [ ] Use Tesseract OCR (not vision models)
- [ ] Set up MongoDB with authentication
- [ ] Enable SSL/TLS for all connections
- [ ] Configure log rotation
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure auto-restart policies
- [ ] Set resource limits
- [ ] Use secrets management (not .env files)
- [ ] Set up backup for MongoDB volumes
- [ ] Configure health checks
- [ ] Use reverse proxy (nginx/traefik)
- [ ] Enable rate limiting

## Cost Comparison

### Self-Hosted (Docker + Tesseract)
- **Server:** $100-500/month (depending on scale)
- **OCR:** Free (Tesseract)
- **Total:** $100-500/month

### Cloud OCR (Docker + AWS Textract)
- **Server:** $50-200/month (smaller instances)
- **OCR:** $1.50 per 1000 pages
- **Total:** Variable based on usage

### Serverless (AWS Lambda + Textract)
- **Compute:** Pay per invocation
- **OCR:** $1.50 per 1000 pages
- **Total:** Most cost-effective for sporadic usage

## Recommendation

**For Production:**
1. Use Docker with Tesseract OCR
2. Start with single server (docker-compose)
3. Scale to Docker Swarm when needed
4. Move to Kubernetes for enterprise scale

Docker solves the Tesseract installation problem and makes your app production-ready!
