#!/usr/bin/env python3
"""
Test script to verify template images functionality.
"""

import sys
import os
import json
import tkinter as tk
from tkinter import ttk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
    print("✓ PIL/Pillow is available")
except ImportError:
    PIL_AVAILABLE = False
    print("✗ PIL/Pillow is not available")

def test_template_file():
    """Test template JSON file loading."""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'home_templates.json')
    
    print(f"\nTesting template file: {template_path}")
    
    if os.path.exists(template_path):
        print("✓ Template file exists")
        
        try:
            with open(template_path, 'r') as f:
                templates = json.load(f)
            print(f"✓ Template file loaded successfully - {len(templates)} templates found")
            
            for key, template in templates.items():
                print(f"  - {key}: {template.get('name', 'No name')}")
                if 'image' in template:
                    print(f"    Image: {template['image']}")
                else:
                    print(f"    No image specified")
                    
        except Exception as e:
            print(f"✗ Error loading template file: {e}")
    else:
        print("✗ Template file not found")

def test_image_files():
    """Test image file availability."""
    image_dir = os.path.join(os.path.dirname(__file__), 'resources', 'images', 'houses')
    
    print(f"\nTesting image directory: {image_dir}")
    
    if os.path.exists(image_dir):
        print("✓ Image directory exists")
        
        image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
        print(f"✓ Found {len(image_files)} image files")
        
        for img_file in image_files:
            img_path = os.path.join(image_dir, img_file)
            print(f"  - {img_file} ({os.path.getsize(img_path)} bytes)")
            
            if PIL_AVAILABLE:
                try:
                    with Image.open(img_path) as img:
                        print(f"    Size: {img.size}, Mode: {img.mode}")
                except Exception as e:
                    print(f"    ✗ Error loading image: {e}")
    else:
        print("✗ Image directory not found")

def test_template_gui():
    """Test template selection GUI with images."""
    if not PIL_AVAILABLE:
        print("\n✗ Cannot test GUI - PIL not available")
        return
        
    print("\nTesting template selection GUI...")
    
    try:
        from src.log_system.logger import SmartHomeLogger
        from src.gui.templates_dialog import TemplatesDialog
        
        # Create dummy logger
        logger = SmartHomeLogger()
        
        # Create main window
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        # Create templates dialog
        dialog = TemplatesDialog(root, None, logger)
        
        print("✓ Template dialog created successfully")
        print("  Check the dialog window for image preview functionality")
        
        # Run dialog
        selected = dialog.get_selected_template()
        
        if selected:
            print(f"✓ Template selected: {selected.get('name', 'Unknown')}")
            if 'image' in selected:
                print(f"  Image: {selected['image']}")
        else:
            print("✗ No template selected")
            
        root.destroy()
        
    except Exception as e:
        print(f"✗ Error testing GUI: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("Smart Home Template Image Tests")
    print("=" * 40)
    
    test_template_file()
    test_image_files()
    
    # Only run GUI test if explicitly requested
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        test_template_gui()
    else:
        print("\nSkipping GUI test (use --gui to test)")

if __name__ == '__main__':
    main()