# 🚀 GHID INSTALARE COMPLET - OCR Inteligent pentru Facturi

## ✅ Cerințe Sistemice

- **Windows 10/11** (Pro, Home, Enterprise)
- **Python 3.9+** (recomandă 3.10 sau 3.11)
- **Minimum 4GB RAM**
- **Spațiu disc: 2-3 GB** (pentru PyTorch și modele)
- **Conexiune internet** (pentru descărcări inițiale)

---

## 📋 PASUL 1: Instalarea Python

### Opțiunea A: Folosind Python Official (Recomandat)

1. **Descarcă Python**
   - Mergi la https://www.python.org/downloads/
   - Descarcă **Python 3.11** (cea mai stabilă versiune)
   - ⚠️ **IMPORTANT**: Bifează "Add Python to PATH"

2. **Verifică instalarea**
   ```powershell
   python --version
   pip --version
   ```

### Opțiunea B: Folosind Anaconda (Pentru Data Science)

1. **Descarcă Anaconda**
   - https://www.anaconda.com/download
   - Alege versiunea pentru Windows

2. **Creează environment virtual**
   ```powershell
   conda create -n ocr_env python=3.11
   conda activate ocr_env
   ```

---

## 🔧 PASUL 2: Instalarea Tesseract OCR Engine

### Ce este Tesseract?
Tesseract este motorul OCR tradițional open-source (cel mai bun pentru text clar).

### Instalare:

1. **Descarcă Tesseract pentru Windows**
   - Mergi la: https://github.com/UB-Mannheim/tesseract/wiki
   - Descarcă cel mai recent installer (ex: `tesseract-ocr-w64-setup-v5.x.x.exe`)

2. **Instalează cu suport limba română**
   - Rulează installerul
   - Când te întreabă despre "Additional language data"
   - ✅ Bifează: **Romanian (Română)**
   - ✅ Bifează: **English**
   - **Cale de instalare**: Lasă default `C:\Program Files\Tesseract-OCR`

3. **Verifică instalarea**
   ```powershell
   tesseract --version
   tesseract --list-langs
   ```

   Ar trebui să vezi `ron` în lista de limbi.

### Dacă rata de eroare la descărcare:

1. Descarcă manual fișierele de limbă:
   - https://github.com/UB-Mannheim/tesseract/wiki/Data-Files
   - Copiază în `C:\Program Files\Tesseract-OCR\tessdata`

---

## 📄 PASUL 3: Instalarea Poppler (Pentru PDF)

### Ce este Poppler?
Poppler convertește PDF-uri în imagini pentru procesare OCR.

### Instalare:

1. **Descarcă Poppler pentru Windows**
   - Mergi la: https://github.com/oschwartz10612/poppler-windows/releases/
   - Descarcă cel mai recent release (ex: `Release-25.12.0-0.zip`)

2. **Extrage în `C:\poppler`**
   ```powershell
   # Cale finală ar trebui să arate așa:
   C:\poppler\Library\bin\pdfinfo.exe
   ```

3. **Adaugă la PATH (opțional, dar recomandat)**
   - Deschide "System Properties" (Win+Pause)
   - "Advanced system settings"
   - "Environment Variables"
   - Adaugă în PATH: `C:\poppler\Library\bin`

---

## 🐍 PASUL 4: Setup Python Virtual Environment

### Creează folder proiect

```powershell
# Deschide PowerShell și merge în folder proiect
cd C:\Users\admin\Documents\OCR_INVOICE
```

### Creează virtual environment

```powershell
# Creează venv
python -m venv venv

# Activează venv (Pe Windows)
venv\Scripts\Activate

# Acum ar trebui să vezi (venv) la începutul liniei
```

### Upgrade pip

```powershell
python -m pip install --upgrade pip
```

---

## 📦 PASUL 5: Instalarea Dependențelor Python

### Instalare pachetele necesare

```powershell
# Asigură-te că ești în virtual environment (venv activat)

# Instalează din requirements.txt
pip install -r requirements.txt

# Aceasta poate dura 10-15 minute (télécharge ~1.5GB de modele)
# Fii patient! ⏳
```

### Dacă dai erori la instalare:

**Problemă: "ModuleNotFoundError" pentru cv2**
```powershell
pip install --upgrade opencv-python opencv-contrib-python
```

**Problemă: "Cannot import torch"**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Problemă: "pytesseract not found"**
- Verifică că Tesseract este instalat la `C:\Program Files\Tesseract-OCR`
- Editează fișierul și setează calea corect

---

## ⚙️ PASUL 6: Configurare Sistem OCR

### Creează structura directoare

```powershell
# Rulează scriptul de setup
python create_ground_truth_template.py

# Aceasta va crea:
# test_invoices/
# ├── excellent_quality/
# ├── good_quality/
# ├── poor_quality/
# └── very_poor_quality/
```

### Verifică configurația

```powershell
# Testează configurația
python config.py
```

Ar trebui să zie:
- ✓ Tesseract path
- ✓ Project paths
- ✓ OCR settings

---

## 🧪 PASUL 7: Test Sistem OCR

### Testare procesor OCR

```powershell
# 1. Plasează o imagine de factură în test_invoices/
# 2. Rulează demo:

python quick_benchmark_demo.py

# Alege opțiunea 1: Test Single Processor
```

### Expectedoutput:

```
OCR Engine: Tesseract
Confidence: 85.34%
Binarization: Adaptive Gaussian

Extracted Fields:
  invoice_number: FACT-2024-001
  invoice_date: 2024-01-15
  contractor: SC EXEMPLU SRL
  idno: 1234567890123
  total_amount: 1250.50
```

---

## 📊 PASUL 8: Preparare Date pentru Teză

### 1. Colectează Facturi de Test

Plasează imagini în directoarele corespunzătoare:

```
test_invoices/
├── excellent_quality/
│   ├── scan_001.jpg  (Scanată perfect, contrast bun)
│   └── scan_002.jpg
│
├── good_quality/
│   ├── photo_001.jpg  (Fotografie bună, iluminare OK)
│   └── photo_002.jpg
│
├── poor_quality/
│   ├── photo_blur_001.jpg  (Foto neclară, mic blur)
│   └── photo_dark_001.jpg  (Foto înclinată)
│
└── very_poor_quality/
    ├── photo_shadow_001.jpg  (Umbre, luminare inegală)
    └── photo_angle_001.jpg    (Foarte înclinată)
```

### 2. Creează Ground Truth CSV

```powershell
# Generează template
python create_ground_truth_template.py

# Aceasta creeazăground_truth.csv
```

### 3. Completează Ground Truth în Excel

1. Deschide `ground_truth.csv` în **Microsoft Excel**
2. Pentru **fiecare rând**, completează:
   - `true_invoice_number`: Numărul exact din factură
   - `true_invoice_date`: Data în format `YYYY-MM-DD`
   - `true_contractor`: Nume companie exact
   - `true_idno`: 13 cifre exact
   - `true_total_amount`: Suma cu zecimale (ex: 1250.50)

3. Salvează: **Ctrl+S**

---

## 🏃 PASUL 9: Rulează Benchmark Complet

### Pentru Teză

```powershell
# Creează folderul de rezultate
mkdir thesis_results

# Rulează benchmark
python ocr_benchmark_system.py

# Aceasta va genera:
# thesis_results/
# ├── graphs/
# │   ├── field_accuracy.png
# │   ├── confidence_distribution.png
# │   └── engine_comparison.png
# ├── reports/
# │   └── executive_summary.md
# ├── latex_tables/
# │   └── field_accuracy_table.tex
# └── benchmark_results.csv
```

### Demo Rapid (Testare)

```powershell
python quick_benchmark_demo.py --benchmark
```

---

## 📈 PASUL 10: Utilizează Rezultate în Teză

### Graficele Automate

Aceste imagini pot fi inserate direct în teză:
- `thesis_results/graphs/field_accuracy.png`
- `thesis_results/graphs/confidence_distribution.png`
- `thesis_results/graphs/engine_comparison.png`

**În LaTeX:**
```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{../thesis_results/graphs/field_accuracy.png}
\caption{Acuratețe Extragere Câmpuri OCR}
\label{fig:field_accuracy}
\end{figure}
```

### Tabelele LaTeX

Copiază direct din `thesis_results/latex_tables/field_accuracy_table.tex`

### Datele Brute pentru Analiză

Folosește `thesis_results/benchmark_results.csv` în Excel/Calc pentru grafice suplimentare

---

## 🐛 TROUBLESHOOTING

### Eroare: "tesseract not found"

```python
# La început de advanced_ocr_processor.py:

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Eroare: "TESSDATA_PREFIX not set"

```python
import os
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
```

### Eroare: "No module named easyocr"

```powershell
# Reinstalează cu GPU support (dacă NVIDIA disponibil):
pip install easyocr --upgrade

# Sau cu CPU only:
pip install easyocr torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Eroare: "ModuleNotFoundError: No module named 'pdf2image'"

```powershell
pip install pdf2image
# Și asigură-te că Poppler este instalat și în PATH
```

### Imagini procesate lent (mai mult de 5 secunde)

**Soluție: Activează GPU (dacă ai NVIDIA)**

1. Descarcă CUDA Toolkit: https://developer.nvidia.com/cuda-toolkit
2. Descarcă cuDNN: https://developer.nvidia.com/cudnn
3. Instalează și configurează PATH
4. În `config.py` setează: `'easyocr_gpu': True`

---

## 💾 BACKUP și MANAGEMENT

### Salvează Ground Truth
```powershell
# Backup importante date
Copy-Item ground_truth.csv ground_truth_backup.csv
Copy-Item thesis_results thesis_results_backup -Recurse
```

### Golire Cache
```powershell
# Golire cache modele OCR (dacă groapă spațiu)
Remove-Item -Path $env:USERPROFILE\.EasyOCR -Recurse -Force
```

---

## 📞 SUPORT

Dacă întâmpini probleme:

1. **Citește loguri de eroare** - sunt în limba engleză dar descriptive
2. **Verifica caile** - asigură-te că Tesseract și Poppler sunt la locurile corecte
3. **Testează individual**:
   ```powershell
   python quick_benchmark_demo.py --test
   python quick_benchmark_demo.py --compare
   ```

---

## 📚 URMĂTORII PAȘI

1. Colectează 30-50 facturi de test
2. Completează ground truth
3. Rulează benchmark complet
4. Analizează rezultate
5. Inserează grafice în teză
6. Scrie concluzii

**Estimare timp pentru teză complet:**
- Colectare facturi: 1-2 ore
- Completare ground truth: 2-4 ore
- Benchmark: 30 minute - 2 ore (depinde de count)
- Analiză și redactare: 2-3 ore

**Total: 6-12 ore de lucru**

---

**Succes cu teza! 🎓**
