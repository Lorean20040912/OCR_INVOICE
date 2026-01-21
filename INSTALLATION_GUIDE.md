# 🚀 Ghid Instalare Completă - Sistem OCR Avansat

## Sistem: Windows + PyCharm + Python 3.9+

---

## 📋 Verificări Preliminare

```powershell
# Verifică Python
python --version  # Trebuie >= 3.9

# Verifică dacă ai PyCharm
"C:\Program Files\JetBrains\PyCharm*" # Sau cauta în Program Files
```

---

## 🔧 Pasul 1: Instalează Tesseract OCR Engine

### 1.1 Descarcă Tesseract
- **Link**: [github.com/UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **Versiune recomandată**: `tesseract-ocr-w64-setup-v5.x.exe` (pentru Windows 64-bit)

### 1.2 Instalare
1. Descarcă și rulează setup-ul
2. **IMPORTANT**: La "Additional language data", selectează **Romanian (Română)**
3. Notează calea de instalare (de obicei: `C:\Program Files\Tesseract-OCR`)
4. Finalizează instalarea

### 1.3 Configurare în Cod
```python
import pytesseract

# Adaugă la ÎNCEPUTUL fișierului (după imports)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**NU MERGe?** Verifică:
- Instalezi versiunea de 64-bit (corespunde cu Python)
- Calea din cod să coincidă cu locația reală

---

## 📦 Pasul 2: Instalează Poppler (pentru PDF)

### 2.1 Descarcă Poppler
- **Link**: [github.com/oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)
- **Descarcă**: `Release-XX.XX.0-0.zip` (latest)

### 2.2 Instalare
1. Extrage ZIP-ul în `C:\poppler`
2. Adaugă la Windows PATH:
   - Apasă `Win + X` → "System"
   - Settings → "Environment Variables"
   - Adaugă în PATH: `C:\poppler\Library\bin`
3. Restart calculator (opțional, dar sigur)

### 2.3 Verificare
```powershell
# Deschide PowerShell și verifică
pdftotext --version  # Trebuie să apară versiunea
```

---

## 🐍 Pasul 3: Setare Virtual Environment în PyCharm

### 3.1 Deschide Proiectul în PyCharm
1. File → Open → Selectează folder-ul proiectului
2. Asteaptă ca PyCharm să indexeze fișierele

### 3.2 Creează Virtual Environment
```
File → Settings → Project: OCR_INVOICE → Python Interpreter
```

1. Click pe icon "gear" → "Add..."
2. Selectează "New environment"
3. Location: `C:\Users\admin\Documents\OCR_INVOICE\venv`
4. Base interpreter: (autodetectat)
5. Click "OK"

**Sau din Terminal**:
```powershell
cd C:\Users\admin\Documents\OCR_INVOICE
python -m venv venv
venv\Scripts\activate
```

### 3.3 Verifică Activare
```powershell
# Trebuie să vezi (venv) la începutul liniei
(venv) PS C:\Users\admin\Documents\OCR_INVOICE>
```

---

## 📥 Pasul 4: Instalează Pachete Python

### 4.1 Upgrade pip
```powershell
# Activează environment-ul dacă nu e activ
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### 4.2 Instalează Requirements
```powershell
# Instalează toate pachete
pip install -r requirements.txt

# ATENȚIE: Poate dura 10-15 minute!
# Torch și TorchVision sunt mari
```

### 4.3 Verificare
```powershell
# Verifică dacă s-a instalat corect
python -c "import cv2, easyocr, torch; print('✓ All OK!')"
```

**Probleme Comune**:

| Eroare | Soluție |
|--------|---------|
| `ModuleNotFoundError: No module named 'cv2'` | `pip install opencv-python` |
| `ModuleNotFoundError: No module named 'torch'` | `pip install torch` |
| `Timeout downloading` | `pip install --default-timeout=1000 -r requirements.txt` |

---

## 🧪 Pasul 5: Testare

### 5.1 Test Tesseract
```python
# test_tesseract.py
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Creeaza imagine test
img = Image.new('RGB', (200, 50), color='white')
text = pytesseract.image_to_string(img)
print("✓ Tesseract OK!")
```

### 5.2 Test EasyOCR
```python
# test_easyocr.py
import easyocr

reader = easyocr.Reader(['ro', 'en'], gpu=False)
print("✓ EasyOCR OK! (Prima oară descarcă modele, poate lua 5-10 min)")
```

### 5.3 Test Complet
```powershell
# Rulează din terminal
python advanced_ocr_processor.py
```

---

## 📊 Pasul 6: Generare Ground Truth și Benchmark

### 6.1 Creează Template Ground Truth
```powershell
python create_ground_truth_template.py
```

Rezultat: `ground_truth.csv` și folder `test_invoices/`

### 6.2 Completează Ground Truth
1. Deschide `ground_truth.csv` în Excel
2. Pentru fiecare factură, completează:
   - `true_invoice_number` (ex: FACT-2024-001)
   - `true_invoice_date` (format: 2024-01-15)
   - `true_contractor` (ex: SC EXEMPLU SRL)
   - `true_idno` (13 cifre, ex: 1234567890123)
   - `true_total_amount` (ex: 1250.50)

### 6.3 Rulează Benchmark
```powershell
# Demo benchmark (rapid)
python quick_benchmark_demo.py

# Benchmark complet
python -c "
from ocr_benchmark_system import OCRBenchmark
benchmark = OCRBenchmark(output_dir='thesis_results')
benchmark.run_full_benchmark('ground_truth.csv', 'test_invoices/')
"
```

### 6.4 Generează Raport
```powershell
python generate_thesis_report.py thesis_results
```

Rezultat: Grafice, tabele LaTeX, raport Markdown & HTML

---

## 🎓 Pasul 7: Utilizare în Teză

### 7.1 Structura pentru Capitolul Experimental

```
CAPITOLUL 4: STUDIU EXPERIMENTAL

4.1 Metodologia
    4.1.1 Dataset
    4.1.2 Metode evaluate
    4.1.3 Metrici

4.2 Rezultate
    [INSEREAZĂ: thesis_results/graphs/field_accuracy.png]
    [INSEREAZĂ: thesis_results/graphs/engine_comparison.png]
    
    Tabel LaTeX:
    [COPY din: thesis_results/latex_tables/field_accuracy_table.tex]

4.3 Discuție
    [COPY din: thesis_results/reports/executive_summary.md]

4.4 Concluzii
    [COPY din: thesis_results/Raport_Complet_Teza.md]
```

### 7.2 Export pentru Word/LaTeX
```powershell
# Imagini - în calitate înaltă
copy thesis_results/graphs/*.png "C:\Teza\images\"

# Tabele LaTeX
copy thesis_results/latex_tables/*.tex "C:\Teza\tables\"

# Raport Markdown → Copy în teză
notepad thesis_results/Raport_Complet_Teza.md
```

---

## ⚙️ Configurare Avansată

### GPU Support (Opțional)
Dacă ai GPU NVIDIA:

```powershell
# Desinstalează torch CPU
pip uninstall torch torchvision

# Instalează pytorch cu CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Configurare OCR
```python
# advanced_ocr_processor.py - linia ~140
class Config:
    USE_GPU = True  # Dacă ai GPU NVIDIA
    OCR_MIN_CONFIDENCE = 0.6
    SAVE_DEBUG_IMAGES = True
```

---

## 🐛 Troubleshooting

### Problema: "Tesseract not found"
```powershell
# Verifică instalare
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version

# Dacă merge, calea e corecta!
```

### Problema: "EasyOCR download timeout"
```powershell
# Instalează manual modelele
python -c "import easyocr; easyocr.Reader(['ro', 'en'], gpu=False)"
# Asteaptă să descarce (5-10 min)
```

### Problema: "Virtual environment nu merge"
```powershell
# Șterge env vechi
rmdir /s /q venv

# Recreează
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Problema: "ModuleNotFoundError: No module named 'torch'"
```powershell
# Verifică că ai environment activ
(venv) PS ... ← Trebuie să apară

# Dacă nu apare:
venv\Scripts\activate

# Apoi instalează din nou
pip install torch
```

---

## ✅ Checklist Final

- [ ] Tesseract instalat cu suport Română
- [ ] Poppler în PATH
- [ ] Virtual environment creat și activ
- [ ] Pachete instalate (`pip list` arată ~50 pachete)
- [ ] Test scripts au rulat cu succes
- [ ] Ground truth CSV creat și completat
- [ ] Benchmark a generat grafice
- [ ] Raport HTML/Markdown generat

---

## 📞 Suport

| Problemă | Link/Comanda |
|----------|-------------|
| Tesseract nu merge | https://github.com/UB-Mannheim/tesseract/wiki |
| Poppler PATH | `echo %PATH%` în PowerShell |
| Python version | `python --version` |
| Virtual env | `python -m venv --help` |

---

**Status**: ✓ Gata de utilizare!

Acum poți:
1. Procesa facturi cu OCR avansat
2. Genera benchmark-uri comparative
3. Crea rapoarte pentru teză
4. Integra în aplicația Flask

**Succes la teză!** 🎓📚
