#!/usr/bin/env python3
"""
Enhanced test script for drag-and-drop functionality with sensors and improved arrow clearing.
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

def test_enhanced_drag_functionality():
    """Test enhanced drag-and-drop with sensors and real-time arrow updates."""
    print("Testing Enhanced System View Drag and Drop...")
    
    # Create root window
    root = tk.Tk()
    root.title("Enhanced Drag & Drop Test")
    root.geometry("1600x1000")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Add some test sensors to make it more interesting
    from src.sensors.temperature_sensor import TemperatureSensor
    from src.sensors.motion_sensor import MotionSensor
    from src.sensors.door_window_sensor import DoorWindowSensor
    
    temp_sensor = TemperatureSensor("temp_01", "Living Room Temperature")
    motion_sensor = MotionSensor("motion_01", "Hallway Motion")
    door_sensor = DoorWindowSensor("door_01", "Front Door")
    
    engine.add_sensor(temp_sensor)
    engine.add_sensor(motion_sensor)
    engine.add_sensor(door_sensor)
    
    # Create system view
    system_view = SystemView(root, engine, logger)
    system_view.frame.pack(fill=tk.BOTH, expand=True)
    
    # Add comprehensive test instructions
    info_frame = ttk.LabelFrame(root, text="Enhanced Drag & Drop Test Instructions", padding="10")
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    instructions = """
    🎯 ENHANCED DRAG & DROP FEATURES:
    
    1. DRAGGABLE COMPONENTS:
       • System Components: API Server, Database, MQTT Broker (rectangles)
       • Sensors: Temperature, Motion, Door/Window (smaller rectangles)
       • Controllers: Data Filters and Aggregators (diamonds/circles)
    
    2. REAL-TIME ARROW UPDATES:
       • Arrows clear immediately when dragging starts
       • Arrows redraw in real-time during drag operations
       • Color-coded: HTTP (red), MQTT (teal), DATA (blue)
    
    3. RIGHT-CLICK MENUS:
       • System Components: Start/Stop/Restart/Configure/View Logs
       • Sensors: Toggle Active/View Data/Configure/Remove
       • Controllers: Configure/View Config/Remove
    
    4. VISUAL FEEDBACK:
       • Component borders show status (green=running, gray=stopped, red=error)
       • Smooth movement during drag operations
       • Connection labels show relationship types
    
    TEST ACTIONS:
    • Click and drag any component around the canvas
    • Right-click components for context-specific options
    • Watch arrows update in real-time during dragging
    """
    
    info_label = ttk.Label(info_frame, text=instructions, justify=tk.LEFT, font=('Arial', 9))
    info_label.pack(anchor=tk.W)
    
    # Create enhanced control panel
    control_frame = ttk.LabelFrame(root, text="Test Controls", padding="10")
    control_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Row 1: System controls
    system_row = ttk.Frame(control_frame)
    system_row.pack(fill=tk.X, pady=2)
    ttk.Label(system_row, text="System:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    def refresh_all():
        system_view.refresh_diagram()
        print("✓ Diagram refreshed with all components")
    
    def start_all_components():
        system_view.start_all_components()
        print("✓ Started all system components")
    
    def stop_all_components():
        system_view.stop_all_components()
        print("✓ Stopped all system components")
    
    ttk.Button(system_row, text="Refresh All", command=refresh_all).pack(side=tk.LEFT, padx=5)
    ttk.Button(system_row, text="Start All Components", command=start_all_components).pack(side=tk.LEFT, padx=5)
    ttk.Button(system_row, text="Stop All Components", command=stop_all_components).pack(side=tk.LEFT, padx=5)
    
    # Row 2: Component controls
    component_row = ttk.Frame(control_frame)
    component_row.pack(fill=tk.X, pady=2)
    ttk.Label(component_row, text="Add:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    def add_test_sensor():
        from src.sensors.light_sensor import LightSensor
        sensor_count = len([s for s in engine.get_sensors().values() if s.get_sensor_type() == 'light'])
        light_sensor = LightSensor(f"light_{sensor_count:02d}", f"Light Sensor {sensor_count + 1}")
        engine.add_sensor(light_sensor)
        system_view.refresh_diagram()
        print(f"✓ Added {light_sensor.name}")
    
    def add_filter():
        system_view.add_controller('filter')
        print("✓ Added data filter controller")
    
    def add_aggregator():
        system_view.add_controller('aggregator')
        print("✓ Added data aggregator controller")
    
    ttk.Button(component_row, text="Add Light Sensor", command=add_test_sensor).pack(side=tk.LEFT, padx=5)
    ttk.Button(component_row, text="Add Filter", command=add_filter).pack(side=tk.LEFT, padx=5)
    ttk.Button(component_row, text="Add Aggregator", command=add_aggregator).pack(side=tk.LEFT, padx=5)
    
    # Row 3: Test actions
    test_row = ttk.Frame(control_frame)
    test_row.pack(fill=tk.X, pady=2)
    ttk.Label(test_row, text="Test:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    def test_sensor_data():
        sensors = engine.get_sensors()
        if sensors:
            sensor = list(sensors.values())[0]
            try:
                data = sensor.read_data()
                print(f"✓ {sensor.name}: {data}")
            except Exception as e:
                print(f"✗ Error reading {sensor.name}: {e}")
        else:
            print("✗ No sensors available")
    
    def toggle_first_sensor():
        sensors = engine.get_sensors()
        if sensors:
            sensor = list(sensors.values())[0]
            sensor.is_active = not sensor.is_active
            system_view.refresh_diagram()
            print(f"✓ {sensor.name} {'activated' if sensor.is_active else 'deactivated'}")
    
    ttk.Button(test_row, text="Test Sensor Reading", command=test_sensor_data).pack(side=tk.LEFT, padx=5)
    ttk.Button(test_row, text="Toggle First Sensor", command=toggle_first_sensor).pack(side=tk.LEFT, padx=5)
    
    # Status display
    status_frame = ttk.LabelFrame(root, text="Component Status", padding="10")
    status_frame.pack(fill=tk.X, padx=10, pady=5)
    
    status_text = tk.Text(status_frame, height=4, wrap=tk.WORD, font=('Consolas', 9))
    status_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=status_text.yview)
    status_text.configure(yscrollcommand=status_scroll.set)
    
    status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_status_display():
        status_text.delete(1.0, tk.END)
        
        # System components
        status_text.insert(tk.END, "SYSTEM COMPONENTS:\n")
        for comp_id, comp in system_view.component_manager.components.items():
            pos = system_view.canvas_components.get(comp_id, {}).get('position', (0, 0))
            status_text.insert(tk.END, f"  {comp.name}: {comp.status.value} at {pos}\n")
        
        # Sensors
        status_text.insert(tk.END, "\nSENSORS:\n")
        for sensor_id, sensor in engine.get_sensors().items():
            pos = system_view.canvas_components.get(sensor_id, {}).get('position', (0, 0))
            active = "active" if sensor.is_active else "inactive"
            status_text.insert(tk.END, f"  {sensor.name}: {active} at {pos}\n")
        
        # Controllers
        if system_view.controllers:
            status_text.insert(tk.END, "\nCONTROLLERS:\n")
            for ctrl_id, ctrl in system_view.controllers.items():
                pos = system_view.canvas_components.get(ctrl_id, {}).get('position', (0, 0))
                status_text.insert(tk.END, f"  {ctrl.name}: {ctrl.controller_type} at {pos}\n")
        
        root.after(3000, update_status_display)  # Update every 3 seconds
    
    # Start status updates
    update_status_display()
    
    print("\n🚀 Enhanced Drag & Drop Test Started!")
    print("📋 Features to test:")
    print("   • Drag system components, sensors, and controllers")
    print("   • Watch real-time arrow updates during dragging")
    print("   • Right-click components for context menus")
    print("   • Add new components and see them become draggable")
    print("   • Check status updates in the bottom panel")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    print("Enhanced System View Drag & Drop Test")
    print("=" * 60)
    
    try:
        test_enhanced_drag_functionality()
        print("✓ Test completed successfully.")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()