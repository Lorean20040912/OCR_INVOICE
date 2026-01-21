#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch process invoices and create report
"""

import cv2
import pytesseract
import os
import sys
import re
from pathlib import Path
import json
from datetime import datetime

os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCRBatch:
    def __init__(self):
        self.results = []
    
    def process_directory(self, directory):
        """Process all images in directory"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(root, file)
                    result = self.process_image(image_path)
                    self.results.append(result)
                    
                    inv = result.get('invoice_number') or 'N/A'
                    date = result.get('date') or 'N/A'
                    print(f"[{len(self.results)}] {file:40} -> INV: {str(inv):15} | DATE: {str(date)}")
    
    def process_image(self, image_path):
        """Process single image"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'path': image_path, 'error': 'Could not read image'}
            
            # Try multiple preprocessing approaches
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            best_text = ""
            best_length = 0
            
            # 1. Basic median blur + CLAHE
            gray1 = cv2.medianBlur(gray, 3)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray1 = clahe.apply(gray1)
            
            # 2. Bilateral filter
            gray2 = cv2.bilateralFilter(gray, 9, 75, 75)
            gray2 = clahe.apply(gray2)
            
            # 3. Otsu threshold
            _, gray3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 4. Adaptive threshold
            gray4 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
            
            methods = [gray1, gray2, gray3, gray4]
            
            config = '--psm 6 --oem 3 -l ron'
            
            for gray_img in methods:
                text = pytesseract.image_to_string(gray_img, config=config)
                if len(text.strip()) > best_length:
                    best_length = len(text.strip())
                    best_text = text
            
            # Extract fields
            fields = self.extract_fields(best_text)
            fields['path'] = image_path
            fields['raw_text'] = best_text
            
            return fields
        
        except Exception as e:
            return {'path': image_path, 'error': str(e)}
    
    def extract_fields(self, text):
        """Extract key fields"""
        fields = {
            'invoice_number': None,
            'date': None,
            'contractor': None,
            'amount': None
        }
        
        # Invoice number patterns - alphanumeric like aax5062751
        patterns_inv = [
            r'([a-z0-9]{8,})',  # Any alphanumeric sequence 8+ chars
            r'Factur[a\s]+[#\s]*:?\s*([A-Za-z0-9\-/]+)',
            r'(?:NR|Nr|nr)\.?\s*:?\s*([A-Za-z0-9\-/]+)',
        ]
        
        for pattern in patterns_inv:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['invoice_number'] = match.group(1).strip()
                break
        
        # Date patterns - MANY more patterns
        patterns_date = [
            r'(?:Data|Date|Data\s+factur)[\s:]*([0-9]{1,2}[/\.\-][0-9]{1,2}[/\.\-][0-9]{2,4})',
            r'Data\s*:?\s*([0-9]{1,2}[/\.\-][0-9]{1,2}[/\.\-][0-9]{2,4})',
            r'Date\s*:?\s*([0-9]{1,2}[/\.\-][0-9]{1,2}[/\.\-][0-9]{2,4})',
            r'([0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4})',
            r'([0-9]{2}/[0-9]{2}/[0-9]{4})',
            r'([0-9]{4}-[0-9]{2}-[0-9]{2})',
            r'([0-9]{1,2}\s+(?:ian|feb|mar|apr|mai|iun|iul|aug|sep|oct|noi|dec)[a-z]*\s+[0-9]{4})',
            r'\b([0-9]{1,2}[./-][0-9]{1,2}[./-](?:20|19)[0-9]{2})\b',
            r'(\d{1,2}\.\d{1,2}\.\d{4})',
            r'(?:din|din\s+data)\s+([0-9]{1,2}(?:[/\.\-])[0-9]{1,2}(?:[/\.\-])[0-9]{2,4})'
        ]
        
        for pattern in patterns_date:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                if len(date_str) >= 8:
                    fields['date'] = date_str
                    break
        
        # Amount patterns - TOTAL at bottom
        patterns_amount = [
            r'(?:Total|TOTAL)[\s\w]*:?\s*([0-9]+[,\.][0-9]{2})',
            r'([0-9]{3,}[,\.][0-9]{2})\s*(?:lei|LEI)',
            r'(?:Suma|SUMA)[\s\w]*:?\s*([0-9]+[,\.][0-9]{2})',
        ]
        
        for pattern in patterns_amount:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields['amount'] = match.group(1).strip()
                break
        
        return fields
    
    def save_report(self, output_file='ocr_report.json'):
        """Save results to JSON"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_processed': len(self.results),
            'successful': len([r for r in self.results if 'error' not in r or not r.get('error')]),
            'results': self.results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\nReport saved to: {output_file}")
        return report
    
    def print_summary(self):
        """Print summary statistics"""
        print("\n" + "="*70)
        print("OCR BATCH PROCESSING SUMMARY")
        print("="*70)
        
        successful = [r for r in self.results if 'error' not in r or not r.get('error')]
        
        print(f"Total processed: {len(self.results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(self.results) - len(successful)}")
        
        # Count extracted fields
        invoices_found = len([r for r in successful if r.get('invoice_number')])
        dates_found = len([r for r in successful if r.get('date')])
        amounts_found = len([r for r in successful if r.get('amount')])
        
        print(f"\nExtracted fields:")
        print(f"  Invoice numbers: {invoices_found}/{len(successful)} ({100*invoices_found//len(successful) if successful else 0}%)")
        print(f"  Dates: {dates_found}/{len(successful)} ({100*dates_found//len(successful) if successful else 0}%)")
        print(f"  Amounts: {amounts_found}/{len(successful)} ({100*amounts_found//len(successful) if successful else 0}%)")
        
        print("\n" + "="*70)

def main():
    batch = OCRBatch()
    
    # Process directories
    directories = [
        'test_invoices/excellent_quality',
        'test_invoices/good_quality',
        'test_invoices/poor_quality',
        'test_invoices/very_poor_quality',
        'test_invoices/test_generated',
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"\nProcessing: {directory}/")
            batch.process_directory(directory)
    
    # Save and print results
    batch.save_report()
    batch.print_summary()

if __name__ == '__main__':
    main()
