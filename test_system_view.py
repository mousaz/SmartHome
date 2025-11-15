#!/usr/bin/env python3

"""
Test the new tabbed interface with system view.
"""

import tkinter as tk
from tkinter import ttk
from src.simulation.engine import SimulationEngine
from src.log_system.logger import SmartHomeLogger
from src.gui.system_view import SystemView
from src.sensors.common_sensors import TemperatureSensor, MotionSensor, DoorWindowSensor

def test_system_view():
    """Test the system view functionality."""
    
    # Initialize components
    logger = SmartHomeLogger("test_system_view")
    sim_engine = SimulationEngine(logger)
    
    # Create test window
    root = tk.Tk()
    root.title("Test System View")
    root.geometry("1400x800")
    
    # Create system view
    system_view = SystemView(root, sim_engine, logger)
    system_view.frame.pack(fill=tk.BOTH, expand=True)
    
    # Add some test sensors
    temp_sensor = TemperatureSensor(name="Living Room Temp", location=(200, 150))
    motion_sensor = MotionSensor(name="Kitchen Motion", location=(300, 200))
    door_sensor = DoorWindowSensor(name="Main Door", location=(100, 100))
    
    sim_engine.add_sensor(temp_sensor)
    sim_engine.add_sensor(motion_sensor)
    sim_engine.add_sensor(door_sensor)
    
    # Add some test controllers
    system_view.add_controller("filter")
    system_view.add_controller("aggregator")
    
    # Refresh the diagram
    system_view.refresh_diagram()
    
    print("✅ System view test setup complete!")
    print("🔧 Try the following:")
    print("   - Click on sensors and controllers to select them")
    print("   - Use toolbar buttons to add components")
    print("   - Check configuration panels")
    print("   - Switch between tabs in configuration panel")
    
    root.mainloop()

if __name__ == "__main__":
    test_system_view()