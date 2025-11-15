#!/usr/bin/env python3
"""Test sensor dragging on background images."""

import tkinter as tk
import json
import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from gui.home_view import HomeView
from log_system.logger import SmartHomeLogger

# Simple mock sensor class for testing
class MockSensor:
    def __init__(self, sensor_id, name, sensor_type, x, y):
        self.sensor_id = sensor_id
        self.name = name
        self.sensor_type = sensor_type
        self.location = (x, y)
        self.status = MockStatus()
    
    def get_sensor_type(self):
        return self.sensor_type
    
    def set_location(self, x, y):
        self.location = (x, y)
        print(f"🔄 Sensor {self.name} location updated to ({x}, {y})")

class MockStatus:
    def __init__(self):
        self.value = 'active'

class MockSimEngine:
    def __init__(self):
        pass

def main():
    print("🧪 Sensor Dragging Test")
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
    root.title("Sensor Dragging Test")
    root.geometry("900x700")
    
    # Create home view
    logger = SmartHomeLogger()
    sim_engine = MockSimEngine()
    home_view = HomeView(root, sim_engine, logger)
    home_view.frame.pack(fill=tk.BOTH, expand=True)
    
    # Load template after GUI is ready
    def setup_test():
        print("🚀 Setting up test...")
        home_view.load_template(family_template)
        
        # Add some test sensors
        sensors = [
            MockSensor("temp1", "Living Room Temp", "temperature", 200, 150),
            MockSensor("motion1", "Front Door Motion", "motion", 400, 100),
            MockSensor("door1", "Main Door Sensor", "door_window", 350, 300),
            MockSensor("smoke1", "Kitchen Smoke", "smoke", 500, 400),
        ]
        
        for sensor in sensors:
            home_view.add_sensor(sensor)
            print(f"📍 Added sensor: {sensor.name} at {sensor.location}")
        
        print("✅ Test setup complete!")
        print("🖱️ Try dragging the sensors around the image!")
        
    root.after(500, setup_test)
    
    print("🖥️ Starting GUI - sensors will appear shortly...")
    root.mainloop()

if __name__ == "__main__":
    main()