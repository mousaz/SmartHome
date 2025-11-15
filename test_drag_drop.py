#!/usr/bin/env python3
"""
Test script for drag-and-drop and connection arrows in system view.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.system_view import SystemView
from simulation.engine import SimulationEngine
import logging

def test_drag_and_connections():
    """Test drag-and-drop and connection arrows functionality."""
    print("Testing System View Drag and Drop with Connection Arrows...")
    
    # Create root window
    root = tk.Tk()
    root.title("System View Drag & Drop Test")
    root.geometry("1400x900")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Create system view
    system_view = SystemView(root, engine, logger)
    system_view.frame.pack(fill=tk.BOTH, expand=True)
    
    # Add information label
    info_frame = ttk.Frame(root)
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    info_text = """
    Drag & Drop Test Instructions:
    1. Try clicking and dragging the system components (API Server, Database, MQTT Broker)
    2. Observe the connection arrows between components
    3. Notice how arrows update when you move components
    4. Right-click components for context menu options
    5. Use toolbar buttons to start/stop components
    """
    
    info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
    info_label.pack(anchor=tk.W)
    
    # Create control buttons for testing
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)
    
    def refresh_diagram():
        system_view.refresh_diagram()
        print("Diagram refreshed")
    
    def toggle_api_server():
        api_component = system_view.component_manager.components.get('api_server')
        if api_component:
            if api_component.status.value == 'stopped':
                system_view.start_component('api_server')
                print("Started API Server")
            else:
                system_view.stop_component('api_server')
                print("Stopped API Server")
    
    def add_test_controller():
        system_view.add_controller('filter')
        print("Added test controller")
    
    ttk.Button(button_frame, text="Refresh Diagram", command=refresh_diagram).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Toggle API Server", command=toggle_api_server).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Add Controller", command=add_test_controller).pack(side=tk.LEFT, padx=5)
    
    # Display component info
    status_frame = ttk.LabelFrame(root, text="Component Status", padding="10")
    status_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def update_status():
        status_text = ""
        for comp_id, comp in system_view.component_manager.components.items():
            pos = system_view.canvas_components.get(comp_id, {}).get('position', (0, 0))
            status_text += f"{comp.name}: {comp.status.value} at {pos}\n"
        
        status_label.config(text=status_text)
        root.after(2000, update_status)  # Update every 2 seconds
    
    status_label = ttk.Label(status_frame, text="Loading...", justify=tk.LEFT)
    status_label.pack(anchor=tk.W)
    
    # Start status updates
    update_status()
    
    print("GUI started. Test the drag and drop functionality!")
    print("- Drag components around the canvas")
    print("- Watch connection arrows update automatically")
    print("- Right-click components for options")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    print("System View Drag & Drop Test")
    print("=" * 50)
    
    try:
        test_drag_and_connections()
        print("Test completed.")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()