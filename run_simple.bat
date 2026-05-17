@echo off
title OCR Invoice Processor - Simple Run

echo 🔧 OCR INVOICE PROCESSOR - SIMPLE RUN
echo =====================================
echo.

echo 1. Instalez dependencies...
pip install flask flask-cors opencv-python pytesseract pillow numpy requests python-dotenv
echo.

echo 2. Creez directoare...
if not exist "uploads" mkdir uploads
if not exist "exports" mkdir exports
if not exist "exports\json" mkdir exports\json
if not exist "exports\xml" mkdir exports\xml
if not exist "exports\dbf" mkdir exports\dbf
echo.

echo 3. Frontend setup...
cd frontend
if not exist node_modules npm install
cd ..
echo.

echo 🚀 Pentru pornire:
echo Backend:  python app.py
echo Frontend: cd frontend ^&^& npm run dev
echo.

echo Sau automatic: python auto_setup_and_run.py
pause
