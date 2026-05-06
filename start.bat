@echo off
echo Chronicles of Documents - Quick Start
echo =====================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo X Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo [OK] Docker is installed
echo.

REM Ask user which mode
echo Select mode:
echo 1) Development (uses Ollama vision models on host)
echo 2) Production (uses Tesseract OCR in container)
set /p choice="Enter choice [1-2]: "

if "%choice%"=="1" (
    echo.
    echo Starting in DEVELOPMENT mode...
    echo.
    echo Make sure Ollama is running on your host:
    echo   ollama pull llama3.2
    echo   ollama pull llama3.2-vision
    echo.
    pause
    
    docker-compose -f docker-compose.dev.yml up
) else if "%choice%"=="2" (
    echo.
    echo Starting in PRODUCTION mode...
    echo This will start MongoDB, ChromaDB, and Backend with Tesseract OCR
    echo.
    
    docker-compose up -d
    
    echo.
    echo [OK] Services started!
    echo.
    echo [Folder] Place documents in: backend\documents\
    echo [Results] Check results in: backend\output\
    echo.
    echo View logs: docker-compose logs -f backend
    echo Stop services: docker-compose down
    echo.
    pause
) else (
    echo Invalid choice
    pause
    exit /b 1
)
