#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resize invoice images to fix memory issues
"""

import cv2
import os
import sys

def resize_image(input_path, output_path, max_width=1500):
    """Resize image to reduce memory usage"""
    try:
        # Read with low resolution first
        img = cv2.imread(input_path, cv2.IMREAD_REDUCED_COLOR_2)
        
        if img is None:
            print(f"❌ Failed to read: {input_path}")
            return False
        
        # Get original size
        height, width = img.shape[:2]
        
        # Calculate new size
        if width > max_width:
            scale = max_width / width
            new_width = max_width
            new_height = int(height * scale)
        else:
            new_width = width
            new_height = height
        
        # Resize
        resized = cv2.resize(img, (new_width, new_height))
        
        # Save
        cv2.imwrite(output_path, resized)
        print(f"✅ Resized: {input_path}")
        print(f"   Size: {width}x{height} → {new_width}x{new_height}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    # Resize all images
    base_dir = "test_invoices"
    
    for quality_dir in os.listdir(base_dir):
        quality_path = os.path.join(base_dir, quality_dir)
        
        if not os.path.isdir(quality_path):
            continue
        
        for filename in os.listdir(quality_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                input_path = os.path.join(quality_path, filename)
                resize_image(input_path, input_path)
    
    print("\n✅ All images resized!")
