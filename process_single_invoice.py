#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple OCR Processing Demo
Run this to test the OCR system on your invoice images
"""

import os
import json
import sys
from pathlib import Path

# Set Tesseract path
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from advanced_ocr_processor import IntelligentOCRProcessor


def process_single_invoice(image_path):
    """Process a single invoice image"""
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    print(f"\n{'='*60}")
    print(f"Processing: {image_path}")
    print(f"{'='*60}\n")
    
    try:
        processor = IntelligentOCRProcessor(save_debug=True)
        result = processor.process_invoice(image_path)
        
        print("📊 RESULTS")
        print("-" * 60)
        print(f"OCR Engine: {result['ocr_engine']}")
        print(f"Confidence: {result['ocr_confidence']:.2%}")
        print(f"Binarization: {result['binarization_method']}")
        
        print(f"\n📋 EXTRACTED FIELDS")
        print("-" * 60)
        fields = result['extracted_fields']
        
        print(f"Invoice Number: {fields['invoice_number'] or '(Not found)'}")
        print(f"Invoice Date: {fields['invoice_date'] or '(Not found)'}")
        print(f"Contractor: {fields['contractor'] or '(Not found)'}")
        print(f"IDNO: {fields['idno'] or '(Not found)'}")
        print(f"Total Amount: {fields['total_amount'] or '(Not found)'}")
        
        print(f"\n📄 RAW TEXT (first 500 chars)")
        print("-" * 60)
        print(result['raw_text'][:500])
        
        print(f"\n✅ Processing complete!")
        print(f"Debug images saved in: debug_preprocessing/")
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("\n" + "="*60)
    print("OCR INVOICE PROCESSOR - DEMO")
    print("="*60)
    
    # Check if image path is provided as argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        process_single_invoice(image_path)
    else:
        print("\n📌 Usage:")
        print(r"   .\venv\Scripts\python.exe process_single_invoice.py <image_path>")
        print(f"\n📝 Examples:")
        print(r"   .\venv\Scripts\python.exe process_single_invoice.py invoice.jpg")
        print(r"   .\venv\Scripts\python.exe process_single_invoice.py test_invoices/good_quality/inv_001.jpg")
        
        print(f"\n📋 Available test directories:")
        print(f"   test_invoices/excellent_quality/")
        print(f"   test_invoices/good_quality/")
        print(f"   test_invoices/poor_quality/")
        print(f"   test_invoices/very_poor_quality/")
        
        print(f"\n💡 Steps:")
        print(f"   1. Place your invoice image(s) in one of the directories above")
        print(r"   2. Run: .\venv\Scripts\python.exe process_single_invoice.py <image_path>")
        print(f"   3. Check results above and debug images in debug_preprocessing/")


if __name__ == '__main__':
    main()
