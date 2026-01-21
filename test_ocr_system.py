#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test and Example Script - OCR System
Run this to verify everything works correctly
"""

import os
import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test if all imports work"""
    print("="*60)
    print("TEST 1: Imports")
    print("="*60)
    
    try:
        import cv2
        print("✓ OpenCV")
    except ImportError as e:
        print(f"✗ OpenCV: {e}")
        return False
    
    try:
        import easyocr
        print("✓ EasyOCR")
    except ImportError as e:
        print(f"✗ EasyOCR: {e}")
        return False
    
    try:
        import pytesseract
        print("✓ Pytesseract")
    except ImportError as e:
        print(f"✗ Pytesseract: {e}")
        return False
    
    try:
        import pandas
        print("✓ Pandas")
    except ImportError as e:
        print(f"✗ Pandas: {e}")
        return False
    
    try:
        import matplotlib
        print("✓ Matplotlib")
    except ImportError as e:
        print(f"✗ Matplotlib: {e}")
        return False
    
    try:
        import torch
        print("✓ PyTorch")
    except ImportError as e:
        print(f"✗ PyTorch: {e}")
        return False
    
    print("\n✓ All imports successful!\n")
    return True


def test_tesseract():
    """Test Tesseract installation"""
    print("="*60)
    print("TEST 2: Tesseract OCR")
    print("="*60)
    
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Setează calea către Tesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Verifică versiune
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract version: {version}")
        
        # Test pe imagine
        img = Image.new('RGB', (200, 50), color='white')
        text = pytesseract.image_to_string(img)
        print("✓ Tesseract processing works")
        
    except FileNotFoundError:
        print("✗ Tesseract not found")
        print("  → Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("✓ Tesseract test passed!\n")
    return True


def test_easyocr():
    """Test EasyOCR"""
    print("="*60)
    print("TEST 3: EasyOCR")
    print("="*60)
    
    try:
        import easyocr
        import numpy as np
        
        print("Initializing EasyOCR reader...")
        print("(First time downloads models, ~500MB)")
        
        reader = easyocr.Reader(['ro', 'en'], gpu=False, verbose=False)
        print("✓ EasyOCR initialized")
        
        # Create dummy image
        img = np.zeros((50, 200, 3), dtype=np.uint8)
        
        print("Processing test image...")
        results = reader.readtext(img)
        print("✓ EasyOCR processing works")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("✓ EasyOCR test passed!\n")
    return True


def test_ocr_processor():
    """Test OCR Processor"""
    print("="*60)
    print("TEST 4: OCR Processor")
    print("="*60)
    
    try:
        from advanced_ocr_processor import IntelligentOCRProcessor
        
        print("Initializing OCR Processor...")
        processor = IntelligentOCRProcessor(save_debug=False)
        print("✓ OCR Processor initialized")
        
        # List test images
        test_images = [f for f in os.listdir('.') if f.endswith(('.jpg', '.png'))]
        
        if test_images:
            print(f"\nFound {len(test_images)} test image(s)")
            img = test_images[0]
            print(f"Processing: {img}")
            
            result = processor.process_invoice(img)
            
            print(f"✓ OCR Engine: {result['ocr_engine']}")
            print(f"✓ Confidence: {result['ocr_confidence']:.2%}")
            print(f"✓ Invoice Number: {result['extracted_fields']['invoice_number']}")
            print(f"✓ Date: {result['extracted_fields']['invoice_date']}")
            print(f"✓ IDNO: {result['extracted_fields']['idno']}")
            print(f"✓ Amount: {result['extracted_fields']['total_amount']}")
        else:
            print("⚠ No test images found (create some for full test)")
            print("  Supported formats: .jpg, .png")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✓ OCR Processor test passed!\n")
    return True


def test_benchmark():
    """Test Benchmark System"""
    print("="*60)
    print("TEST 5: Benchmark System")
    print("="*60)
    
    try:
        from ocr_benchmark_system import OCRBenchmark
        
        print("Initializing Benchmark system...")
        benchmark = OCRBenchmark(output_dir='test_results')
        print("✓ Benchmark initialized")
        
        # Check directories created
        dirs = [
            'test_results',
            'test_results/graphs',
            'test_results/reports',
            'test_results/latex_tables'
        ]
        
        for d in dirs:
            if os.path.exists(d):
                print(f"✓ Directory created: {d}")
            else:
                print(f"✗ Directory missing: {d}")
                return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✓ Benchmark system test passed!\n")
    return True


def show_system_info():
    """Display system information"""
    print("="*60)
    print("SYSTEM INFORMATION")
    print("="*60)
    
    import platform
    import numpy as np
    
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"NumPy: {np.__version__}")
    
    try:
        import cv2
        print(f"OpenCV: {cv2.__version__}")
    except:
        print("OpenCV: Not installed")
    
    try:
        import torch
        print(f"PyTorch: {torch.__version__}")
        print(f"CUDA Available: {torch.cuda.is_available()}")
    except:
        print("PyTorch: Not installed")
    
    try:
        import easyocr
        print(f"EasyOCR: Installed")
    except:
        print("EasyOCR: Not installed")
    
    print()


def create_example_ground_truth():
    """Create example ground truth"""
    print("="*60)
    print("CREATING EXAMPLE GROUND TRUTH")
    print("="*60)
    
    try:
        from create_ground_truth_template import create_ground_truth_template
        
        # Create test directories
        os.makedirs('test_invoices/good', exist_ok=True)
        
        # Create template
        create_ground_truth_template(
            invoices_dir='test_invoices',
            output_csv='example_ground_truth.csv'
        )
        
        print("\n✓ Example ground truth created: example_ground_truth.csv")
        print("  Next: Fill with real data and run benchmark")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  OCR SYSTEM - TEST SUITE".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print()
    
    # Show system info
    show_system_info()
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Tesseract", test_tesseract),
        ("EasyOCR", test_easyocr),
        ("OCR Processor", test_ocr_processor),
        ("Benchmark", test_benchmark),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"✗ TEST FAILED: {name}")
            print(f"  Error: {e}")
            results[name] = False
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.\n")
        
        # Offer to create example
        print("Next steps:")
        print("1. Run: python create_ground_truth_template.py")
        print("2. Place invoice images in test_invoices/ folders")
        print("3. Fill ground_truth.csv with real data")
        print("4. Run: python quick_benchmark_demo.py")
        print("5. Check results in thesis_results/ folder")
        
    else:
        print("\n⚠️  Some tests failed. Review the output above.\n")
        print("Troubleshooting:")
        print("- Check INSTALLATION_GUIDE.md for setup help")
        print("- Verify Tesseract is installed: C:\\Program Files\\Tesseract-OCR")
        print("- Run: pip install -r requirements.txt --upgrade")
    
    print()
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
