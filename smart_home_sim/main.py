#!/usr/bin/env python3
"""
Smart Home Simulation Application
Main entry point for the application.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root and src to path
project_root = os.path.dirname(__file__)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# Import application modules
try:
    from src.gui.main_window import SmartHomeMainWindow
    from src.simulation.engine import SimulationEngine
    from src.log_system.logger import SmartHomeLogger
except ImportError as e:
    print(f"Import error: {e}")
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path[:3])
    sys.exit(1)

def main():
    """Main application entry point."""
    try:
        # Initialize logging
        logger = SmartHomeLogger()
        logger.info("Starting Smart Home Simulation Application")
        
        # Initialize simulation engine
        sim_engine = SimulationEngine(logger)
        
        # Create main window
        root = tk.Tk()
        app = SmartHomeMainWindow(root, sim_engine, logger)
        
        # Configure window
        root.title("Smart Home Simulation")
        root.geometry("1200x800")
        root.minsize(800, 600)
        
        # Center window on screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Start application
        logger.info("Application GUI initialized successfully")
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Failed to start application: {str(e)}"
        print(error_msg)
        if 'messagebox' in globals():
            messagebox.showerror("Startup Error", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()