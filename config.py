"""
Configurare Sistem OCR Inteligent
Setări optimizate pentru procesare facturi în română și engleză
"""
import os
from pathlib import Path

# Încarcă variabilele de mediu din .env dacă python-dotenv este disponibil;
# altfel continuă fără a opri aplicația.
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - fallback dacă lipsește pachetul
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()


class Config:
    """Configurare globală sistem OCR"""

    # === PROJECT PATHS ===
    BASE_DIR = Path(__file__).parent.absolute()
    PROJECT_ROOT = BASE_DIR

    # Căi utilizate în restul codului
    UPLOAD_FOLDER = BASE_DIR / 'uploads'         # compat pentru cod existent
    EXPORT_FOLDER = BASE_DIR / 'exports'
    JSON_EXPORT_PATH = EXPORT_FOLDER / 'json'
    XML_EXPORT_PATH = EXPORT_FOLDER / 'xml'
    DBF_EXPORT_PATH = EXPORT_FOLDER / 'dbf'

    # Denumiri alternative folosite de alte module
    UPLOADS_DIR = UPLOAD_FOLDER
    DEBUG_DIR = BASE_DIR / 'debug_preprocessing'
    RESULTS_DIR = BASE_DIR / 'benchmark_results'
    THESIS_RESULTS_DIR = BASE_DIR / 'thesis_results'
    TEST_INVOICES_DIR = BASE_DIR / 'test_invoices'

    # === FILES & LIMITS ===
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    MAX_FILE_SIZE = MAX_CONTENT_LENGTH

    # === TESSERACT & POPPLER (Windows) ===
    TESSERACT_CONFIG = '--psm 6 --oem 3 -l ron'
    TESSERACT_PATH = os.environ.get('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    TESSDATA_PREFIX = os.environ.get('TESSDATA_PREFIX', r'C:\Program Files\Tesseract-OCR\tessdata')
    POPPLER_PATH = os.environ.get('POPPLER_PATH', r'C:\poppler\Library\bin')

    # === OCR ENGINE SETTINGS ===
    OCR_CONFIG = {
        'tesseract_psm': 6,   # 6 = Assume a single uniform block of text
        'tesseract_oem': 3,   # 3 = Both legacy and LSTM model
        'tesseract_lang': 'ron',
        'min_confidence': 0.5,
        'easyocr_gpu': False,
        'easyocr_languages': ['ro', 'en'],
    }

    # === INVOICE FIELD PATTERNS ===
    INVOICE_PATTERNS = {
        'invoice_number': [
            r'(?:FACT|Factur|Nr|Invoice|#|Factură)\s*[-:]*\s*([A-Z0-9\-/]+)',
            r'([A-Z]{1,3}\d{2,4}[/-]\d{1,6})',
        ],
        'invoice_date': [
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',
            r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',
        ],
        'idno': [
            r'\b(\d{13})\b',
            r'(?:IDNO|Tax ID)\s*[:=]?\s*(\d{13})',
        ],
        'total_amount': [
            r'(?:Total|Suma|Amount)\s*[:=]?\s*([\d,. ]+)',
            r'\b(\d+[.,]\d{2})\s*(?:MDL|RON|EUR|USD)\b',
        ]
    }

    # === BENCHMARK & THESIS SETTINGS ===
    BENCHMARK = {
        'output_dir': 'benchmark_results',
        'graph_dpi': 300,
        'generate_latex': True,
        'generate_graphs': True,
    }
    THESIS = {
        'output_dir': 'thesis_results',
        'include_debug_images': False,
        'include_raw_data': True,
        'min_invoices_for_analysis': 20,
    }

    # === EXTERNAL SERVICES ===
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    ONE_C_API_URL = os.getenv('ONE_C_API_URL', 'http://localhost:8080/api')
    ONE_C_USERNAME = os.getenv('ONE_C_USERNAME', 'admin')
    ONE_C_PASSWORD = os.getenv('ONE_C_PASSWORD', 'password')

    # === LOGGING ===
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # === UTIL ===
    @classmethod
    def create_directories(cls):
        """Creează directoarele necesare pentru rulare"""
        directories = [
            cls.UPLOAD_FOLDER,
            cls.EXPORT_FOLDER,
            cls.JSON_EXPORT_PATH,
            cls.XML_EXPORT_PATH,
            cls.DBF_EXPORT_PATH,
            cls.DEBUG_DIR,
            cls.RESULTS_DIR,
            cls.THESIS_RESULTS_DIR,
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)