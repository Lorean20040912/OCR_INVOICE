#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR with different PSM modes
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

def extract_with_psm_modes(image_path):
    """Try different PSM modes"""
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Preprocessing
    gray = cv2.medianBlur(gray, 3)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    # Otsu threshold
    _, gray_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    results = {}
    
    # PSM modes to try
    psm_modes = {
        '3': 'Fully automatic page segmentation, but no OSD',
        '4': 'Assume a single column of text',
        '5': 'Assume a single uniform block of text',
        '6': 'Assume a single uniform block of text',
        '11': 'Sparse text. Find as much text as possible',
        '13': 'Raw line. Treat the image as a single text line'
    }
    
    for psm, description in psm_modes.items():
        config = f'--psm {psm} --oem 3 -l ron'
        try:
            # Try with preprocessed
            text1 = pytesseract.image_to_string(gray, config=config)
            
            # Try with binary
            text2 = pytesseract.image_to_string(gray_binary, config=config)
            
            # Get the longer one
            text = text1 if len(text1) > len(text2) else text2
            
            results[psm] = {
                'description': description,
                'text': text,
                'length': len(text.strip())
            }
        except Exception as e:
            print(f"Error with PSM {psm}: {e}")
    
    return results

def extract_numbers_dates(text):
    """Extract potential dates and numbers"""
    # Find all numbers that look like dates
    date_patterns = [
        r'(\d{1,2}[./\-]\d{1,2}[./\-]\d{4})',
        r'(\d{4}[./\-]\d{1,2}[./\-]\d{1,2})',
        r'(\d{1,2}\.\d{1,2}\.\d{4})',
    ]
    
    numbers = {}
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            numbers.update({f'date_{i}': m for i, m in enumerate(matches)})
    
    # Find amounts
    amount_pattern = r'(\d+[.,]\d{2})'
    amounts = re.findall(amount_pattern, text)
    numbers.update({f'amount_{i}': a for i, a in enumerate(amounts)})
    
    return numbers

def main():
    if len(sys.argv) < 2:
        print("Usage: python ocr_psm.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        sys.exit(1)
    
    results = extract_with_psm_modes(image_path)
    
    if results:
        print("\n" + "="*70)
        print("TESSERACT PSM MODES COMPARISON")
        print("="*70)
        
        # Sort by length
        sorted_results = sorted(results.items(), key=lambda x: x[1]['length'], reverse=True)
        
        for psm, data in sorted_results:
            print(f"\nPSM {psm}: {data['description']}")
            print(f"  Characters: {data['length']}")
            print(f"  Text preview: {data['text'][:100]}")
            
            # Extract numbers
            numbers = extract_numbers_dates(data['text'])
            if numbers:
                print(f"  Extracted numbers/dates:")
                for key, value in list(numbers.items())[:5]:
                    print(f"    {key}: {value}")
        
        print("\n" + "="*70)
        print("BEST RESULT (PSM 6):")
        print("="*70)
        best = results.get('6', {}).get('text', '')
        print(best)
        print("="*70)

if __name__ == '__main__':
    main()
