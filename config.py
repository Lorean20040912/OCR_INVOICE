"""
Configurare Sistem OCR Inteligent
Setări optimizate pentru procesare facturi în moldavă și engleză
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurare globală sistem OCR"""
    
    # === PROJECT PATHS ===
    PROJECT_ROOT = Path(__file__).parent
    TEST_INVOICES_DIR = PROJECT_ROOT / 'test_invoices'
    DEBUG_DIR = PROJECT_ROOT / 'debug_preprocessing'
    RESULTS_DIR = PROJECT_ROOT / 'benchmark_results'
    THESIS_RESULTS_DIR = PROJECT_ROOT / 'thesis_results'
    UPLOADS_DIR = PROJECT_ROOT / 'uploads'
    
    # === TESSERACT & POPPLER (Windows) ===
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSDATA_PREFIX = r'C:\Program Files\Tesseract-OCR\tessdata'
    POPPLER_PATH = r'C:\poppler\Library\bin'
    
    # === OCR ENGINE SETTINGS ===
    OCR_CONFIG = {
        'tesseract_psm': 6,  # 6 = Assume a single uniform block of text
        'tesseract_oem': 3,  # 3 = Both legacy and LSTM model
        'tesseract_lang': 'ron',  # Romanian language code
        'min_confidence': 0.5,  # Reject results below 50%
        'easyocr_gpu': False,  # Set to True if NVIDIA GPU available
        'easyocr_languages': ['ro', 'en'],  # Romanian and English
    }
    
    # === IMAGE PREPROCESSING ===
    PREPROCESSING = {
        'resize_max_height': 1200,
        'resize_max_width': 1600,
        'auto_rotate': True,
        'remove_shadows': True,
        'clahe_clip_limit': 3.0,
        'clahe_tile_size': 8,
        'adaptive_contrast': True,
        'denoise_bilateral': True,
        'bilateral_diameter': 9,
        'sharpen_text': True,
        'binarization_methods': ['adaptive_gaussian', 'adaptive_mean', 'otsu']
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
    
    # === BENCHMARK SETTINGS ===
    BENCHMARK = {
        'output_dir': 'benchmark_results',
        'graph_dpi': 300,
        'generate_latex': True,
        'generate_graphs': True,
    }
    
    # === THESIS REPORT SETTINGS ===
    THESIS = {
        'output_dir': 'thesis_results',
        'include_debug_images': False,
        'include_raw_data': True,
        'min_invoices_for_analysis': 20,
    }
    
    # === GOOGLE CLOUD & 1C API ===
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    ONE_C_API_URL = os.getenv('ONE_C_API_URL')
    ONE_C_USERNAME = os.getenv('ONE_C_USERNAME')
    ONE_C_PASSWORD = os.getenv('ONE_C_PASSWORD')
    
    # === LOGGING ===
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # === WEB APP SETTINGS ===
    UPLOAD_FOLDER = 'uploads'
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}