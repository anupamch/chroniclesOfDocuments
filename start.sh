#!/bin/bash

echo "Chronicles of Documents - Quick Start"
echo "====================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Ask user which mode
echo "Select mode:"
echo "1) Development (uses Ollama vision models on host)"
echo "2) Production (uses Tesseract OCR in container)"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "Starting in DEVELOPMENT mode..."
        echo ""
        echo "Make sure Ollama is running on your host:"
        echo "  ollama pull llama3.2"
        echo "  ollama pull llama3.2-vision"
        echo ""
        read -p "Press Enter to continue..."
        
        docker-compose -f docker-compose.dev.yml up
        ;;
    2)
        echo ""
        echo "Starting in PRODUCTION mode..."
        echo "This will start MongoDB, ChromaDB, and Backend with Tesseract OCR"
        echo ""
        
        docker-compose up -d
        
        echo ""
        echo "✅ Services started!"
        echo ""
        echo "📁 Place documents in: backend/documents/"
        echo "📊 Check results in: backend/output/"
        echo ""
        echo "View logs: docker-compose logs -f backend"
        echo "Stop services: docker-compose down"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
