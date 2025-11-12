#!/usr/bin/env python3
"""
Diagnostic script to check image loading in home view.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
    print("✓ PIL is available")
except ImportError:
    PIL_AVAILABLE = False
    print("✗ PIL not available")

def test_direct_image_loading():
    """Test loading images directly."""
    print("\n=== Direct Image Loading Test ===")
    
    # Test paths
    project_root = os.path.dirname(__file__)
    image_path = os.path.join(project_root, 'resources', 'images', 'houses', '2bedroom001.jpg')
    
    print(f"Project root: {project_root}")
    print(f"Image path: {image_path}")
    print(f"Image exists: {os.path.exists(image_path)}")
    
    if PIL_AVAILABLE and os.path.exists(image_path):
        try:
            # Test loading with PIL
            with Image.open(image_path) as img:
                print(f"✓ PIL can load image: {img.size}, {img.mode}")
                
                # Test creating PhotoImage
                img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                print(f"✓ PhotoImage created successfully")
                return True
                
        except Exception as e:
            print(f"✗ Error loading image: {e}")
            return False
    
    return False

def test_template_loading():
    """Test template loading with image paths."""
    print("\n=== Template Loading Test ===")
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'home_templates.json')
    print(f"Template path: {template_path}")
    print(f"Template exists: {os.path.exists(template_path)}")
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            templates = json.load(f)
        
        for name, template in templates.items():
            print(f"\nTemplate: {name}")
            if 'image' in template:
                image_rel_path = template['image']
                print(f"  Image (relative): {image_rel_path}")
                
                # Calculate full path like the code does
                full_path = os.path.join(os.path.dirname(__file__), image_rel_path)
                print(f"  Image (full): {full_path}")
                print(f"  Exists: {os.path.exists(full_path)}")
            else:
                print("  No image")

def test_home_view_image():
    """Test image loading through HomeView."""
    print("\n=== HomeView Image Loading Test ===")
    
    try:
        from src.log_system.logger import SmartHomeLogger
        from src.simulation.engine import SimulationEngine
        from src.gui.home_view import HomeView
        
        # Create minimal setup
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        logger = SmartHomeLogger()
        sim_engine = SimulationEngine(logger)
        
        # Create HomeView
        home_view = HomeView(root, sim_engine, logger)
        
        # Load a template with image
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'home_templates.json')
        with open(template_path, 'r') as f:
            templates = json.load(f)
        
        # Try family_house template
        if 'family_house' in templates:
            template = templates['family_house']
            print(f"Loading template: {template.get('name', 'Unknown')}")
            print(f"Template image: {template.get('image', 'None')}")
            
            # Load template
            home_view.load_template(template)
            
            # Check if image was loaded
            if hasattr(home_view, 'background_image_id') and home_view.background_image_id:
                print("✓ Background image ID exists")
                print(f"  Image ID: {home_view.background_image_id}")
                
                # Check if PhotoImage exists
                if hasattr(home_view, 'background_photo') and home_view.background_photo:
                    print("✓ PhotoImage object exists")
                else:
                    print("✗ PhotoImage object missing")
                    
            else:
                print("✗ No background image ID found")
        
        root.destroy()
        
    except Exception as e:
        print(f"✗ HomeView test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Smart Home Image Diagnostic")
    print("=" * 30)
    
    test_direct_image_loading()
    test_template_loading()
    test_home_view_image()