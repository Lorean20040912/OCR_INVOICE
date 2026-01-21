#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple OCR for invoices - Tesseract only
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

class SimpleOCR:
    def __init__(self):
        self.debug = True
    
    def preprocess(self, image):
        """Preprocess image with multiple techniques"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Try multiple preprocessing approaches
        results = {}
        
        # 1. Basic median blur + CLAHE
        gray1 = cv2.medianBlur(gray, 3)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray1 = clahe.apply(gray1)
        results['basic'] = gray1
        
        # 2. Bilateral filter (preserves edges)
        gray2 = cv2.bilateralFilter(gray, 9, 75, 75)
        gray2 = clahe.apply(gray2)
        results['bilateral'] = gray2
        
        # 3. Invert if dark background
        if cv2.mean(gray)[0] < 127:
            gray3 = cv2.bitwise_not(gray)
            gray3 = cv2.medianBlur(gray3, 3)
            gray3 = clahe.apply(gray3)
            results['inverted'] = gray3
        
        # 4. Threshold (Otsu)
        _, gray4 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        results['otsu'] = gray4
        
        # 5. Adaptive threshold
        gray5 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
        results['adaptive'] = gray5
        
        return results
    
    def extract_text(self, image_path):
        """Extract text from invoice - try all preprocessing methods"""
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        preprocess_methods = self.preprocess(image)
        
        best_text = ""
        best_length = 0
        
        # Try each preprocessing method
        for method_name, gray in preprocess_methods.items():
            config = '--psm 6 --oem 3 -l ron'
            text = pytesseract.image_to_string(gray, config=config)
            
            if len(text.strip()) > best_length:
                best_length = len(text.strip())
                best_text = text
        
        return best_text
    
    def extract_fields(self, text):
        """Extract key fields"""
        fields = {
            'invoice_number': None,
            'date': None,
            'contractor': None,
            'amount': None
        }
        
        # Split text into lines for processing
        lines = text.split('\n')
        
        # Invoice number - look for alphanumeric patterns (aax5062751, 22x5082751, etc)
        for line in lines:
            # Look for letter+number combinations
            match = re.search(r'([a-z0-9]{8,})', line, re.IGNORECASE)
            if match:
                inv = match.group(1).strip()
                if re.search(r'[a-z].*\d', inv, re.IGNORECASE):  # Must have letters AND numbers
                    fields['invoice_number'] = inv
                    break
        
        # Date - FIRST date only (format: DD.MM.YYYY or DD/MM/YYYY)
        for line in lines:
            match = re.search(r'([0-9]{1,2}[\.\/][0-9]{1,2}[\.\/][0-9]{4})', line)
            if match:
                date_str = match.group(1).strip()
                # Check if it's a valid date in 2026
                if '2026' in date_str or '2025' in date_str or '2024' in date_str:
                    fields['date'] = date_str
                    break
        
        # Total amount - look for the TOTAL line
        for line in lines:
            # Match patterns like "TOTAL: 592.82 lei" or "592.82"
            match = re.search(r'(?:TOTAL|Total)[:\s]*([0-9]+[\.][0-9]{2})\s*(?:lei)?', line, re.IGNORECASE)
            if match:
                fields['amount'] = match.group(1).strip()
                break
        
        # Fallback: if no TOTAL found, look for any amount with lei
        if not fields['amount']:
            for line in lines:
                match = re.search(r'([0-9]{2,}[\.][0-9]{2})\s*lei', line, re.IGNORECASE)
                if match:
                    amount = match.group(1).strip()
                    # Check if it looks like 592.82 (over 100)
                    if float(amount) > 100:
                        fields['amount'] = amount
                        break
        
        # Contractor - look for company names
        contractor_patterns = [
            r'(?:Contractor|Contactor|Contragent)[:\s]+([A-Z\s\.]+)',
            r'T\.D\s+GROUP',
            r'([A-Z][A-Z\s\.]+(?:SRL|SA|GROUP|Ltd))',
        ]
        
        for pattern in contractor_patterns:
            for line in lines:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    contractor = match.group(1) if '(' in pattern else match.group(0)
                    if len(contractor.strip()) > 3:
                        fields['contractor'] = contractor.strip()
                        break
            if fields['contractor']:
                break
        
        return fields
    
    def process(self, image_path):
        """Process invoice"""
        text = self.extract_text(image_path)
        if not text:
            print("Failed to extract text")
            return None
        
        fields = self.extract_fields(text)
        
        return {
            'path': image_path,
            'text': text,
            'fields': fields
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python ocr_simple.py <image_path>")
        print("\nExample:")
        print("  python ocr_simple.py test_invoices/good_quality/your_invoice.jpg.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        sys.exit(1)
    
    ocr = SimpleOCR()
    result = ocr.process(image_path)
    
    if result:
        print("\n" + "="*60)
        print("EXTRACTED TEXT:")
        print("="*60)
        try:
            print(result['text'])
        except:
            # Handle encoding issues
            print(result['text'].encode('utf-8', errors='replace').decode('utf-8'))
        print("\n" + "="*60)
        print("EXTRACTED FIELDS:")
        print("="*60)
        for key, value in result['fields'].items():
            print(f"{key:20} : {value}")
        print("="*60)
        print("\nSuccess!")
    else:
        print("Failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
