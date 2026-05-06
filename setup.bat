@echo off
echo ========================================
echo Chronicles of Documents - Windows Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.12+ from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python is installed

REM Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama is not running!
    echo Please install Ollama from https://ollama.ai
    echo Then run: ollama pull llama3.2
    echo           ollama pull llama3.2-vision
    pause
)

echo.
echo Installing Python dependencies...
cd backend
pip install -r requirements.txt

echo.
echo Creating folders...
if not exist "documents" mkdir documents
if not exist "output" mkdir output

echo.
echo Creating .env file...
if not exist ".env" (
    echo OLLAMA_BASE_URL=http://localhost:11434 > .env
    echo OLLAMA_MODEL=llama3.2 >> .env
    echo OLLAMA_VISION_MODEL=llama3.2-vision >> .env
    echo OCR_METHOD=vision >> .env
    echo INPUT_FOLDER=./documents >> .env
    echo OUTPUT_FOLDER=./output >> .env
    echo [OK] Created .env file
) else (
    echo [OK] .env file already exists
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Place documents in: backend\documents\
echo 2. Run: cd backend
echo 3. Run: python app/main.py
echo 4. Check results in: backend\output\
echo.
pause
