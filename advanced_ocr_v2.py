#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesare avansată OCR cu EasyOCR + Tesseract
Versiune optimizată pentru facturi de calitate proastă
"""

import cv2
import numpy as np
import pytesseract
import easyocr
import os
import re
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Tesseract
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class AdvancedPreprocessor:
    """Advanced image preprocessing"""
    
    def __init__(self):
        self.debug_dir = 'debug_advanced'
        os.makedirs(self.debug_dir, exist_ok=True)
    
    def process(self, image_path: str, save_debug=True) -> List[np.ndarray]:
        """Return multiple preprocessed versions"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read: {image_path}")
        
        # Resize if too large
        h, w = img.shape[:2]
        if max(h, w) > 1500:
            scale = 1500 / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        versions = {}
        
        # Version 1: Standard + CLAHE
        v1 = cv2.medianBlur(gray, 3)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        v1 = clahe.apply(v1)
        versions['v1_clahe'] = v1
        
        # Version 2: Bilateral + CLAHE
        v2 = cv2.bilateralFilter(gray, 9, 75, 75)
        v2 = clahe.apply(v2)
        versions['v2_bilateral'] = v2
        
        # Version 3: Otsu threshold
        _, v3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        versions['v3_otsu'] = v3
        
        # Version 4: Adaptive threshold
        v4 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
        versions['v4_adaptive'] = v4
        
        # Version 5: Inverted if dark
        if cv2.mean(gray)[0] < 127:
            v5 = cv2.bitwise_not(gray)
            v5 = cv2.medianBlur(v5, 3)
            v5 = clahe.apply(v5)
            versions['v5_inverted'] = v5
        
        # Save debug if requested
        if save_debug:
            base_name = Path(image_path).stem
            for name, img_data in versions.items():
                out = os.path.join(self.debug_dir, f'{base_name}_{name}.jpg')
                cv2.imwrite(out, img_data)
        
        return list(versions.values())


class AdvancedOCR:
    """Multiple OCR engines combined"""
    
    def __init__(self):
        self.preprocessor = AdvancedPreprocessor()
        
        # Initialize EasyOCR
        try:
            self.reader = easyocr.Reader(['ro', 'en'], gpu=False, verbose=False)
            logger.info("✓ EasyOCR loaded")
        except Exception as e:
            logger.warning(f"EasyOCR failed: {e}")
            self.reader = None
    
    def ocr_easyocr(self, image) -> Dict:
        """EasyOCR extraction"""
        if not self.reader:
            return {'engine': 'EasyOCR', 'text': '', 'conf': 0}
        
        try:
            results = self.reader.readtext(image, detail=1)
            text = '\n'.join([r[1] for r in results])
            conf = np.mean([r[2] for r in results]) if results else 0
            return {'engine': 'EasyOCR', 'text': text, 'conf': float(conf)}
        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return {'engine': 'EasyOCR', 'text': '', 'conf': 0}
    
    def ocr_tesseract(self, image) -> Dict:
        """Tesseract extraction"""
        try:
            text = pytesseract.image_to_string(image, config='--psm 6 --oem 3')
            data = pytesseract.image_to_data(image, config='--psm 6 --oem 3',
                                            output_type=pytesseract.Output.DICT)
            conf = np.mean([int(c) for c in data['conf'] if int(c) > 0]) / 100 if data['conf'] else 0
            return {'engine': 'Tesseract', 'text': text, 'conf': float(conf)}
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return {'engine': 'Tesseract', 'text': '', 'conf': 0}
    
    def extract_fields(self, text: str) -> Dict:
        """Extract fields from text"""
        fields = {
            'invoice_number': None,
            'date': None,
            'contractor': None,
            'amount': None
        }
        
        lines = text.split('\n')
        
        # Invoice number (aax5062751, 22x5082751, etc)
        for line in lines:
            m = re.search(r'([a-z0-9]{8,})', line, re.IGNORECASE)
            if m:
                inv = m.group(1).strip()
                if re.search(r'[a-z].*\d', inv, re.IGNORECASE):
                    fields['invoice_number'] = inv
                    break
        
        # Date (first only)
        for line in lines:
            m = re.search(r'([0-9]{1,2}[\.\/][0-9]{1,2}[\.\/][0-9]{4})', line)
            if m:
                date_str = m.group(1).strip()
                if any(y in date_str for y in ['2024', '2025', '2026', '2027']):
                    fields['date'] = date_str
                    break
        
        # Amount
        for line in lines:
            m = re.search(r'(?:TOTAL|Total)[:\s]*([0-9]+[\.][0-9]{2})\s*(?:lei)?', line, re.IGNORECASE)
            if m:
                fields['amount'] = m.group(1).strip()
                break
        
        # Contractor
        for line in lines:
            m = re.search(r'(?:Contractor|T\.D\s+GROUP)', line, re.IGNORECASE)
            if m:
                fields['contractor'] = m.group(0).strip()
                break
        
        return fields
    
    def process(self, image_path: str) -> Dict:
        """Process invoice with advanced OCR"""
        logger.info(f"Processing: {image_path}")
        
        try:
            # Get multiple preprocessed versions
            versions = self.preprocessor.process(image_path, save_debug=True)
            
            best_text = ""
            best_conf = 0
            best_engine = ""
            all_results = []
            
            # Try each version with both engines
            for version in versions:
                # EasyOCR
                easy_result = self.ocr_easyocr(version)
                all_results.append(easy_result)
                
                if easy_result['conf'] > best_conf and len(easy_result['text'].strip()) > 50:
                    best_conf = easy_result['conf']
                    best_text = easy_result['text']
                    best_engine = 'EasyOCR'
                
                # Tesseract
                tess_result = self.ocr_tesseract(version)
                all_results.append(tess_result)
                
                if tess_result['conf'] > best_conf and len(tess_result['text'].strip()) > 50:
                    best_conf = tess_result['conf']
                    best_text = tess_result['text']
                    best_engine = 'Tesseract'
            
            # Extract fields
            fields = self.extract_fields(best_text)
            
            return {
                'path': image_path,
                'text': best_text,
                'engine': best_engine,
                'confidence': best_conf,
                'fields': fields,
                'all_results': all_results
            }
        
        except Exception as e:
            logger.error(f"Error: {e}")
            return {'error': str(e), 'path': image_path}


if __name__ == '__main__':
    ocr = AdvancedOCR()
    
    test_img = 'test_invoices/user_data/invoice_user_aax5062751.jpg'
    if os.path.exists(test_img):
        result = ocr.process(test_img)
        
        print("\n" + "="*70)
        print("ADVANCED OCR PROCESSOR")
        print("="*70)
        print(f"Best Engine: {result.get('engine')}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        print("\nExtracted Fields:")
        for key, val in result.get('fields', {}).items():
            print(f"  {key:20} : {val}")
        print("="*70)
    else:
        print(f"Test image not found: {test_img}")
