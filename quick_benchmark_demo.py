"""
Demo rapid - benchmark pe câteva facturi pentru testare
"""

from ocr_benchmark_system import OCRBenchmark
import pandas as pd
import os


def create_demo_ground_truth(output_file='demo_ground_truth.csv'):
    """Creează ground truth demo pentru testare rapidă"""
    data = [
        {
            'invoice_id': 'INV_001',
            'filename': 'invoice1.jpg',
            'true_invoice_number': 'FACT-2024-001',
            'true_invoice_date': '2024-01-15',
            'true_contractor': 'SC EXEMPLU SRL',
            'true_idno': '1234567890123',
            'true_total_amount': '1250.50'
        },
        {
            'invoice_id': 'INV_002',
            'filename': 'invoice2.jpg',
            'true_invoice_number': 'F-2024-0042',
            'true_invoice_date': '2024-01-20',
            'true_contractor': 'COMPANIA TEST SA',
            'true_idno': '9876543210987',
            'true_total_amount': '3450.00'
        },
        {
            'invoice_id': 'INV_003',
            'filename': 'invoice3.jpg',
            'true_invoice_number': 'INV/2024/003',
            'true_invoice_date': '2024-02-10',
            'true_contractor': 'FIRMA DEMO IMPEX',
            'true_idno': '5555555555555',
            'true_total_amount': '2150.75'
        },
    ]
    
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✓ Demo ground truth creat: {output_file}")
    return output_file


def run_demo_benchmark():
    """Rulează demo benchmark"""
    
    print("="*60)
    print("OCR Benchmark - Demo")
    print("="*60)
    
    # Creează demo ground truth
    gt_file = create_demo_ground_truth()
    
    # Verifică dacă exista imagini de test
    demo_images_dir = 'demo_invoices'
    
    if not os.path.exists(demo_images_dir):
        print(f"\n⚠️  Directorul {demo_images_dir} nu există!")
        print(f"   Creează directorul și adaugă imagini de factură pentru test")
        os.makedirs(demo_images_dir, exist_ok=True)
    else:
        # Rulează benchmark
        benchmark = OCRBenchmark(output_dir='demo_results')
        
        try:
            benchmark.run_full_benchmark(
                ground_truth_csv=gt_file,
                images_dir=demo_images_dir
            )
            
            print(f"\n✓ Demo rezultate salvate în: demo_results/")
            print(f"  - Grafice: demo_results/graphs/")
            print(f"  - Rapoarte: demo_results/reports/")
            print(f"  - Tabele LaTeX: demo_results/latex_tables/")
            
        except Exception as e:
            print(f"❌ Eroare în benchmark: {e}")


if __name__ == '__main__':
    run_demo_benchmark()
