#!/usr/bin/env python3

"""
Test bidirectional selection between home view and sensor panel.
"""

import tkinter as tk
from tkinter import ttk
from src.simulation.engine import SimulationEngine
from src.log_system.logger import SmartHomeLogger
from src.gui.home_view import HomeView
from src.gui.sensor_panel import SensorPanel
from src.sensors.common_sensors import TemperatureSensor, MotionSensor

def test_bidirectional_selection():
    """Test bidirectional selection functionality."""
    
    # Initialize components
    logger = SmartHomeLogger("test_selection")
    sim_engine = SimulationEngine(logger)
    
    # Create test window
    root = tk.Tk()
    root.title("Test Bidirectional Selection")
    root.geometry("1000x700")
    
    # Create paned window
    paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True)
    
    # Create home view and sensor panel
    home_view = HomeView(paned, sim_engine, logger)
    sensor_panel = SensorPanel(paned, sim_engine, logger)
    
    paned.add(home_view.frame, weight=2)
    paned.add(sensor_panel.frame, weight=1)
    
    # Set up bidirectional selection
    def on_home_selection(sensor_id):
        print(f"Home view selected: {sensor_id}")
        sensor_panel.select_sensor_external(sensor_id)
    
    def on_panel_selection(sensor_id):
        print(f"Sensor panel selected: {sensor_id}")
        home_view.select_sensor_external(sensor_id)
    
    home_view.set_selection_callback(on_home_selection)
    sensor_panel.set_selection_callback(on_panel_selection)
    
    # Add some test sensors
    temp_sensor = TemperatureSensor(name="Living Room Temp", location=(200, 150))
    motion_sensor = MotionSensor(name="Kitchen Motion", location=(300, 200))
    
    sim_engine.add_sensor(temp_sensor)
    sim_engine.add_sensor(motion_sensor)
    
    # Add sensors to home view
    home_view.add_sensor(temp_sensor)
    home_view.add_sensor(motion_sensor)
    
    # Refresh sensor panel
    sensor_panel.refresh()
    
    print("✅ Test setup complete!")
    print("🔄 Try selecting sensors in either panel - selection should sync!")
    print("📍 Click sensors in home view or select them in sensor panel")
    
    root.mainloop()

if __name__ == "__main__":
    test_bidirectional_selection()