#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE START PRINCIPAL - OCR INVOICE PROCESSOR
Pornește atât backend-ul Flask cât și frontend-ul React
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

class ProjectRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.frontend_path = self.project_root / "frontend"
        self.backend_path = self.project_root

    def check_requirements(self):
        """Verifică dacă sunt instalate dependințele"""
        print("🔍 Verificare dependințe...")

        # Verifică Python packages
        try:
            import flask, cv2, pytesseract
            print("✅ Python packages OK")
        except ImportError as e:
            print(f"❌ Lipsă package Python: {e}")
            print("💡 Rulează: pip install -r requirements.txt")
            return False

        # Verifică Node.js și npm
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js {result.stdout.strip()}")
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            print("❌ Node.js nu este instalat")
            print("💡 Descarcă și instalează Node.js de la https://nodejs.org")
            return False

        # Verifică dependințele frontend
        if not (self.frontend_path / "node_modules").exists():
            print("⚠️ Node modules nu sunt instalate")
            print("💡 Voi instala dependințele frontend...")
            return "install_frontend"

        return True

    def install_frontend_deps(self):
        """Instalează dependințele frontend"""
        print("📦 Instalare dependințe frontend...")
        os.chdir(self.frontend_path)

        try:
            subprocess.run(['npm', 'install'], check=True)
            print("✅ Dependințe frontend instalate")
            return True
        except subprocess.CalledProcessError:
            print("❌ Eroare la instalarea dependințelor frontend")
            return False
        finally:
            os.chdir(self.project_root)

    def start_backend(self):
        """Pornește backend-ul Flask"""
        print("🐍 Pornire backend Flask...")

        # Setează variabile de mediu
        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'development'

        try:
            subprocess.run([sys.executable, 'app.py'], cwd=self.backend_path)
        except KeyboardInterrupt:
            print("\n🔴 Backend Flask oprit")
        except Exception as e:
            print(f"❌ Eroare backend: {e}")

    def start_frontend(self):
        """Pornește frontend-ul React"""
        print("⚛️ Pornire frontend React...")

        try:
            subprocess.run(['npm', 'run', 'dev'], cwd=self.frontend_path)
        except KeyboardInterrupt:
            print("\n🔴 Frontend React oprit")
        except Exception as e:
            print(f"❌ Eroare frontend: {e}")

    def open_browser(self):
        """Deschide browser după câteva secunde"""
        time.sleep(5)
        try:
            webbrowser.open('http://localhost:5173')
            print("🌐 Aplicația s-a deschis în browser!")
        except:
            print("💡 Deschide manual: http://localhost:5173")

    def run(self):
        """Rulează proiectul complet"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                  OCR INVOICE PROCESSOR                       ║
║                    🚀 PORNIRE PROIECT                        ║
╚══════════════════════════════════════════════════════════════╝
""")

        # Verifică cerințele
        check_result = self.check_requirements()
        if check_result == False:
            return
        elif check_result == "install_frontend":
            if not self.install_frontend_deps():
                return

        print("\n🎯 Pornire servicii...")
        print("📍 Backend Flask: http://localhost:5000")
        print("📍 Frontend React: http://localhost:5173")
        print("🔄 CTRL+C pentru a opri\n")

        try:
            # Pornește backend în thread separat
            backend_thread = threading.Thread(target=self.start_backend, daemon=True)
            backend_thread.start()

            # Așteaptă puțin ca backend-ul să pornească
            time.sleep(3)

            # Deschide browser în thread separat
            browser_thread = threading.Thread(target=self.open_browser, daemon=True)
            browser_thread.start()

            # Pornește frontend în thread principal
            self.start_frontend()

        except KeyboardInterrupt:
            print("\n\n🔴 Oprire aplicație...")
            print("👋 La revedere!")

def main():
    """Funcția principală"""
    runner = ProjectRunner()
    runner.run()

if __name__ == '__main__':
    main()
