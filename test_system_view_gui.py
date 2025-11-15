#!/usr/bin/env python3
"""
Test script for system view integration with components.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.system_view import SystemView
from system.components import ComponentManager, APIServer, DatabaseServer, MQTTBroker
from simulation.engine import SimulationEngine

def test_system_view():
    """Test the system view with component integration."""
    print("Testing System View with Components...")
    
    # Create root window
    root = tk.Tk()
    root.title("System View Test")
    root.geometry("1200x800")
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Create system view
    system_view = SystemView(root, engine)
    system_view.frame.pack(fill=tk.BOTH, expand=True)
    
    # Test component manager integration
    print(f"Component manager has {len(system_view.component_manager.components)} components")
    for comp_id, comp in system_view.component_manager.components.items():
        print(f"  - {comp_id}: {comp.name}")
    
    # Add a label with instructions
    info_label = ttk.Label(root, text="System View Test - Check the System View tab for components")
    info_label.pack(pady=5)
    
    # Create test buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)
    
    def start_all():
        system_view.start_all_components()
        print("Started all components")
    
    def stop_all():
        system_view.stop_all_components()
        print("Stopped all components")
    
    def refresh():
        system_view.refresh_diagram()
        print("Refreshed diagram")
    
    ttk.Button(button_frame, text="Start All Components", command=start_all).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Stop All Components", command=stop_all).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Refresh Diagram", command=refresh).pack(side=tk.LEFT, padx=5)
    
    # Start the GUI
    print("Starting GUI... Close the window to exit.")
    root.mainloop()

if __name__ == "__main__":
    print("System View Integration Test")
    print("=" * 50)
    
    try:
        test_system_view()
        print("Test completed.")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()