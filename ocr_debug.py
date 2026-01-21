#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR with debug - save intermediate images
"""

import cv2
import pytesseract
import os
import sys
import re
from pathlib import Path

# Setup Tesseract
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCRDebug:
    def __init__(self, save_debug=True):
        self.save_debug = save_debug
        self.debug_dir = 'debug_ocr'
        if save_debug and not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
    
    def preprocess(self, image, base_name):
        """Preprocess image with multiple techniques"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if self.save_debug:
            cv2.imwrite(f'{self.debug_dir}/{base_name}_00_original_gray.jpg', gray)
        
        # 1. Bilateral filter
        gray1 = cv2.bilateralFilter(gray, 9, 75, 75)
        if self.save_debug:
            cv2.imwrite(f'{self.debug_dir}/{base_name}_01_bilateral.jpg', gray1)
        
        # 2. CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray1 = clahe.apply(gray1)
        if self.save_debug:
            cv2.imwrite(f'{self.debug_dir}/{base_name}_02_clahe.jpg', gray1)
        
        # 3. Otsu threshold
        _, gray2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if self.save_debug:
            cv2.imwrite(f'{self.debug_dir}/{base_name}_03_otsu.jpg', gray2)
        
        # 4. Adaptive threshold
        gray3 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
        if self.save_debug:
            cv2.imwrite(f'{self.debug_dir}/{base_name}_04_adaptive.jpg', gray3)
        
        # 5. Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        gray4 = cv2.morphologyEx(gray2, cv2.MORPH_CLOSE, kernel, iterations=1)
        if self.save_debug:
            cv2.imwrite(f'{self.debug_dir}/{base_name}_05_morph.jpg', gray4)
        
        return {
            'bilateral_clahe': gray1,
            'otsu': gray2,
            'adaptive': gray3,
            'morphology': gray4
        }
    
    def extract_text_with_details(self, image_path):
        """Extract text with details"""
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        base_name = Path(image_path).stem
        preprocess_methods = self.preprocess(image, base_name)
        
        results = {}
        
        config = '--psm 6 --oem 3 -l ron'
        
        for method_name, gray in preprocess_methods.items():
            text = pytesseract.image_to_string(gray, config=config)
            results[method_name] = {
                'text': text,
                'length': len(text.strip()),
                'lines': len([l for l in text.split('\n') if l.strip()])
            }
        
        # Return the one with most text
        best = max(results.items(), key=lambda x: x[1]['length'])
        
        return {
            'best_method': best[0],
            'text': best[1]['text'],
            'all_results': results
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python ocr_debug.py <image_path>")
        print("\nExample:")
        print("  python ocr_debug.py test_invoices/good_quality/your_invoice.jpg.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        sys.exit(1)
    
    ocr = OCRDebug(save_debug=True)
    result = ocr.extract_text_with_details(image_path)
    
    if result:
        print("\n" + "="*60)
        print(f"Best method: {result['best_method']}")
        print("="*60)
        print("EXTRACTED TEXT:")
        print("-"*60)
        print(result['text'][:500])  # First 500 chars
        print("-"*60)
        print(f"\nAll methods:")
        for method, details in result['all_results'].items():
            print(f"  {method:20} - {details['lines']:3} lines, {details['length']:4} chars")
        print(f"\nDebug images saved to: {ocr.debug_dir}/")
        print("="*60)
    else:
        print("Failed!")

if __name__ == '__main__':
    main()
