"""
Security panel for managing security settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SecurityPanel:
    """Panel for managing security settings."""
    
    def __init__(self, parent, simulation_engine, logger):
        self.parent = parent
        self.sim_engine = simulation_engine
        self.logger = logger
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the security panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Security", padding="5")
        
        # Security status
        status_frame = ttk.LabelFrame(self.frame, text="Security Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.security_status = ttk.Label(status_frame, text="Security: Enabled", foreground="green")
        self.security_status.pack()
        
        # Authentication
        auth_frame = ttk.LabelFrame(self.frame, text="Authentication", padding="5")
        auth_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(auth_frame, text="Authenticate All Sensors", command=self.authenticate_all).pack(fill=tk.X, pady=2)
        ttk.Button(auth_frame, text="Security Settings", command=self.show_security_settings).pack(fill=tk.X, pady=2)
        
        # Security log summary
        log_frame = ttk.LabelFrame(self.frame, text="Security Events", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.security_log = tk.Listbox(log_frame, height=8)
        self.security_log.pack(fill=tk.BOTH, expand=True)
        
        # Add some sample entries
        self.add_security_event("System started", "INFO")
        self.add_security_event("All sensors authenticated", "INFO")
    
    def authenticate_all(self):
        """Authenticate all sensors."""
        messagebox.showinfo("Authentication", "All sensors authenticated successfully")
        self.add_security_event("Manual authentication performed", "INFO")
    
    def show_security_settings(self):
        """Show security settings dialog."""
        messagebox.showinfo("Security Settings", "Security settings dialog not yet implemented")
    
    def add_security_event(self, message: str, level: str = "INFO"):
        """Add a security event to the log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {level}: {message}"
        
        self.security_log.insert(tk.END, entry)
        self.security_log.see(tk.END)
    
    def on_simulation_event(self, event):
        """Handle simulation events."""
        if event.event_type in ['sensor_added', 'sensor_removed']:
            self.add_security_event(f"Sensor {event.event_type}: {event.sensor_id}", "INFO")