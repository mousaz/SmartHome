#!/usr/bin/env python3
"""Automatic test for image loading - loads template automatically."""

import sys
import os
import tkinter as tk
from tkinter import ttk
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import SmartHomeMainWindow
from src.core.logger import SmartHomeLogger
from src.gui.home_view import HomeView

def auto_load_template():
    """Automatically load a template with an image."""
    try:
        # Load template
        templates_path = os.path.join(os.path.dirname(__file__), 'templates', 'home_templates.json')
        with open(templates_path, 'r') as f:
            templates = json.load(f)
        
        # Find family house template
        family_template = None
        for template in templates:
            if template.get('name') == 'Family House':
                family_template = template
                break
        
        if not family_template:
            print("❌ Family House template not found!")
            return
            
        print(f"✅ Found template: {family_template['name']}")
        print(f"📂 Image path: {family_template.get('image', 'No image')}")
        
        # Create GUI
        root = tk.Tk()
        root.title("Auto Image Test")
        root.geometry("900x700")
        
        # Create home view
        logger = SmartHomeLogger()
        home_view = HomeView(root, logger)
        home_view.pack(fill=tk.BOTH, expand=True)
        
        # Load template after a short delay to ensure GUI is ready
        def load_after_delay():
            print("🚀 Loading template...")
            home_view.load_template(family_template)
            
        root.after(100, load_after_delay)
        
        print("🖥️ Starting GUI...")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Auto Image Loading Test")
    print("=" * 30)
    auto_load_template()