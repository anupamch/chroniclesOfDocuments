@echo off
echo ========================================
echo Chronicles of Documents - API Test
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

REM Install requests if needed
echo Installing dependencies...
pip install requests >nul 2>&1

echo.
echo Starting API tests...
echo.
echo Make sure:
echo 1. Docker containers are running (docker-compose up)
echo 2. API is accessible at http://localhost:8000
echo.
pause

python test_api.py

echo.
pause
