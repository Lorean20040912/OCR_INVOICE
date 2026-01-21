"""
OCR Inteligent pentru facturi fotografiate prost
Combină: EasyOCR + Tesseract + Pre-procesare avansată + AI pentru extracție
"""

import cv2
import numpy as np
import easyocr
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IMPORTANT: Configurează calea către Tesseract OCR și TESSDATA_PREFIX
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class AdvancedImagePreprocessor:
    """Pre-procesare avansată pentru imagini de calitate proastă"""
    
    def __init__(self, save_debug=True, debug_dir='debug_preprocessing'):
        self.save_debug = save_debug
        self.debug_dir = debug_dir
        if save_debug:
            os.makedirs(debug_dir, exist_ok=True)
    
    def auto_rotate(self, image: np.ndarray) -> np.ndarray:
        """Detectează și corectează rotația imaginii"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Deteează text orientation usando Tesseract
        try:
            osd = pytesseract.image_to_osd(gray)
            angle = int(osd.split('\n')[2].split(': ')[1])
            
            if angle != 0:
                h, w = image.shape[:2]
                center = (w // 2, h // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                image = cv2.warpAffine(image, rotation_matrix, (w, h),
                                      borderMode=cv2.BORDER_REFLECT)
                logger.info(f"✓ Imagine rotată cu {angle} grade")
        except Exception as e:
            logger.warning(f"Auto-rotație nu s-a putut efectua: {e}")
        
        return image
    
    def remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """Elimină umbrele din imaginea fotografiată"""
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Separă canalele
        l, a, b = cv2.split(result)
        
        # CLAHE pe canal luminozitate
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        result = cv2.merge([l, a, b])
        return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    
    def adaptive_contrast(self, image: np.ndarray) -> np.ndarray:
        """Îmbunătățire contrast adaptivă (CLAHE)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    
    def denoise_advanced(self, image: np.ndarray) -> np.ndarray:
        """Reducere zgomot avansată cu bilateral filter"""
        # Bilateral filter - păstrează muchiile
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        # Non-local means denoise pentru mai multă netezire
        denoised = cv2.fastNlMeansDenoisingColored(denoised, None, h=10, hForColorComponents=10, templateWindowSize=7, searchWindowSize=21)
        return denoised
    
    def sharpen_text(self, image: np.ndarray) -> np.ndarray:
        """Ascuțire text pentru claritate OCR"""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(image, -1, kernel)
        # Blend cu original
        return cv2.addWeighted(image, 0.7, sharpened, 0.3, 0)
    
    def adaptive_binarization(self, image: np.ndarray) -> List[np.ndarray]:
        """Binarizare adaptivă - încearcă 3 metode, returnează toate"""
        # Handle both color and grayscale images
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        results = []
        
        # Metoda 1: Adaptive Gaussian
        binary1 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        results.append(("Adaptive Gaussian", binary1))
        
        # Metoda 2: Adaptive Mean
        binary2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        results.append(("Adaptive Mean", binary2))
        
        # Metoda 3: Otsu
        _, binary3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results.append(("Otsu", binary3))
        
        return results
    
    def preprocess_pipeline(self, image_path: str, save_steps=True) -> np.ndarray:
        """Pipeline complet de pre-procesare"""
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        h, w = image.shape[:2]
        
        # Aggressive resize for memory
        if max(h, w) > 1200:
            scale = 1200 / max(h, w)
            image = cv2.resize(image, None, fx=scale, fy=scale)
        
        steps = {'Original': image.copy()}
        
        # Minimal preprocessing (skip heavy operations)
        # 1. Convert to grayscale + contrast only
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Quick denoise
        gray = cv2.medianBlur(gray, 3)
        
        # 3. Contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        steps['Processed'] = gray
        
        # Salvează pașii (debug)
        if save_steps and self.save_debug:
            base_name = Path(image_path).stem
            for step_name, img in steps.items():
                out_path = os.path.join(self.debug_dir, f'{base_name}_{step_name}.jpg')
                cv2.imwrite(out_path, img)
        
        return gray


class IntelligentOCRProcessor:
    """Procesator OCR inteligent cu combinație de motoare"""
    
    def __init__(self, save_debug=True):
        self.preprocessor = AdvancedImagePreprocessor(save_debug=save_debug)
        self.tesseract_config = '--psm 6 --oem 3 -l ron'
        
        # Inițializează EasyOCR cu limba română
        try:
            self.reader = easyocr.Reader(['ro', 'en'], gpu=False)
            logger.info("✓ EasyOCR inițializat")
        except Exception as e:
            logger.warning(f"EasyOCR error: {e}, va folosi doar Tesseract")
            self.reader = None
    
    def extract_with_tesseract(self, image: np.ndarray) -> Dict:
        """Extrage text cu Tesseract"""
        try:
            # Use config parameter instead of lang (works with pytesseract 0.3.13+)
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            data = pytesseract.image_to_data(image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
            
            confidence = np.mean([int(c) for c in data['conf'] if int(c) > 0])
            
            return {
                'engine': 'Tesseract',
                'text': text,
                'confidence': confidence,
                'raw_data': data
            }
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return {'engine': 'Tesseract', 'text': '', 'confidence': 0, 'error': str(e)}
    
    def extract_with_easyocr(self, image: np.ndarray) -> Dict:
        """Extrage text cu EasyOCR"""
        if not self.reader:
            return {'engine': 'EasyOCR', 'text': '', 'confidence': 0}
        
        try:
            results = self.reader.readtext(image, detail=1)
            
            text_parts = []
            confidences = []
            
            for (bbox, text, conf) in results:
                text_parts.append(text)
                confidences.append(conf)
            
            full_text = '\n'.join(text_parts)
            avg_confidence = np.mean(confidences) if confidences else 0
            
            return {
                'engine': 'EasyOCR',
                'text': full_text,
                'confidence': avg_confidence,
                'details': results
            }
        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return {'engine': 'EasyOCR', 'text': '', 'confidence': 0, 'error': str(e)}
    
    def combine_results(self, tesseract_result: Dict, easyocr_result: Dict) -> Dict:
        """Combină rezultatele din ambele motoare"""
        if tesseract_result['confidence'] > easyocr_result['confidence']:
            return tesseract_result
        else:
            return easyocr_result
    
    def extract_invoice_fields(self, ocr_text: str) -> Dict:
        """Pattern matching inteligent pentru câmpuri de factură"""
        import re
        
        fields = {
            'invoice_number': None,
            'invoice_date': None,
            'contractor': None,
            'idno': None,
            'total_amount': None
        }
        
        # Pattern-uri multiple pentru fiecare câmp
        # Invoice number
        patterns_invoice = [
            r'(?:FACT|Factur|Nr|Invoice|#)\s*[-:]*\s*([A-Z0-9\-/]+)',
            r'([A-Z]{1,3}\d{2,4}[/-]\d{1,6})',
        ]
        
        # Invoice date
        patterns_date = [
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',
            r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',
        ]
        
        # IDNO (13 cifre pentru Moldova)
        patterns_idno = [
            r'\b(\d{13})\b',
            r'IDNO\s*[:=]?\s*(\d{13})',
        ]
        
        # Amount (format: 1250.50 sau 1250,50)
        patterns_amount = [
            r'(?:Total|Subtotal|Suma|Amount)\s*[:=]?\s*([\d,. ]+)',
            r'\b(\d+[.,]\d{2})\s*(?:MDL|RON|EUR|$)\b',
        ]
        
        # Căutare patterns
        for pattern in patterns_invoice:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                fields['invoice_number'] = match.group(1)
                break
        
        for pattern in patterns_date:
            match = re.search(pattern, ocr_text)
            if match:
                fields['invoice_date'] = match.group(0)
                break
        
        for pattern in patterns_idno:
            match = re.search(pattern, ocr_text)
            if match:
                fields['idno'] = match.group(1)
                break
        
        for pattern in patterns_amount:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '.')
                fields['total_amount'] = amount
                break
        
        return fields
    
    def process_invoice(self, image_path: str) -> Dict:
        """Procesează factură completă"""
        logger.info(f"Procesează: {image_path}")
        
        # Pre-procesare
        processed_image = self.preprocessor.preprocess_pipeline(image_path)
        
        # Binarizare adaptivă - încearcă toate metodele
        binary_images = self.preprocessor.adaptive_binarization(processed_image)
        
        best_result = None
        best_confidence = 0
        
        # Testeaza cu fiecare imagine binarizată
        for binary_name, binary_image in binary_images:
            # Tesseract
            tess_result = self.extract_with_tesseract(binary_image)
            
            # EasyOCR
            easy_result = self.extract_with_easyocr(binary_image)
            
            # Selectează cel mai bun
            if tess_result['confidence'] > best_confidence:
                best_confidence = tess_result['confidence']
                best_result = tess_result
                best_result['binarization_method'] = binary_name
            
            if easy_result['confidence'] > best_confidence:
                best_confidence = easy_result['confidence']
                best_result = easy_result
                best_result['binarization_method'] = binary_name
        
        # Extrage câmpuri
        extracted_fields = self.extract_invoice_fields(best_result['text'])
        
        result = {
            'image_path': image_path,
            'ocr_engine': best_result['engine'],
            'ocr_confidence': best_result['confidence'],
            'binarization_method': best_result.get('binarization_method', 'Unknown'),
            'raw_text': best_result['text'],
            'extracted_fields': extracted_fields,
            'timestamp': str(Path(image_path).stat().st_mtime)
        }
        
        logger.info(f"✓ Processare completă - Confidence: {best_result['confidence']:.2%}")
        
        return result


if __name__ == '__main__':
    # Demo
    processor = IntelligentOCRProcessor()
    
    # Testează cu o imagine dacă există
    test_images = [f for f in os.listdir('.') if f.endswith(('.jpg', '.png'))]
    if test_images:
        result = processor.process_invoice(test_images[0])
        print(json.dumps(result, indent=2, ensure_ascii=False))
