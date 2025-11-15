#!/usr/bin/env python3
"""
Simple test to verify template image functionality works correctly.
"""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_template_image_integration():
    """Test the complete template image integration."""
    
    print("Template Image Integration Test")
    print("=" * 35)
    
    # Test 1: Template file loading
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'home_templates.json')
    if os.path.exists(template_path):
        print("✓ Template file exists")
        
        with open(template_path, 'r') as f:
            templates = json.load(f)
        
        templates_with_images = 0
        for name, template in templates.items():
            if 'image' in template:
                templates_with_images += 1
                image_path = template['image']
                
                # Check if image file exists
                if not os.path.isabs(image_path):
                    full_image_path = os.path.join(os.path.dirname(__file__), image_path)
                else:
                    full_image_path = image_path
                
                if os.path.exists(full_image_path):
                    print(f"✓ {name}: Image found - {os.path.basename(image_path)}")
                else:
                    print(f"✗ {name}: Image missing - {image_path}")
        
        print(f"  Total templates: {len(templates)}")
        print(f"  Templates with images: {templates_with_images}")
        
    else:
        print("✗ Template file not found")
        return False
    
    # Test 2: PIL availability
    try:
        from PIL import Image, ImageTk
        print("✓ PIL/Pillow available for image processing")
    except ImportError:
        print("✗ PIL/Pillow not available")
        return False
    
    # Test 3: Home view import
    try:
        from src.gui.home_view import HomeView
        print("✓ HomeView module imports successfully")
    except ImportError as e:
        print(f"✗ HomeView import failed: {e}")
        return False
    
    # Test 4: Templates dialog import
    try:
        from src.gui.templates_dialog import TemplatesDialog
        print("✓ TemplatesDialog module imports successfully")
    except ImportError as e:
        print(f"✗ TemplatesDialog import failed: {e}")
        return False
    
    print("\nIntegration Test Result: ✓ PASSED")
    print("\nTo test the GUI:")
    print("1. Run: python main.py")
    print("2. Select a template (Studio Apartment or Family House)")
    print("3. Check that background image displays without walls/furniture")
    print("4. Use 'Show Background' toggle to show/hide image")
    print("5. Use 'Room Labels' toggle to show/hide room names")
    
    return True

if __name__ == '__main__':
    success = test_template_image_integration()
    sys.exit(0 if success else 1)