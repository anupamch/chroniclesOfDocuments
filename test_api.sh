#!/bin/bash

echo "========================================"
echo "Chronicles of Documents - API Test"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python is not installed!"
    exit 1
fi

# Install requests if needed
echo "Installing dependencies..."
pip3 install requests > /dev/null 2>&1

echo ""
echo "Starting API tests..."
echo ""
echo "Make sure:"
echo "1. Docker containers are running (docker-compose up)"
echo "2. API is accessible at http://localhost:8000"
echo ""
read -p "Press Enter to continue..."

python3 test_api.py
