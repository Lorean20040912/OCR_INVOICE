#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 AUTO SETUP & RUN - OCR INVOICE PROCESSOR
Instalează automat tot ce trebuie și pornește aplicația
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
import urllib.request
import zipfile

class AutoSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.frontend_path = self.project_root / "frontend"
        self.venv_path = self.project_root / "venv"

    def print_header(self):
        print("""
╔══════════════════════════════════════════════════════════════╗
║                  OCR INVOICE PROCESSOR                       ║
║                🔧 AUTO SETUP & RUN                          ║
╚══════════════════════════════════════════════════════════════╝

🚀 Configurez și pornesc totul automat...
""")

    def check_python(self):
        """Verifică Python"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                print(f"✅ Python {version.major}.{version.minor} OK")
                return True
            else:
                print(f"❌ Python {version.major}.{version.minor} prea vechi (minim Python 3.8)")
                return False
        except:
            print("❌ Python nu este instalat")
            return False

    def setup_virtual_environment(self):
        """Creează și activează virtual environment"""
        print("📦 Configurez Python virtual environment...")

        if not self.venv_path.exists():
            try:
                subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], check=True)
                print("✅ Virtual environment creat")
            except subprocess.CalledProcessError:
                print("❌ Eroare la crearea virtual environment")
                return False
        else:
            print("✅ Virtual environment există deja")

        # Determină calea către executabilul Python din venv
        if os.name == 'nt':  # Windows
            self.python_exe = self.venv_path / "Scripts" / "python.exe"
            self.pip_exe = self.venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux/Mac
            self.python_exe = self.venv_path / "bin" / "python"
            self.pip_exe = self.venv_path / "bin" / "pip"

        return True

    def install_python_packages(self):
        """Instalează packageurile Python"""
        print("📦 Instalez dependințele Python...")

        # Lista minimă de package-uri esențiale
        essential_packages = [
            "flask==3.0.0",
            "flask-cors==4.0.0", 
            "opencv-python==4.8.1.78",
            "pytesseract==0.3.10",
            "pillow==10.1.0",
            "numpy==1.24.3",
            "requests==2.31.0",
            "python-dotenv==1.0.0"
        ]

        try:
            # Upgrade pip
            subprocess.run([str(self.pip_exe), 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            print("✅ pip actualizat")

            # Instalează packageurile esențiale
            for package in essential_packages:
                print(f"   Installing {package.split('==')[0]}...")
                result = subprocess.run([str(self.pip_exe), 'install', package], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"⚠️ Eroare la {package}: {result.stderr}")

            print("✅ Dependințe Python instalate")
            return True

        except Exception as e:
            print(f"❌ Eroare la instalarea Python packages: {e}")
            return False

    def check_node(self):
        """Verifică și instalează Node.js"""
        print("🔍 Verific Node.js...")

        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Node.js {version} găsit")
                return True
        except FileNotFoundError:
            pass

        print("❌ Node.js nu este instalat")
        print("💡 Descarcă Node.js de la: https://nodejs.org")
        print("⚠️ Instalează Node.js și rulează din nou scriptul")
        return False

    def setup_frontend(self):
        """Configurează frontend-ul"""
        print("⚛️ Configurez frontend React...")

        if not self.frontend_path.exists():
            print("❌ Folderul frontend nu există")
            return False

        os.chdir(self.frontend_path)

        try:
            # Verifică package.json
            if not (self.frontend_path / "package.json").exists():
                print("❌ package.json nu există în frontend")
                return False

            # Instalează dependințele
            print("📦 Instalez dependințele frontend...")
            result = subprocess.run(['npm', 'install'], 
                                  capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Frontend dependencies instalate")
                return True
            else:
                print(f"❌ Eroare npm install: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Eroare setup frontend: {e}")
            return False
        finally:
            os.chdir(self.project_root)

    def verify_tesseract(self):
        """Verifică Tesseract OCR"""
        print("🔍 Verific Tesseract OCR...")

        try:
            # Încearcă să ruleze tesseract
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tesseract OCR găsit")
                return True
        except FileNotFoundError:
            pass

        print("⚠️ Tesseract OCR nu este găsit în PATH")
        print("💡 Pentru OCR complet, instalează Tesseract:")
        print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-ron")
        print("📝 Aplicația va funcționa cu OCR limitat")
        return False

    def create_missing_files(self):
        """Creează fișierele lipsă necesare"""
        print("📝 Verific fișierele necesare...")

        # Creează directoarele
        directories = ['uploads', 'exports', 'exports/json', 'exports/xml', 'exports/dbf']
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)

        print("✅ Directoare create")

    def start_backend(self):
        """Pornește backend Flask"""
        print("🐍 Pornesc backend Flask...")

        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'development'

        try:
            subprocess.run([str(self.python_exe), 'app.py'], cwd=self.project_root)
        except KeyboardInterrupt:
            print("\n🔴 Backend oprit")
        except Exception as e:
            print(f"❌ Eroare backend: {e}")

    def start_frontend(self):
        """Pornește frontend React"""
        print("⚛️ Pornesc frontend React...")

        try:
            subprocess.run(['npm', 'run', 'dev'], cwd=self.frontend_path)
        except KeyboardInterrupt:
            print("\n🔴 Frontend oprit")
        except Exception as e:
            print(f"❌ Eroare frontend: {e}")

    def open_browser(self):
        """Deschide browser"""
        time.sleep(8)
        try:
            webbrowser.open('http://localhost:5173')
            print("🌐 Aplicația s-a deschis în browser!")
        except:
            print("💡 Deschide manual: http://localhost:5173")

    def run_application(self):
        """Rulează aplicația completă"""
        print("\n🚀 Pornesc aplicația...")
        print("📍 Backend Flask: http://localhost:5000")
        print("📍 Frontend React: http://localhost:5173")
        print("🔄 CTRL+C pentru oprire\n")

        try:
            # Backend în thread
            backend_thread = threading.Thread(target=self.start_backend, daemon=True)
            backend_thread.start()

            # Browser în thread
            browser_thread = threading.Thread(target=self.open_browser, daemon=True)
            browser_thread.start()

            # Așteaptă puțin
            time.sleep(4)

            # Frontend în thread principal
            self.start_frontend()

        except KeyboardInterrupt:
            print("\n\n🔴 Aplicația oprită")
            print("👋 La revedere!")

    def main(self):
        """Funcția principală"""
        self.print_header()

        # 1. Verifică Python
        if not self.check_python():
            input("Apasă Enter pentru ieșire...")
            return

        # 2. Setup virtual environment
        if not self.setup_virtual_environment():
            input("Apasă Enter pentru ieșire...")
            return

        # 3. Instalează Python packages
        if not self.install_python_packages():
            input("Apasă Enter pentru ieșire...")
            return

        # 4. Verifică Node.js
        if not self.check_node():
            input("Apasă Enter pentru ieșire...")
            return

        # 5. Setup frontend
        if not self.setup_frontend():
            input("Apasă Enter pentru ieșire...")
            return

        # 6. Verifică Tesseract (opțional)
        self.verify_tesseract()

        # 7. Creează fișiere
        self.create_missing_files()

        print("\n" + "="*60)
        print("🎉 SETUP COMPLET! Pornesc aplicația...")
        print("="*60)

        # 8. Rulează aplicația
        self.run_application()

if __name__ == '__main__':
    setup = AutoSetup()
    setup.main()
