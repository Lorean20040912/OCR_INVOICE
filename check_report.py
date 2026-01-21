import json

data = json.load(open('ocr_report.json'))

print(f"Total processed: {data['total_processed']}")
print(f"Successful: {data['successful']}")
print("\nResults:")
print("="*80)

for r in data['results']:
    path = r.get('path', '').split('\\')[-1]
    inv = r.get('invoice_number', 'N/A')
    date = r.get('date', 'N/A')
    amount = r.get('amount', 'N/A')
    print(f"{path:40} | INV: {str(inv):15} | DATE: {str(date):12} | AMOUNT: {str(amount)}")

print("="*80)
