#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate test invoice with user's data
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_user_invoice():
    """Create invoice matching user's real data"""
    
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to get fonts
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_normal = ImageFont.truetype("arial.ttf", 14)
        font_small = ImageFont.truetype("arial.ttf", 12)
        font_barcode = ImageFont.truetype("courier.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_barcode = ImageFont.load_default()
    
    y = 50
    
    # Company header
    draw.text((50, y), "T.D GROUP", fill='black', font=font_large)
    y += 40
    draw.text((50, y), "Company Information", fill='black', font=font_small)
    y += 25
    
    # Line
    draw.line([(50, y), (width-50, y)], fill='black', width=2)
    y += 30
    
    # Invoice title
    draw.text((250, y), "FACTURA", fill='black', font=font_large)
    y += 50
    
    # Invoice number - will be under barcode
    draw.text((50, y), "Numar Factura:", fill='black', font=font_normal)
    y += 35
    
    # Barcode representation
    draw.rectangle([(50, y), (300, y+50)], outline='black', width=2)
    draw.text((60, y+15), "|||||||||||||||", fill='black', font=font_barcode)
    y += 60
    
    # Invoice number under barcode
    draw.text((50, y), "aax5062751", fill='black', font=font_normal)
    y += 35
    
    # Date - CLEARER
    draw.text((50, y), "Data emiterii: 21.01.2026", fill='black', font=font_normal)
    y += 30
    
    draw.text((50, y), "Data scadentei: 31.01.2027", fill='black', font=font_normal)
    y += 50
    
    # Line
    draw.line([(50, y), (width-50, y)], fill='black', width=1)
    y += 30
    
    # Table header
    draw.text((50, y), "Descriere", fill='black', font=font_normal)
    draw.text((400, y), "Cantitate", fill='black', font=font_normal)
    draw.text((550, y), "Pret", fill='black', font=font_normal)
    y += 30
    
    draw.line([(50, y), (width-50, y)], fill='black', width=1)
    y += 30
    
    # Items
    draw.text((50, y), "Servicii profesionale", fill='black', font=font_small)
    draw.text((400, y), "2", fill='black', font=font_small)
    draw.text((550, y), "250.00", fill='black', font=font_small)
    y += 35
    
    draw.text((50, y), "Consultanta", fill='black', font=font_small)
    draw.text((400, y), "1", fill='black', font=font_small)
    draw.text((550, y), "92.82", fill='black', font=font_small)
    y += 50
    
    # Line
    draw.line([(50, y), (width-50, y)], fill='black', width=2)
    y += 30
    
    # Total - AT BOTTOM - VERY CLEAR
    y = height - 150
    draw.line([(50, y), (width-50, y)], fill='black', width=2)
    y += 30
    
    draw.text((50, y), "TOTAL FACTURA: 592.82 lei", fill='black', font=font_large)
    y += 50
    
    # Contractor
    draw.line([(50, y), (width-50, y)], fill='black', width=1)
    y += 20
    draw.text((50, y), "Contractor: T.D GROUP", fill='black', font=font_small)
    
    # Save
    os.makedirs('test_invoices/user_data', exist_ok=True)
    image.save('test_invoices/user_data/invoice_user_aax5062751.jpg')
    print("Created: test_invoices/user_data/invoice_user_aax5062751.jpg")
    print("- Invoice Number: aax5062751")
    print("- Contractor: T.D GROUP")
    print("- Date: 21.01.2026")
    print("- Total: 592.82 lei")

if __name__ == '__main__':
    create_user_invoice()
