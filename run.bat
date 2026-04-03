@echo off
echo.
echo  StockMind AI - Setup Script (Windows)
echo ==========================================
echo.

cd backend

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies (this may take 2 minutes)...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
venv\Scripts\pip.exe install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Dependency installation failed.
    echo Try running manually:
    echo   cd backend
    echo   venv\Scripts\pip.exe install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [4/4] All dependencies installed!
echo.
echo  Backend API starting at: http://localhost:8000
echo  Now open frontend\index.html in your browser
echo.
echo  Press Ctrl+C to stop the server
echo.

venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000 --reload
pause
