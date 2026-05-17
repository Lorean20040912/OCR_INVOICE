#!/usr/bin/env python3
"""
SCRIPT DE START SIMPLU - OCR INVOICE PROCESSOR
Pornește backend-ul Flask
"""

import os
import sys
from pathlib import Path
from config import Config

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  OCR INVOICE PROCESSOR                       ║
║                    🚀 BACKEND START                          ║
╚══════════════════════════════════════════════════════════════╝
""")

    # Creează directoarele necesare
    Config.create_directories()
    print("✅ Directoare create")

    # Verifică Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR găsit")
    except:
        print("❌ Tesseract OCR nu este instalat sau configurat")
        print("💡 Instalează Tesseract OCR și configurează calea")

    print("\n🐍 Pornesc Flask server...")
    print("📍 Backend API: http://localhost:5000")
    print("🔄 CTRL+C pentru stop\n")

    # Pornește aplicația
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
