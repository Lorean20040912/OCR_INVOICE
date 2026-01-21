#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Ground Truth Template for Thesis Evaluation
"""

import os
import csv
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroundTruthTemplate:
    """Generate ground truth CSV template"""
    
    def __init__(self, output_file: str = 'ground_truth.csv'):
        self.output_file = output_file
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    def find_images(self, search_dir: str = 'test_invoices') -> list:
        """Find all invoice images"""
        images = []
        
        for ext in self.image_extensions:
            images.extend(Path(search_dir).glob(f'**/*{ext}'))
            images.extend(Path(search_dir).glob(f'**/*{ext.upper()}'))
        
        return sorted(set(images))
    
    def create_template(self):
        """Create ground truth CSV template"""
        images = self.find_images()
        
        logger.info(f"Found {len(images)} images")
        
        if not images:
            logger.warning("No images found!")
            return
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'invoice_id',
                'filename',
                'file_path',
                'true_invoice_number',
                'true_invoice_date',
                'true_contractor',
                'true_idno',
                'true_total_amount',
                'notes',
                'quality_level'
            ])
            
            writer.writeheader()
            
            for i, img_path in enumerate(images, 1):
                writer.writerow({
                    'invoice_id': f'INV_{i:03d}',
                    'filename': img_path.name,
                    'file_path': str(img_path),
                    'true_invoice_number': '',  # User fills in
                    'true_invoice_date': '',    # Format: DD.MM.YYYY
                    'true_contractor': '',      # e.g., "T.D GROUP"
                    'true_idno': '',            # 13 digits
                    'true_total_amount': '',    # e.g., "592.82"
                    'notes': '',                # Additional notes
                    'quality_level': ''         # excellent/good/poor/very_poor
                })
        
        logger.info(f"✓ Created: {self.output_file}")
        logger.info(f"  - {len(images)} entries")
        logger.info("  - Please fill in TRUE values from invoice images")
        logger.info("  - This file is used for accuracy evaluation")
        
        self._print_sample()
    
    def _print_sample(self):
        """Print sample format"""
        print("\n" + "="*70)
        print("GROUND TRUTH TEMPLATE CREATED")
        print("="*70)
        print("\nExample format:")
        print("  invoice_id        : INV_001")
        print("  filename          : invoice_user_aax5062751.jpg")
        print("  true_invoice_number: aax5062751")
        print("  true_invoice_date : 21.01.2026")
        print("  true_contractor   : T.D GROUP")
        print("  true_total_amount : 592.82")
        print("  quality_level     : good/poor/very_poor")
        print("\n" + "="*70)


if __name__ == '__main__':
    gt = GroundTruthTemplate()
    gt.create_template()
