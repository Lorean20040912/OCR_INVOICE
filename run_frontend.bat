@echo off
title OCR Frontend - React App

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  OCR INVOICE PROCESSOR                       ║
echo ║                    ⚛️ FRONTEND START                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0frontend"

if not exist node_modules (
    echo 📦 Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo ❌ Error installing dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed
)

echo.
echo 🚀 Starting React development server...
echo 📍 Frontend: http://localhost:5173
echo 🔄 CTRL+C to stop
echo.

call npm run dev

pause
