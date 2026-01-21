"""
Script pentru crearea template-ului de ground truth
Rulează acest script pentru a genera fișierul CSV unde vei introduce datele reale
"""

import pandas as pd
import os
import glob
from pathlib import Path


def create_ground_truth_template(invoices_dir='test_invoices', output_csv='ground_truth.csv'):
    """Creează template CSV pentru ground truth"""
    
    # Găsește toate imaginile
    image_files = []
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    
    if os.path.exists(invoices_dir):
        for ext in extensions:
            image_files.extend(glob.glob(os.path.join(invoices_dir, ext)))
            # Cauta și în subdirectoare
            image_files.extend(glob.glob(os.path.join(invoices_dir, '**', ext), recursive=True))
    
    if not image_files:
        print(f"⚠️  Nu s-au găsit imagini în {invoices_dir}")
        print("   Creez template cu 3 exemplu...")
        image_files = ['example_001.jpg', 'example_002.jpg', 'example_003.jpg']
    else:
        # Sortează și obține doar numele fișierului
        image_files = sorted(image_files)
        image_files = [os.path.basename(f) for f in image_files]
    
    # Creează DataFrame template
    data = []
    for i, filename in enumerate(image_files, 1):
        data.append({
            'invoice_id': f'INV_{i:03d}',
            'filename': filename,
            'true_invoice_number': '',  # Completează manual
            'true_invoice_date': '',    # Format: YYYY-MM-DD (ex: 2024-01-15)
            'true_contractor': '',      # Nume companie (ex: SC EXEMPLU SRL)
            'true_idno': '',           # 13 cifre (ex: 1234567890123)
            'true_total_amount': '',   # Număr cu 2 zecimale (ex: 1250.50)
            'notes': ''                # Observații
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    print(f"✓ Template creat: {output_csv}")
    print(f"  Total facturi găsite: {len(data)}")
    print(f"\n📝 Pașii următori:")
    print(f"  1. Deschide {output_csv} în Excel")
    print(f"  2. Completează datele REALE pentru fiecare factură")
    print(f"  3. Salvează fișierul (Excel va salva automat în format CSV)")
    print(f"  4. Rulează benchmark-ul cu:")
    print(f"     python ocr_benchmark_system.py")


def create_subdirectories_template(base_dir='test_invoices'):
    """Creează structură de subdirectoare pentru diferite calități de imagini"""
    
    subdirs = [
        'excellent_quality',  # Scanate perfect
        'good_quality',       # Foto bună
        'poor_quality',       # Foto proastă
        'very_poor_quality'   # Foto foarte proastă
    ]
    
    os.makedirs(base_dir, exist_ok=True)
    
    for subdir in subdirs:
        dir_path = os.path.join(base_dir, subdir)
        os.makedirs(dir_path, exist_ok=True)
    
    print(f"✓ Structură de directoare creată în {base_dir}:")
    for subdir in subdirs:
        print(f"  └── {subdir}/")
    print(f"\n💡 Plasează facturile în subdirectoarele corespunzătoare")


if __name__ == '__main__':
    import sys
    
    print("="*60)
    print("Ground Truth Template Generator")
    print("="*60)
    
    # Creează subdirectoare
    create_subdirectories_template()
    
    print("\n")
    
    # Creează template CSV
    create_ground_truth_template()
    
    print("\n📊 Format Ground Truth CSV:")
    print("""
invoice_id | filename | true_invoice_number | true_invoice_date | true_contractor | true_idno | true_total_amount | notes
-----------|----------|---------------------|-------------------|-----------------|-----------|-------------------|-------
INV_001    | inv_001.jpg | FACT-2024-001  | 2024-01-15    | SC EXEMPLU SRL  | 1234567890123 | 1250.50    | Factură normală
INV_002    | inv_002.jpg |                |               |                 |               |            | De completat
    """)
