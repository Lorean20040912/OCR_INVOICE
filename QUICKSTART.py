#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUICK START - OCR INVOICE PROCESSOR
Run this for fast invoiceprocessing
"""

import sys
import os

# Setup
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  OCR INVOICE PROCESSOR                       ║
║                     QUICK START GUIDE                        ║
╚══════════════════════════════════════════════════════════════╝

USAGE OPTIONS:

1. Process single invoice:
   .\.venv\Scripts\python.exe ocr_simple.py <image_path>
   
   Example:
   .\.venv\Scripts\python.exe ocr_simple.py test_invoices\test_generated\invoice_test.jpg

2. Process all invoices and create report:
   .\.venv\Scripts\python.exe ocr_batch.py
   
   This creates: ocr_report.json with all extracted data

3. Debug preprocessing (see steps):
   .\.venv\Scripts\python.exe ocr_debug.py <image_path>
   
   Saves debug images to: debug_ocr/

4. Test different PSM modes:
   .\.venv\Scripts\python.exe ocr_psm.py <image_path>

5. Generate test invoice:
   .\.venv\Scripts\python.exe generate_invoice.py

═══════════════════════════════════════════════════════════════

SUPPORTED FEATURES:
✓ Romanian language OCR
✓ Multiple preprocessing techniques
✓ Invoice number extraction (INV-2026-001)
✓ Date extraction (21.01.2026)
✓ Amount extraction (1250.00)
✓ Batch processing
✓ JSON report generation

REQUIREMENTS:
✓ Tesseract OCR 5.5.0 installed
✓ Python 3.14 with virtual environment
✓ OpenCV, Tesseract, PIL packages

════════════════════════════════════════════════════════════════
""")

if __name__ == '__main__':
    main()
