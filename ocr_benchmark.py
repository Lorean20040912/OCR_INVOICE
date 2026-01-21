#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Benchmarking System for Thesis
Compare: Tesseract vs EasyOCR vs Advanced
"""

import os
import json
import csv
import cv2
import numpy as np
import pytesseract
import easyocr
from pathlib import Path
from typing import Dict, List
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Tesseract
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class SimpleOCRBenchmark:
    """Simple Tesseract only"""
    
    def __init__(self):
        pass
    
    def process(self, image_path: str) -> Dict:
        """Tesseract only OCR"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'Cannot read image'}
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray, config='--psm 6 --oem 3')
            
            data = pytesseract.image_to_data(gray, config='--psm 6 --oem 3',
                                            output_type=pytesseract.Output.DICT)
            conf = np.mean([int(c) for c in data['conf'] if int(c) > 0]) / 100 if data['conf'] else 0
            
            return {
                'engine': 'Tesseract',
                'text': text,
                'confidence': float(conf)
            }
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return {'error': str(e)}


class EasyOCRBenchmark:
    """EasyOCR only"""
    
    def __init__(self):
        try:
            self.reader = easyocr.Reader(['ro', 'en'], gpu=False, verbose=False)
            logger.info("✓ EasyOCR initialized")
        except Exception as e:
            logger.warning(f"EasyOCR init: {e}")
            self.reader = None
    
    def process(self, image_path: str) -> Dict:
        """EasyOCR extraction"""
        if not self.reader:
            return {'error': 'EasyOCR not available'}
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'error': 'Cannot read image'}
            
            results = self.reader.readtext(img, detail=1)
            text = '\n'.join([r[1] for r in results])
            conf = np.mean([r[2] for r in results]) if results else 0
            
            return {
                'engine': 'EasyOCR',
                'text': text,
                'confidence': float(conf)
            }
        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return {'error': str(e)}


class BenchmarkSystem:
    """Compare multiple OCR engines"""
    
    def __init__(self):
        self.tesseract = SimpleOCRBenchmark()
        self.easyocr = EasyOCRBenchmark()
        self.results = []
        self.ground_truth = {}
        self.load_ground_truth()
    
    def load_ground_truth(self):
        """Load ground truth CSV if exists"""
        gt_file = 'ground_truth.csv'
        if os.path.exists(gt_file):
            try:
                with open(gt_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        filename = row.get('filename', '')
                        self.ground_truth[filename] = {
                            'invoice_number': row.get('true_invoice_number'),
                            'date': row.get('true_invoice_date'),
                            'contractor': row.get('true_contractor'),
                            'amount': row.get('true_total_amount')
                        }
                logger.info(f"✓ Loaded {len(self.ground_truth)} ground truth entries")
            except Exception as e:
                logger.warning(f"Ground truth load error: {e}")
    
    def extract_invoice_number(self, text: str) -> str:
        """Extract invoice number"""
        import re
        for line in text.split('\n'):
            m = re.search(r'([a-z0-9]{8,})', line, re.IGNORECASE)
            if m and re.search(r'[a-z].*\d', m.group(1), re.IGNORECASE):
                return m.group(1).lower().strip()
        return ''
    
    def extract_date(self, text: str) -> str:
        """Extract first date"""
        import re
        for line in text.split('\n'):
            m = re.search(r'([0-9]{1,2}[\.\/][0-9]{1,2}[\.\/][0-9]{4})', line)
            if m and any(y in m.group(1) for y in ['2024', '2025', '2026', '2027']):
                return m.group(1).strip()
        return ''
    
    def extract_amount(self, text: str) -> str:
        """Extract total amount"""
        import re
        for line in text.split('\n'):
            m = re.search(r'(?:TOTAL|Total)[:\s]*([0-9]+[\.][0-9]{2})', line, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return ''
    
    def calculate_accuracy(self, extracted: str, true_value: str) -> float:
        """Calculate accuracy (0-1)"""
        if not true_value:
            return 0.0
        extracted = str(extracted).lower().strip()
        true_value = str(true_value).lower().strip()
        
        if extracted == true_value:
            return 1.0
        
        # Partial match scoring
        if extracted in true_value or true_value in extracted:
            return 0.5
        return 0.0
    
    def benchmark_image(self, image_path: str) -> Dict:
        """Benchmark all engines on single image"""
        logger.info(f"Benchmarking: {Path(image_path).name}")
        
        filename = Path(image_path).name
        gt = self.ground_truth.get(filename, {})
        
        results = {
            'image': filename,
            'path': image_path,
            'timestamp': datetime.now().isoformat(),
            'ground_truth': gt,
            'engines': {}
        }
        
        # Tesseract benchmark
        start = time.time()
        tess_result = self.tesseract.process(image_path)
        tess_time = time.time() - start
        
        if 'error' not in tess_result:
            inv_num = self.extract_invoice_number(tess_result['text'])
            date_val = self.extract_date(tess_result['text'])
            amount_val = self.extract_amount(tess_result['text'])
            
            results['engines']['Tesseract'] = {
                'confidence': tess_result['confidence'],
                'time': tess_time,
                'fields': {
                    'invoice_number': inv_num,
                    'date': date_val,
                    'amount': amount_val
                },
                'accuracy': {
                    'invoice_number': self.calculate_accuracy(inv_num, gt.get('invoice_number', '')),
                    'date': self.calculate_accuracy(date_val, gt.get('date', '')),
                    'amount': self.calculate_accuracy(amount_val, gt.get('amount', ''))
                }
            }
        else:
            results['engines']['Tesseract'] = {'error': tess_result['error']}
        
        # EasyOCR benchmark
        start = time.time()
        easy_result = self.easyocr.process(image_path)
        easy_time = time.time() - start
        
        if 'error' not in easy_result:
            inv_num = self.extract_invoice_number(easy_result['text'])
            date_val = self.extract_date(easy_result['text'])
            amount_val = self.extract_amount(easy_result['text'])
            
            results['engines']['EasyOCR'] = {
                'confidence': easy_result['confidence'],
                'time': easy_time,
                'fields': {
                    'invoice_number': inv_num,
                    'date': date_val,
                    'amount': amount_val
                },
                'accuracy': {
                    'invoice_number': self.calculate_accuracy(inv_num, gt.get('invoice_number', '')),
                    'date': self.calculate_accuracy(date_val, gt.get('date', '')),
                    'amount': self.calculate_accuracy(amount_val, gt.get('amount', ''))
                }
            }
        else:
            results['engines']['EasyOCR'] = {'error': easy_result['error']}
        
        return results
    
    def benchmark_directory(self, image_dir: str) -> List[Dict]:
        """Benchmark all images in directory"""
        results = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        image_files = []
        for ext in image_extensions:
            image_files.extend(Path(image_dir).glob(f'**/*{ext}'))
            image_files.extend(Path(image_dir).glob(f'**/*{ext.upper()}'))
        
        logger.info(f"Found {len(image_files)} images")
        
        for img_path in sorted(set(image_files)):
            if img_path.is_file():
                result = self.benchmark_image(str(img_path))
                results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict], output_file: str = 'benchmark_report.json'):
        """Generate benchmark report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_images': len(results),
            'summary': self._calculate_summary(results),
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Report saved: {output_file}")
        self._print_summary(report['summary'])
    
    def _calculate_summary(self, results: List[Dict]) -> Dict:
        """Calculate summary statistics"""
        summary = {
            'Tesseract': {'avg_conf': 0, 'avg_time': 0, 'accuracy': {}},
            'EasyOCR': {'avg_conf': 0, 'avg_time': 0, 'accuracy': {}}
        }
        
        tess_confs, easy_confs = [], []
        tess_times, easy_times = [], []
        
        for result in results:
            engines = result.get('engines', {})
            
            if 'Tesseract' in engines and 'error' not in engines['Tesseract']:
                tess = engines['Tesseract']
                tess_confs.append(tess.get('confidence', 0))
                tess_times.append(tess.get('time', 0))
            
            if 'EasyOCR' in engines and 'error' not in engines['EasyOCR']:
                easy = engines['EasyOCR']
                easy_confs.append(easy.get('confidence', 0))
                easy_times.append(easy.get('time', 0))
        
        if tess_confs:
            summary['Tesseract']['avg_conf'] = float(np.mean(tess_confs))
            summary['Tesseract']['avg_time'] = float(np.mean(tess_times))
        
        if easy_confs:
            summary['EasyOCR']['avg_conf'] = float(np.mean(easy_confs))
            summary['EasyOCR']['avg_time'] = float(np.mean(easy_times))
        
        return summary
    
    def _print_summary(self, summary: Dict):
        """Print summary"""
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        
        for engine, stats in summary.items():
            if 'error' not in stats:
                print(f"\n{engine}:")
                print(f"  Avg Confidence: {stats.get('avg_conf', 0):.2%}")
                print(f"  Avg Time:       {stats.get('avg_time', 0):.2f}s")
        
        print("\n" + "="*70)


if __name__ == '__main__':
    bench = BenchmarkSystem()
    
    # Benchmark test directory
    results = bench.benchmark_directory('test_invoices')
    
    # Generate report
    bench.generate_report(results)
