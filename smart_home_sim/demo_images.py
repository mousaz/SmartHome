#!/usr/bin/env python3
"""
Demo script showing template background image functionality.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
import threading
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.log_system.logger import SmartHomeLogger
    from src.simulation.engine import SimulationEngine
    from src.gui.home_view import HomeView
    from src.gui.templates_dialog import TemplatesDialog
    
    def demo_image_functionality():
        """Demo the image background functionality."""
        print("Smart Home Image Background Demo")
        print("=" * 40)
        
        # Create main window
        root = tk.Tk()
        root.title("Template Image Demo")
        root.geometry("900x700")
        
        # Create logger and simulation engine
        logger = SmartHomeLogger()
        sim_engine = SimulationEngine(logger)
        
        # Create home view
        home_view = HomeView(root, sim_engine, logger)
        home_view.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create demo frame with instructions
        demo_frame = ttk.LabelFrame(root, text="Demo Instructions", padding="10")
        demo_frame.pack(fill=tk.X, padx=10, pady=5)
        
        instructions = tk.Text(demo_frame, height=4, wrap=tk.WORD)
        instructions.pack(fill=tk.X)
        
        instructions.insert(tk.END, 
            "1. Click 'Load Template' to select a template with background image\n"
            "2. Toggle 'Show Background' to show/hide the image\n"
            "3. Toggle 'Room Labels' to show/hide room names over the image\n"
            "4. Note: When image is loaded, walls and furniture are hidden\n"
        )
        instructions.config(state=tk.DISABLED)
        
        # Control buttons
        button_frame = ttk.Frame(demo_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        def load_template():
            """Load a template with image."""
            dialog = TemplatesDialog(root, sim_engine, logger)
            template = dialog.get_selected_template()
            
            if template:
                home_view.load_template(template)
                sim_engine.load_template(template)
                logger.info(f"Loaded template: {template.get('name', 'Unknown')}")
                
                # Add some demo sensors
                if 'sensors' in template:
                    for sensor_data in template['sensors'][:3]:  # Add first 3 sensors
                        try:
                            sensor = sim_engine.create_sensor_from_config(sensor_data)
                            if sensor:
                                home_view.add_sensor(sensor)
                        except Exception as e:
                            logger.warning(f"Could not create sensor: {e}")
        
        ttk.Button(button_frame, text="Load Template", command=load_template).pack(side=tk.LEFT, padx=5)
        
        def add_demo_sensor():
            """Add a demo sensor at center."""
            try:
                sensor = sim_engine.create_sensor('temperature', 'Demo Temp', (400, 300))
                if sensor:
                    home_view.add_sensor(sensor)
                    logger.info("Added demo temperature sensor")
            except Exception as e:
                logger.warning(f"Could not add demo sensor: {e}")
        
        ttk.Button(button_frame, text="Add Demo Sensor", command=add_demo_sensor).pack(side=tk.LEFT, padx=5)
        
        def show_images_folder():
            """Show information about available images."""
            images_dir = os.path.join(os.path.dirname(__file__), 'resources', 'images', 'houses')
            
            if os.path.exists(images_dir):
                files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                info = f"Available house images ({len(files)}):\n" + "\n".join(files)
            else:
                info = "Images directory not found"
            
            tk.messagebox.showinfo("Available Images", info)
        
        ttk.Button(button_frame, text="Show Images", command=show_images_folder).pack(side=tk.LEFT, padx=5)
        
        # Status label
        status_label = ttk.Label(demo_frame, text="Ready - Load a template to see background image functionality")
        status_label.pack(pady=(5, 0))
        
        # Auto-load first template for demo
        def auto_load():
            time.sleep(1)  # Wait for UI to initialize
            try:
                # Try to load family house template automatically
                import json
                template_path = os.path.join(os.path.dirname(__file__), 'templates', 'home_templates.json')
                
                if os.path.exists(template_path):
                    with open(template_path, 'r') as f:
                        templates = json.load(f)
                    
                    if 'family_house' in templates:
                        template = templates['family_house']
                        root.after(0, lambda: home_view.load_template(template))
                        root.after(0, lambda: status_label.config(text=f"Loaded: {template.get('name', 'Template')}"))
                    
            except Exception as e:
                root.after(0, lambda: status_label.config(text=f"Auto-load failed: {e}"))
        
        # Start auto-load in background (optional)
        # threading.Thread(target=auto_load, daemon=True).start()
        
        logger.info("Image demo started - check the home view for background image functionality")
        
        # Run the demo
        root.mainloop()

    if __name__ == '__main__':
        demo_image_functionality()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the smart_home_sim directory")
except Exception as e:
    print(f"Error starting demo: {e}")
    import traceback
    traceback.print_exc()