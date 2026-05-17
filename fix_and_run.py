#!/usr/bin/env python3
"""
⚡ FIX & RUN - OCR INVOICE PROCESSOR
Repară rapid și pornește aplicația
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("""
🔧 FIX & RUN - OCR INVOICE PROCESSOR
====================================
""")

    project_root = Path(__file__).parent.absolute()
    frontend_path = project_root / "frontend"

    print("1️⃣ Instalez Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Python packages OK")
    except:
        print("⚠️ Unele Python packages au eșuat - continuez...")

    print("\n2️⃣ Instalez Node.js dependencies...")
    try:
        os.chdir(frontend_path)
        subprocess.run(['npm', 'install'], check=True, capture_output=True)
        print("✅ Node.js packages OK")
        os.chdir(project_root)
    except:
        print("❌ Node.js packages au eșuat - verifică Node.js")
        return

    print("\n3️⃣ Creez directoarele...")
    dirs = ['uploads', 'exports', 'exports/json', 'exports/xml', 'exports/dbf']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✅ Directoare create")

    print("""
🚀 Pornesc aplicația...

Terminal 1: python app.py
Terminal 2: cd frontend && npm run dev

Sau rulează: python auto_setup_and_run.py
""")

if __name__ == '__main__':
    main()
