# Production Dockerfile with Tesseract OCR
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Try to fix DNS and update issues on Windows Docker
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# Clean and update package lists
RUN rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    apt-get update

# Install Tesseract and dependencies one by one for better error tracking
RUN apt-get install -y --no-install-recommends tesseract-ocr || \
    (apt-get update && apt-get install -y --no-install-recommends tesseract-ocr)

RUN apt-get install -y --no-install-recommends tesseract-ocr-eng

RUN apt-get install -y --no-install-recommends tesseract-ocr-ben

RUN apt-get install -y --no-install-recommends poppler-utils

RUN apt-get install -y --no-install-recommends libgl1

RUN apt-get install -y --no-install-recommends libglib2.0-0

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app ./app

# Create directories
RUN mkdir -p documents output

ENV OCR_METHOD=tesseract

EXPOSE 8000

CMD ["python", "app/main.py"]
