#!/usr/bin/env python3
"""
Test image loading paths and PIL functionality.
"""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_image_paths():
    """Test that image paths are correct."""
    print("Testing Image Paths")
    print("=" * 20)
    
    # Load templates
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'home_templates.json')
    print(f"Template file: {template_path}")
    print(f"Template exists: {os.path.exists(template_path)}")
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            templates = json.load(f)
            
        for name, template in templates.items():
            if 'image' in template:
                image_path = template['image']
                print(f"\n{name}:")
                print(f"  Relative path: {image_path}")
                
                # Calculate full path like the code does
                base_dir = os.path.dirname(__file__)
                full_path = os.path.join(base_dir, image_path)
                print(f"  Full path: {full_path}")
                print(f"  Exists: {os.path.exists(full_path)}")
                
                if os.path.exists(full_path):
                    size = os.path.getsize(full_path)
                    print(f"  Size: {size} bytes")
                    
                    # Test PIL loading
                    try:
                        from PIL import Image
                        with Image.open(full_path) as img:
                            print(f"  PIL size: {img.size}")
                            print(f"  PIL mode: {img.mode}")
                    except Exception as e:
                        print(f"  PIL error: {e}")

def test_base_dir_calculation():
    """Test the base directory calculation used in the code."""
    print("\nTesting Base Directory Calculation")
    print("=" * 35)
    
    # This mimics the calculation in home_view.py
    current_file = __file__
    print(f"Current file: {current_file}")
    
    # Simulate the path calculation: 
    # os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # This goes: file -> src -> gui -> home_view.py, so we need to go up 3 levels
    
    # But our test is in the root, so let's see what happens
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"Calculated base (3 levels up): {base_dir}")
    
    # What we actually want for our test
    actual_base = os.path.dirname(__file__)
    print(f"Actual project root: {actual_base}")
    
    # Test image path
    test_image = "resources/images/houses/2bedroom001.jpg"
    path1 = os.path.join(base_dir, test_image)
    path2 = os.path.join(actual_base, test_image)
    
    print(f"Method 1 path: {path1}")
    print(f"Method 1 exists: {os.path.exists(path1)}")
    print(f"Method 2 path: {path2}")
    print(f"Method 2 exists: {os.path.exists(path2)}")

if __name__ == '__main__':
    test_image_paths()
    test_base_dir_calculation()