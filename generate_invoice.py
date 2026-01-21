#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a test invoice image
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def create_test_invoice():
    """Create a test invoice image"""
    
    # Create white image
    width, height = 800, 1000
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add some noise to make it more realistic
    img_array = np.array(image)
    noise = np.random.normal(0, 5, img_array.shape).astype(np.uint8)
    img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    image = Image.fromarray(img_array)
    draw = ImageDraw.Draw(image)
    
    # Try to get a font
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_normal = ImageFont.truetype("arial.ttf", 14)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y = 50
    
    # Draw invoice header
    draw.text((50, y), "FACTURA", fill='black', font=font_large)
    y += 50
    
    # Company info
    draw.text((50, y), "S.C. EXAMPLE COMPANY S.R.L.", fill='black', font=font_normal)
    y += 30
    draw.text((50, y), "Adresa: Str. Test, nr. 123, Bucuresti", fill='black', font=font_small)
    y += 25
    draw.text((50, y), "CUI: RO12345678", fill='black', font=font_small)
    y += 25
    
    # Line
    draw.line([(50, y), (width-50, y)], fill='black', width=1)
    y += 30
    
    # Invoice details
    draw.text((50, y), "Numar Factura: INV-2026-001", fill='black', font=font_normal)
    y += 30
    draw.text((50, y), "Data Facturii: 21.01.2026", fill='black', font=font_normal)
    y += 30
    draw.text((50, y), "Data Scadentei: 31.01.2026", fill='black', font=font_normal)
    y += 40
    
    # Line
    draw.line([(50, y), (width-50, y)], fill='black', width=1)
    y += 30
    
    # Table header
    draw.text((50, y), "Descriere", fill='black', font=font_normal)
    draw.text((400, y), "Cantitate", fill='black', font=font_normal)
    draw.text((550, y), "Pret Unitar", fill='black', font=font_normal)
    draw.text((700, y), "Total", fill='black', font=font_normal)
    y += 30
    
    # Line
    draw.line([(50, y), (width-50, y)], fill='black', width=1)
    y += 30
    
    # Table items
    draw.text((50, y), "Servicii de consultanta", fill='black', font=font_small)
    draw.text((400, y), "2", fill='black', font=font_small)
    draw.text((550, y), "500.00", fill='black', font=font_small)
    draw.text((700, y), "1000.00", fill='black', font=font_small)
    y += 30
    
    draw.text((50, y), "Software license", fill='black', font=font_small)
    draw.text((400, y), "1", fill='black', font=font_small)
    draw.text((550, y), "250.00", fill='black', font=font_small)
    draw.text((700, y), "250.00", fill='black', font=font_small)
    y += 50
    
    # Totals
    draw.line([(50, y), (width-50, y)], fill='black', width=1)
    y += 20
    
    draw.text((500, y), "Subtotal:", fill='black', font=font_normal)
    draw.text((700, y), "1250.00", fill='black', font=font_normal)
    y += 30
    
    draw.text((500, y), "TVA (19%):", fill='black', font=font_normal)
    draw.text((700, y), "237.50", fill='black', font=font_normal)
    y += 40
    
    draw.line([(50, y), (width-50, y)], fill='black', width=2)
    y += 20
    
    draw.text((500, y), "TOTAL:", fill='black', font=font_large)
    draw.text((700, y), "1487.50 RON", fill='black', font=font_large)
    y += 50
    
    # Footer
    y = height - 150
    draw.line([(50, y), (width-50, y)], fill='black', width=1)
    y += 20
    
    draw.text((50, y), "Contractor: Client Example SRL", fill='black', font=font_small)
    y += 25
    draw.text((50, y), "Bank Details: Banca Example, IBAN RO12 EXMP 0000 0000 0000 0000", fill='black', font=font_small)
    
    # Save
    os.makedirs('test_invoices/test_generated', exist_ok=True)
    image.save('test_invoices/test_generated/invoice_test.jpg')
    print("Created: test_invoices/test_generated/invoice_test.jpg")

if __name__ == '__main__':
    create_test_invoice()
