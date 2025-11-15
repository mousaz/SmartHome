#!/usr/bin/env python3
"""Simple direct test to load images in home view."""

import tkinter as tk
import json
import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

# Now import
from gui.home_view import HomeView
from log_system.logger import SmartHomeLogger

def main():
    print("🔧 Direct Image Test")
    print("=" * 30)
    
    # Load template
    templates_path = os.path.join(current_dir, 'templates', 'home_templates.json')
    print(f"📂 Loading templates from: {templates_path}")
    
    try:
        with open(templates_path, 'r') as f:
            templates = json.load(f)
        print(f"✅ Loaded {len(templates)} templates")
    except Exception as e:
        print(f"❌ Error loading templates: {e}")
        return
        
    # Find family house template
    family_template = None
    for key, template in templates.items():
        if 'Family House' in template.get('name', ''):
            family_template = template
            break
    
    if not family_template:
        print("❌ Family House template not found!")
        return
        
    print(f"✅ Found template: {family_template['name']}")
    print(f"📂 Image path: {family_template.get('image', 'No image')}")
    
    # Create GUI
    root = tk.Tk()
    root.title("Direct Image Test")
    root.geometry("900x700")
    
    # Create home view
    logger = SmartHomeLogger()
    
    # Create a mock simulation engine 
    class MockSimEngine:
        def __init__(self):
            pass
    
    sim_engine = MockSimEngine()
    home_view = HomeView(root, sim_engine, logger)
    home_view.frame.pack(fill=tk.BOTH, expand=True)
    
    # Load template after GUI is ready
    def load_template():
        print("🚀 Loading template with debug output...")
        home_view.load_template(family_template)
        
    root.after(500, load_template)
    
    print("🖥️ Starting GUI - watch for debug output...")
    root.mainloop()

if __name__ == "__main__":
    main()