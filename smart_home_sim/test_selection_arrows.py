#!/usr/bin/env python3
"""
Test script for selection rectangle movement and arrow clearing fixes.
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

def test_selection_and_arrows():
    """Test selection rectangle movement and arrow clearing."""
    print("Testing Selection Rectangle Movement and Arrow Clearing...")
    
    # Create root window
    root = tk.Tk()
    root.title("Selection & Arrow Test")
    root.geometry("1400x900")
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Add some test sensors
    from src.sensors.temperature_sensor import TemperatureSensor
    from src.sensors.motion_sensor import MotionSensor
    
    temp_sensor = TemperatureSensor("temp_test", "Test Temperature")
    motion_sensor = MotionSensor("motion_test", "Test Motion")
    
    engine.add_sensor(temp_sensor)
    engine.add_sensor(motion_sensor)
    
    # Create system view
    system_view = SystemView(root, engine, logger)
    system_view.frame.pack(fill=tk.BOTH, expand=True)
    
    # Add test instructions
    info_frame = ttk.LabelFrame(root, text="Selection & Arrow Test Instructions", padding="10")
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    instructions = """
    🔍 TESTING FIXES FOR:
    
    1. SELECTION RECTANGLE MOVEMENT:
       • Click on a component to select it (red rectangle appears)
       • Drag the selected component around
       • ✅ RED SELECTION RECTANGLE should MOVE with the component
    
    2. ARROW CLEARING:
       • Observe the arrows between components
       • Start dragging any component
       • ✅ ALL ARROWS should DISAPPEAR immediately when drag starts
       • ✅ NEW ARROWS should appear in real-time during drag
    
    3. TEST STEPS:
       • Click API Server (should show red selection rectangle)
       • Drag API Server (rectangle should move with it, arrows should clear/redraw)
       • Click Database (selection should move to database)
       • Drag Database (test selection movement again)
       • Try sensors too
    """
    
    info_label = ttk.Label(info_frame, text=instructions, justify=tk.LEFT, font=('Arial', 9))
    info_label.pack(anchor=tk.W)
    
    # Create test control panel
    control_frame = ttk.LabelFrame(root, text="Test Controls", padding="10")
    control_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def select_api_server():
        system_view.select_component('api_server')
        print("✓ Selected API Server - check if red rectangle appears")
    
    def select_database():
        system_view.select_component('database')
        print("✓ Selected Database - check if selection moves")
    
    def select_temp_sensor():
        system_view.select_component('temp_test')
        print("✓ Selected Temperature Sensor - check selection")
    
    def clear_selection():
        system_view.selected_component = None
        system_view.canvas.delete("selection")
        system_view.selected_component_label.config(text="No component selected")
        print("✓ Cleared selection")
    
    def refresh_all():
        system_view.refresh_diagram()
        print("✓ Refreshed diagram")
    
    def count_canvas_items():
        all_items = system_view.canvas.find_all()
        connection_items = []
        selection_items = []
        
        for item in all_items:
            tags = system_view.canvas.gettags(item)
            for tag in tags:
                if 'connection' in tag.lower():
                    connection_items.append(item)
                    break
                elif tag == 'selection':
                    selection_items.append(item)
                    break
        
        print(f"📊 Canvas Items: {len(all_items)} total, {len(connection_items)} connections, {len(selection_items)} selection")
    
    # Row 1: Selection tests
    select_row = ttk.Frame(control_frame)
    select_row.pack(fill=tk.X, pady=2)
    ttk.Label(select_row, text="Selection Test:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    ttk.Button(select_row, text="Select API Server", command=select_api_server).pack(side=tk.LEFT, padx=5)
    ttk.Button(select_row, text="Select Database", command=select_database).pack(side=tk.LEFT, padx=5)
    ttk.Button(select_row, text="Select Temp Sensor", command=select_temp_sensor).pack(side=tk.LEFT, padx=5)
    ttk.Button(select_row, text="Clear Selection", command=clear_selection).pack(side=tk.LEFT, padx=5)
    
    # Row 2: Arrow tests
    arrow_row = ttk.Frame(control_frame)
    arrow_row.pack(fill=tk.X, pady=2)
    ttk.Label(arrow_row, text="Arrow Test:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    def force_clear_arrows():
        system_view.clear_all_connections()
        print("✓ Force cleared all arrows")
    
    def force_redraw_arrows():
        system_view.draw_connections()
        system_view.draw_system_connections()
        print("✓ Force redrawn all arrows")
    
    ttk.Button(arrow_row, text="Clear All Arrows", command=force_clear_arrows).pack(side=tk.LEFT, padx=5)
    ttk.Button(arrow_row, text="Redraw Arrows", command=force_redraw_arrows).pack(side=tk.LEFT, padx=5)
    ttk.Button(arrow_row, text="Refresh All", command=refresh_all).pack(side=tk.LEFT, padx=5)
    ttk.Button(arrow_row, text="Count Items", command=count_canvas_items).pack(side=tk.LEFT, padx=5)
    
    # Status display
    status_frame = ttk.LabelFrame(root, text="Test Status", padding="10")
    status_frame.pack(fill=tk.X, padx=10, pady=5)
    
    status_label = ttk.Label(status_frame, text="Ready for testing...", font=('Arial', 10))
    status_label.pack()
    
    def update_status():
        selected = system_view.selected_component
        if selected:
            comp_info = system_view.canvas_components.get(selected, {})
            pos = comp_info.get('position', (0, 0))
            obj = comp_info.get('object', None)
            name = obj.name if hasattr(obj, 'name') else selected
            status_text = f"Selected: {name} at position {pos}"
        else:
            status_text = "No component selected"
        
        # Count canvas items
        all_items = system_view.canvas.find_all()
        selection_items = system_view.canvas.find_withtag("selection")
        
        status_text += f" | Canvas items: {len(all_items)} | Selection items: {len(selection_items)}"
        
        status_label.config(text=status_text)
        root.after(1000, update_status)  # Update every second
    
    # Start status updates
    update_status()
    
    print("\n🧪 Selection & Arrow Test Started!")
    print("🎯 Test Goals:")
    print("   1. Selection rectangle should move with dragged components")
    print("   2. Arrows should clear completely when dragging starts")
    print("   3. Arrows should redraw properly during drag operations")
    print("\n📝 Test Steps:")
    print("   1. Click 'Select API Server' and verify red rectangle appears")
    print("   2. Drag the API Server and watch the selection rectangle")
    print("   3. Drag any component and watch arrow behavior")
    print("   4. Use 'Count Items' to verify arrows are being cleaned up")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    print("Selection Rectangle & Arrow Clearing Test")
    print("=" * 60)
    
    try:
        test_selection_and_arrows()
        print("✓ Test completed.")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()