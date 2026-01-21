#!/usr/bin/env python3
"""
OCR INTELLIGENCE SYSTEM - STARTUP WIZARD
Asistență interactivă pentru setup și utilizare sistem OCR inteligent
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil


class OCRSetupWizard:
    """Wizard interactiv pentru setup și utilizare sistem OCR"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / 'venv'
        
    def print_header(self, text):
        """Tipărește header frumos"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)
    
    def print_section(self, text):
        """Tipărește secțiune"""
        print(f"\n📌 {text}")
        print("-"*60)
    
    def check_python(self):
        """Verifică dacă Python este instalat corect"""
        try:
            import sys
            version = sys.version_info
            if version.major < 3 or (version.major == 3 and version.minor < 9):
                print(f"❌ Python {version.major}.{version.minor} detectat")
                print(f"   Necesită Python 3.9 sau mai nou!")
                return False
            print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
            return True
        except Exception as e:
            print(f"❌ Eroare Python: {e}")
            return False
    
    def check_venv(self):
        """Verifică dacă virtual environment există"""
        if not self.venv_path.exists():
            print(f"❌ Virtual environment nu găsit la: {self.venv_path}")
            return False
        print(f"✓ Virtual environment găsit")
        return True
    
    def create_venv(self):
        """Creează virtual environment"""
        print(f"\n⏳ Creație virtual environment...")
        try:
            subprocess.run([sys.executable, '-m', 'venv', str(self.venv_path)], check=True)
            print(f"✓ Virtual environment creat: {self.venv_path}")
            return True
        except Exception as e:
            print(f"❌ Eroare: {e}")
            return False
    
    def check_tesseract(self):
        """Verifică dacă Tesseract OCR este instalat"""
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                print(f"✓ Tesseract găsit la: {path}")
                return True
        
        print(f"❌ Tesseract nu găsit!")
        print(f"   Descarcă de la: https://github.com/UB-Mannheim/tesseract/wiki")
        print(f"   Instalează cu limba română!")
        return False
    
    def check_poppler(self):
        """Verifică dacă Poppler este instalat"""
        poppler_paths = [
            r'C:\poppler\Library\bin',
            r'C:\poppler-0.68.0\Library\bin',
        ]
        
        for path in poppler_paths:
            if os.path.exists(path):
                print(f"✓ Poppler găsit la: {path}")
                return True
        
        print(f"⚠ Poppler nu găsit (necesar doar pentru PDF)")
        print(f"   Descarcă de la: https://github.com/oschwartz10612/poppler-windows")
        return False
    
    def check_packages(self):
        """Verifică dacă pachete Python sunt instalate"""
        required_packages = [
            'cv2', 'numpy', 'pandas', 'PIL', 'easyocr', 
            'pytesseract', 'torch', 'matplotlib', 'seaborn'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✓ {package}")
            except ImportError:
                print(f"❌ {package}")
                missing.append(package)
        
        if missing:
            print(f"\n⚠ Lipsă: {', '.join(missing)}")
            print(f"   Rulează: pip install -r requirements.txt")
            return False
        
        return True
    
    def setup_directories(self):
        """Creează structura de directoare"""
        dirs = [
            'test_invoices/excellent_quality',
            'test_invoices/good_quality',
            'test_invoices/poor_quality',
            'test_invoices/very_poor_quality',
            'debug_preprocessing',
            'benchmark_results',
            'thesis_results',
            'uploads',
        ]
        
        for dir_name in dirs:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("✓ Structură directoare creată/verificată")
    
    def main_menu(self):
        """Afișează meniu principal"""
        self.print_header("OCR INTELLIGENCE SYSTEM - MENIU PRINCIPAL")
        
        print("""
1. 🔧 SETUP - Verifica și configura sistemul
2. 📊 BENCHMARK - Rulează OCR benchmark
3. 📝 GROUND TRUTH - Creeaza template si completeaza
4. 🧪 TEST - Testeaza procesor OCR pe o imagine
5. 📈 ANALYZE - Analizează rezultate existente
6. 📚 DOCS - Deschide documentație
7. 🛠️  ADVANCED - Comenzi avansate
0. ❌ IEȘIRE

        """)
    
    def menu_setup(self):
        """Meniu: Verificare și setup"""
        self.print_header("VERIFICARE ȘI SETUP SISTEM")
        
        checks = [
            ("Python", self.check_python),
            ("Virtual Environment", self.check_venv),
            ("Tesseract OCR", self.check_tesseract),
            ("Poppler (PDF)", self.check_poppler),
            ("Pachete Python", self.check_packages),
        ]
        
        all_ok = True
        for check_name, check_func in checks:
            self.print_section(f"Verificare: {check_name}")
            if not check_func():
                all_ok = False
        
        self.print_section("Directoare")
        self.setup_directories()
        
        if all_ok:
            print("\n✅ SISTEM GATA! Poți rula benchmark-ul")
        else:
            print("\n⚠️  Sistem incomplet. Consultă instrucțiuni de instalare.")
    
    def menu_benchmark(self):
        """Meniu: Rulează benchmark"""
        self.print_header("BENCHMARK OCR")
        
        print("""
1. Demo rapid (pe imagini existente)
2. Benchmark complet (pe ground_truth.csv)
3. Benchmark pe folder specific
0. Înapoi

        """)
        
        choice = input("Alege opțiune: ").strip()
        
        if choice == '1':
            print("⏳ Benchmark demo...")
            os.system('python quick_benchmark_demo.py --benchmark')
        elif choice == '2':
            if not os.path.exists('ground_truth.csv'):
                print("❌ ground_truth.csv nu găsit!")
                print("   Rulează: python create_ground_truth_template.py")
                return
            
            print("⏳ Benchmark complet...")
            os.system('python -c "from ocr_benchmark_system import OCRBenchmark; b = OCRBenchmark(output_dir=\'thesis_results\'); b.run_full_benchmark(\'ground_truth.csv\', \'test_invoices/\')"')
            
            print("\n✅ Benchmark complet!")
            print("📁 Rezultate în: thesis_results/")
        elif choice == '3':
            folder = input("Introdu calea folderului: ").strip()
            print(f"⏳ Benchmark pe {folder}...")
    
    def menu_ground_truth(self):
        """Meniu: Ground truth"""
        self.print_header("GROUND TRUTH")
        
        print("""
1. Creeaza template CSV (din imaginile existente)
2. Creeaza structura directoare de calitate
3. Deschide template in Excel
0. Înapoi

        """)
        
        choice = input("Alege opțiune: ").strip()
        
        if choice == '1':
            print("⏳ Creare template...")
            os.system('python create_ground_truth_template.py')
        elif choice == '2':
            os.makedirs('test_invoices/excellent_quality', exist_ok=True)
            os.makedirs('test_invoices/good_quality', exist_ok=True)
            os.makedirs('test_invoices/poor_quality', exist_ok=True)
            os.makedirs('test_invoices/very_poor_quality', exist_ok=True)
            print("✓ Structură creată")
        elif choice == '3':
            if os.path.exists('ground_truth.csv'):
                os.startfile('ground_truth.csv')
                print("✓ Deschis în Excel")
            else:
                print("❌ ground_truth.csv nu găsit")
    
    def menu_test(self):
        """Meniu: Test"""
        self.print_header("TEST OCR PROCESSOR")
        
        print("""
1. Test pe o singură imagine
2. Comparație Tesseract vs EasyOCR
3. Test pre-procesare (debug)
0. Înapoi

        """)
        
        choice = input("Alege opțiune: ").strip()
        
        if choice == '1':
            print("⏳ Test procesor...")
            os.system('python quick_benchmark_demo.py --test')
        elif choice == '2':
            print("⏳ Comparație motoare...")
            os.system('python quick_benchmark_demo.py --compare')
    
    def menu_analyze(self):
        """Meniu: Analiză"""
        self.print_header("ANALIZA REZULTATE")
        
        print("""
Fișiere disponibile:
1. Deschide benchmark_results/benchmark_results.csv
2. Deschide thesis_results/benchmark_results.csv
3. Deschide rapoarte Markdown
0. Înapoi

        """)
        
        choice = input("Alege opțiune: ").strip()
        
        if choice == '1' and os.path.exists('benchmark_results/benchmark_results.csv'):
            os.startfile('benchmark_results/benchmark_results.csv')
        elif choice == '2' and os.path.exists('thesis_results/benchmark_results.csv'):
            os.startfile('thesis_results/benchmark_results.csv')
        elif choice == '3':
            if os.path.exists('thesis_results/reports/executive_summary.md'):
                os.startfile('thesis_results/reports/executive_summary.md')
    
    def menu_docs(self):
        """Meniu: Documentație"""
        self.print_header("DOCUMENTAȚIE")
        
        docs = [
            ('WINDOWS_INSTALLATION_GUIDE.md', 'Ghid instalare Windows'),
            ('THESIS_WORKFLOW_GUIDE.md', 'Ghid workflow pentru teză'),
            ('README_OCR_SYSTEM.md', 'README sistem'),
            ('QUICK_REFERENCE.md', 'Referință rapidă'),
        ]
        
        for i, (filename, description) in enumerate(docs, 1):
            print(f"{i}. {description}")
            print(f"   {filename}")
        
        choice = input("\nAlege fișier (nr): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(docs):
                os.startfile(docs[idx][0])
        except:
            pass
    
    def menu_advanced(self):
        """Meniu: Comenzi avansate"""
        self.print_header("COMENZI AVANSATE")
        
        print("""
1. Configurare manuală
2. Clear cache OCR
3. Genereaza raport HTML
4. Debug preprocessing
5. Statistici sistem
0. Înapoi

        """)
        
        choice = input("Alege opțiune: ").strip()
        
        if choice == '1':
            os.system('python -c "from config import CONFIG; print(CONFIG.__dict__)"')
        elif choice == '5':
            print("\n📊 Statistici sistem:")
            print(f"Python: {sys.version}")
            print(f"Project: {self.project_root}")
            print(f"venv: {self.venv_path.exists()}")
    
    def run(self):
        """Rulează wizard-ul"""
        while True:
            self.main_menu()
            
            choice = input("Alege opțiune (0-7): ").strip()
            
            if choice == '1':
                self.menu_setup()
            elif choice == '2':
                self.menu_benchmark()
            elif choice == '3':
                self.menu_ground_truth()
            elif choice == '4':
                self.menu_test()
            elif choice == '5':
                self.menu_analyze()
            elif choice == '6':
                self.menu_docs()
            elif choice == '7':
                self.menu_advanced()
            elif choice == '0':
                print("\n👋 Bye!")
                break
            else:
                print("❌ Opțiune necunoscută")
            
            input("\nPrésează Enter să continui...")


if __name__ == '__main__':
    wizard = OCRSetupWizard()
    
    if len(sys.argv) > 1:
        # Comenzi direct
        if sys.argv[1] == '--setup':
            wizard.menu_setup()
        elif sys.argv[1] == '--benchmark':
            wizard.menu_benchmark()
        elif sys.argv[1] == '--test':
            wizard.menu_test()
        else:
            wizard.run()
    else:
        # Menu interactiv
        wizard.run()
