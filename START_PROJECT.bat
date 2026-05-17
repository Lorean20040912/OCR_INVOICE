 @echo off
title OCR Invoice Processor - Full Stack

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  OCR INVOICE PROCESSOR                       ║
echo ║                    🚀 FULL STACK START                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nu este instalat sau nu este în PATH
    echo 💡 Instalează Python de la https://python.org
    pause
    exit /b 1
)
echo ✅ Python găsit

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js nu este instalat
    echo 💡 Instalează Node.js de la https://nodejs.org
    pause
    exit /b 1
)
echo ✅ Node.js găsit

echo.
echo 🔧 Checking dependencies...

REM Install Python packages if needed
if not exist "venv" (
    echo 📦 Creez virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
echo ✅ Python packages ready

REM Install Node packages if needed
cd frontend
if not exist node_modules (
    echo 📦 Installing Node dependencies...
    call npm install
)
echo ✅ Node packages ready
cd ..

echo.
echo 🚀 Starting services...
echo 📍 Backend: http://localhost:5000
echo 📍 Frontend: http://localhost:5173
echo.
echo ⚠️  Deschide 2 terminale separate:
echo    Terminal 1: python run.py
echo    Terminal 2: cd frontend ^&^& npm run dev
echo.
echo Sau folosește: python start_project.py (automatic)
echo.

pause
