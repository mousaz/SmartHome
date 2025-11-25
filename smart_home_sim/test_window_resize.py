#!/usr/bin/env python3
"""
Test script for window resizing and click detection fixes.
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

def test_window_resize_click_detection():
    """Test window resizing and click detection functionality."""
    print("Testing Window Resize and Click Detection...")
    
    # Create root window
    root = tk.Tk()
    root.title("Window Resize & Click Detection Test")
    root.geometry("1200x800")
    root.minsize(800, 600)  # Set minimum size
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Add test sensors for more components to click on
    from src.sensors.temperature_sensor import TemperatureSensor
    from src.sensors.motion_sensor import MotionSensor
    from src.sensors.door_window_sensor import DoorWindowSensor
    
    temp_sensor = TemperatureSensor("temp_resize_test", "Resize Test Temp")
    motion_sensor = MotionSensor("motion_resize_test", "Resize Test Motion")
    door_sensor = DoorWindowSensor("door_resize_test", "Resize Test Door")
    
    engine.add_sensor(temp_sensor)
    engine.add_sensor(motion_sensor)
    engine.add_sensor(door_sensor)
    
    # Create system view
    system_view = SystemView(root, engine, logger)
    system_view.frame.pack(fill=tk.BOTH, expand=True)
    
    # Add comprehensive test instructions
    info_frame = ttk.LabelFrame(root, text="Window Resize & Click Detection Test", padding="10")
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    instructions = """
    🔧 TESTING WINDOW RESIZE AND CLICK DETECTION:
    
    1. RESIZE WINDOW TESTS:
       • Resize the window by dragging edges/corners
       • Try different window sizes (larger and smaller)
       • Click components after each resize
       • ✅ Components should remain clickable at all window sizes
    
    2. CLICK DETECTION TESTS:
       • Click on system components (API Server, Database, MQTT Broker)
       • Click on sensors (Temperature, Motion, Door sensors)
       • Try clicking at different areas of each component
       • ✅ Components should be selectable regardless of window size
    
    3. COORDINATE SYSTEM TESTS:
       • Resize window, then drag components
       • Selection rectangles should appear correctly
       • Drag operations should work smoothly
       • ✅ Coordinates should be accurate after resize
    
    4. SCROLL TESTS (if applicable):
       • Try scrolling the canvas if components extend beyond view
       • Click components in scrolled areas
       • ✅ Click detection should work in scrolled areas
    """
    
    info_label = ttk.Label(info_frame, text=instructions, justify=tk.LEFT, font=('Arial', 9))
    info_label.pack(anchor=tk.W)
    
    # Create test control panel
    control_frame = ttk.LabelFrame(root, text="Test Controls & Diagnostics", padding="10")
    control_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Diagnostic information display
    diag_row1 = ttk.Frame(control_frame)
    diag_row1.pack(fill=tk.X, pady=2)
    
    def get_canvas_info():
        canvas_width = system_view.canvas.winfo_width()
        canvas_height = system_view.canvas.winfo_height()
        window_width = root.winfo_width()
        window_height = root.winfo_height()
        scroll_region = system_view.canvas.cget('scrollregion')
        
        info = (f"Canvas: {canvas_width}x{canvas_height} | "
                f"Window: {window_width}x{window_height} | "
                f"Scroll: {scroll_region}")
        print(f"📊 {info}")
        diag_label.config(text=info)
    
    diag_label = ttk.Label(diag_row1, text="Canvas info will appear here...", font=('Consolas', 8))
    diag_label.pack(side=tk.LEFT)
    
    ttk.Button(diag_row1, text="Refresh Info", command=get_canvas_info).pack(side=tk.RIGHT)
    
    # Test controls
    test_row = ttk.Frame(control_frame)
    test_row.pack(fill=tk.X, pady=2)
    
    def test_click_at_position(x, y):
        """Test clicking at a specific canvas position."""
        # Simulate a click event
        event = type('Event', (), {})()
        event.x = x
        event.y = y
        
        # Convert to canvas coordinates
        canvas_x = system_view.canvas.canvasx(x)
        canvas_y = system_view.canvas.canvasy(y)
        
        # Find items at this position
        items = system_view.canvas.find_overlapping(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5)
        
        print(f"🎯 Click test at screen({x},{y}) -> canvas({canvas_x:.1f},{canvas_y:.1f})")
        print(f"   Found {len(items)} items: {items}")
        
        if items:
            for item in items:
                tags = system_view.canvas.gettags(item)
                print(f"   Item {item}: tags {tags}")
    
    def test_component_clicks():
        """Test clicking on all components."""
        print("\n🔍 Testing component clicks after current window size...")
        
        for comp_id, comp_info in system_view.canvas_components.items():
            x, y = comp_info['position']
            print(f"🎯 Testing {comp_id} at stored position ({x},{y})")
            
            # Find actual canvas items at this position
            items = system_view.canvas.find_overlapping(x-10, y-10, x+10, y+10)
            print(f"   Items found: {items}")
            
            # Test if component is clickable
            if comp_info['canvas_ids']:
                first_item = comp_info['canvas_ids'][0]
                coords = system_view.canvas.coords(first_item)
                print(f"   First item coords: {coords}")
    
    def resize_window_small():
        root.geometry("900x600")
        root.after(100, get_canvas_info)
        print("📏 Resized window to SMALL (900x600)")
    
    def resize_window_large():
        root.geometry("1600x1000")
        root.after(100, get_canvas_info)
        print("📏 Resized window to LARGE (1600x1000)")
    
    def resize_window_medium():
        root.geometry("1200x800")
        root.after(100, get_canvas_info)
        print("📏 Resized window to MEDIUM (1200x800)")
    
    # Test buttons
    ttk.Label(test_row, text="Window Size:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    ttk.Button(test_row, text="Small", command=resize_window_small).pack(side=tk.LEFT, padx=2)
    ttk.Button(test_row, text="Medium", command=resize_window_medium).pack(side=tk.LEFT, padx=2)
    ttk.Button(test_row, text="Large", command=resize_window_large).pack(side=tk.LEFT, padx=2)
    
    ttk.Separator(test_row, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
    
    ttk.Label(test_row, text="Tests:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    ttk.Button(test_row, text="Test Component Clicks", command=test_component_clicks).pack(side=tk.LEFT, padx=2)
    ttk.Button(test_row, text="Refresh Diagram", command=system_view.refresh_diagram).pack(side=tk.LEFT, padx=2)
    
    # Click tracking
    click_info_frame = ttk.LabelFrame(root, text="Click Tracking", padding="5")
    click_info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    click_info_label = ttk.Label(click_info_frame, text="Click anywhere on canvas to see coordinate info", font=('Consolas', 9))
    click_info_label.pack()
    
    # Override canvas click to add debugging
    original_click = system_view.on_canvas_click
    
    def debug_canvas_click(event):
        canvas_x = system_view.canvas.canvasx(event.x)
        canvas_y = system_view.canvas.canvasy(event.y)
        
        items = system_view.canvas.find_overlapping(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5)
        
        click_info = (f"Click: screen({event.x},{event.y}) -> canvas({canvas_x:.1f},{canvas_y:.1f}) | "
                     f"Items: {len(items)} | Window: {root.winfo_width()}x{root.winfo_height()}")
        
        click_info_label.config(text=click_info)
        print(f"🖱️ {click_info}")
        
        if items:
            for item in items:
                tags = system_view.canvas.gettags(item)
                print(f"   Item {item}: {tags}")
        
        # Call original click handler
        original_click(event)
    
    system_view.canvas.bind('<Button-1>', debug_canvas_click)
    
    # Window resize tracking
    def on_window_resize(event=None):
        if event and event.widget == root:
            get_canvas_info()
            print(f"🪟 Window resized to {root.winfo_width()}x{root.winfo_height()}")
    
    root.bind('<Configure>', on_window_resize)
    
    # Initial canvas info
    root.after(500, get_canvas_info)
    
    print("\n🧪 Window Resize & Click Detection Test Started!")
    print("🎯 Test Goals:")
    print("   1. Components remain clickable after window resize")
    print("   2. Click detection works with proper canvas coordinates")
    print("   3. Drag operations work correctly after resize")
    print("   4. Selection rectangles appear at correct positions")
    print("\n📝 Manual Test Steps:")
    print("   1. Click components to verify they're selectable")
    print("   2. Resize window using buttons or by dragging window edges")
    print("   3. Click components again after resize")
    print("   4. Try dragging components after resize")
    print("   5. Watch the click tracking info at bottom")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    print("Window Resize & Click Detection Test")
    print("=" * 60)
    
    try:
        test_window_resize_click_detection()
        print("✓ Test completed.")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()