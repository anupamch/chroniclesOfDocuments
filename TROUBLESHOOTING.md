# Docker Build Troubleshooting

## Error: apt-get exit code 100

This error usually happens on Windows Docker Desktop due to network/DNS issues.

### Solution 1: Use Pre-built Image (Recommended)

Instead of building locally, use a pre-built base image with Tesseract:

```dockerfile
# Use this in backend/Dockerfile
FROM jitesoft/tesseract-ocr:5

# Install Python
RUN apt-get update && apt-get install -y python3.12 python3-pip

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY app ./app
RUN mkdir -p documents output

ENV OCR_METHOD=tesseract
CMD ["python3", "app/main.py"]
```

### Solution 2: Fix Docker DNS

1. Open Docker Desktop Settings
2. Go to Docker Engine
3. Add DNS servers:

```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

4. Click "Apply & Restart"
5. Try building again

### Solution 3: Use WSL2 Backend

1. Open Docker Desktop Settings
2. Go to General
3. Enable "Use the WSL 2 based engine"
4. Restart Docker Desktop
5. Try building again

### Solution 4: Build with --network=host

```bash
docker build --network=host -t chronicles-backend ./backend
```

### Solution 5: Use Cached Layers

Pull a base image first:

```bash
docker pull python:3.12-slim
docker build -t chronicles-backend ./backend
```

### Solution 6: Manual Build Steps

Build step by step to identify the failing package:

```bash
# Test base image
docker run -it python:3.12-slim bash

# Inside container, test each package
apt-get update
apt-get install -y tesseract-ocr
apt-get install -y tesseract-ocr-eng
apt-get install -y poppler-utils
```

### Solution 7: Use Alternative Dockerfile

For development on Windows, use vision models:

```bash
# Use simple dockerfile without Tesseract
docker-compose -f docker-compose.simple.yml up
```

For production on Linux server, Tesseract will work fine.

### Solution 8: Check Internet Connection

```bash
# Test if Docker can reach internet
docker run --rm python:3.12-slim apt-get update

# If this fails, check:
# - Firewall settings
# - VPN connection
# - Corporate proxy
```

### Solution 9: Use Different Mirror

Add to Dockerfile before apt-get:

```dockerfile
RUN echo "deb http://deb.debian.org/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list
```

### Solution 10: Build on Linux Server

If all else fails:
1. Use vision models on Windows for development
2. Deploy to Linux server for production with Tesseract
3. Linux servers don't have these Docker DNS issues

## Recommended Approach

**For Development (Windows):**
```bash
# Use vision models (no Tesseract needed)
docker-compose -f docker-compose.simple.yml up
```

**For Production (Linux Server):**
```bash
# Use Tesseract (works perfectly on Linux)
docker-compose up -d
```

## Alternative: Native Installation

If Docker continues to fail, install natively:

```bash
# Install Tesseract on Windows
choco install tesseract

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run directly
python app/main.py
```
