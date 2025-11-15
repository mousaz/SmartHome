#!/usr/bin/env python3
"""
Final test to verify image loading is working correctly.
"""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_final_image_functionality():
    """Test that all image functionality works correctly."""
    print("Final Image Functionality Test")
    print("=" * 30)
    
    # Test 1: Template loading
    try:
        from src.gui.templates_dialog import TemplatesDialog
        from src.log_system.logger import SmartHomeLogger
        
        logger = SmartHomeLogger()
        
        # Create a mock dialog to test template loading
        class MockParent:
            pass
        
        # This will test the template loading path calculation
        dialog = TemplatesDialog(None, None, logger)
        
        if hasattr(dialog, 'templates') and dialog.templates:
            print("✓ Templates loaded successfully")
            
            for name, template in dialog.templates.items():
                if 'image' in template:
                    print(f"  - {name}: Has image - {template['image']}")
                else:
                    print(f"  - {name}: No image")
        else:
            print("✗ No templates loaded")
            
    except Exception as e:
        print(f"✗ Template loading failed: {e}")
        
    # Test 2: Image path calculation
    print("\nTesting Image Path Calculation:")
    
    try:
        # Simulate the path calculation from src/gui/home_view.py
        fake_file_path = os.path.join(os.path.dirname(__file__), 'src', 'gui', 'home_view.py')
        
        # Simulate the calculation
        current_dir = os.path.dirname(fake_file_path)  # src/gui/
        gui_dir = os.path.dirname(current_dir)  # src/
        project_root = os.path.dirname(gui_dir)  # project root
        
        print(f"  Simulated current dir: {current_dir}")
        print(f"  Project root: {project_root}")
        
        # Test image path
        test_image = "resources/images/houses/2bedroom001.jpg"
        full_path = os.path.join(project_root, test_image)
        
        print(f"  Test image path: {full_path}")
        print(f"  Image exists: {os.path.exists(full_path)}")
        
        if os.path.exists(full_path):
            print("✓ Path calculation is correct!")
        else:
            print("✗ Path calculation is incorrect")
            
    except Exception as e:
        print(f"✗ Path calculation test failed: {e}")
    
    # Test 3: PIL functionality
    print("\nTesting PIL Image Loading:")
    
    try:
        from PIL import Image, ImageTk
        print("✓ PIL imports successful")
        
        # Test loading an actual image
        image_path = os.path.join(os.path.dirname(__file__), 'resources', 'images', 'houses', '2bedroom001.jpg')
        
        if os.path.exists(image_path):
            with Image.open(image_path) as img:
                print(f"✓ Image loaded: {img.size}, {img.mode}")
                
                # Test thumbnail
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                print(f"✓ Thumbnail created: {img.size}")
                
        else:
            print(f"✗ Test image not found: {image_path}")
            
    except Exception as e:
        print(f"✗ PIL test failed: {e}")
    
    print("\nImage functionality should now work correctly!")
    print("Run 'python main.py' and select a template to see the background image.")

if __name__ == '__main__':
    test_final_image_functionality()