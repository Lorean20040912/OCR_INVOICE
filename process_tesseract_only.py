#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Process invoice using Tesseract only (lightweight)
"""

import cv2
import pytesseract
import os
import sys
from pathlib import Path

# Set Tesseract path - REQUIRED for Windows
import os
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_invoice(image_path):
    """Process invoice with Tesseract"""
    
    print(f"📄 Processing: {image_path}")
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to read image: {image_path}")
        return None
    
    print(f"✓ Image size: {image.shape}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print(f"✓ Converted to grayscale")
    
    # Quick preprocessing
    gray = cv2.medianBlur(gray, 3)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    print(f"✓ Applied preprocessing")
    
    # Extract with Tesseract
    try:
        print(f"\n🔍 Running Tesseract OCR...")
        text = pytesseract.image_to_string(gray, config='--psm 6 --oem 3 -l ron', lang='ron')
        
        print(f"\n📝 Extracted Text:")
        print("=" * 50)
        print(text)
        print("=" * 50)
        
        return text
        
    except Exception as e:
        print(f"❌ Tesseract error: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python process_tesseract_only.py <image_path>")
        print("\nExample:")
        print("  python process_tesseract_only.py test_invoices/good_quality/your_invoice.jpg.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        sys.exit(1)
    
    result = process_invoice(image_path)
    
    if result:
        print("\n✅ Success!")
    else:
        print("\n❌ Failed!")
