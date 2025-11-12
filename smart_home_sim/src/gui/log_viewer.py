"""
Log viewer for displaying simulation logs.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime


class LogViewer:
    """Widget for viewing simulation logs."""
    
    def __init__(self, parent, logger):
        self.parent = parent
        self.logger = logger
        
        self.setup_ui()
        self.setup_log_handler()
    
    def setup_ui(self):
        """Initialize the log viewer UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Log Viewer", padding="5")
        
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Clear", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save", command=self.save_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # Log level filter
        ttk.Label(toolbar, text="Level:").pack(side=tk.LEFT, padx=(10, 5))
        self.level_var = tk.StringVar(value="All")
        level_combo = ttk.Combobox(toolbar, textvariable=self.level_var,
                                  values=["All", "DEBUG", "INFO", "WARNING", "ERROR"],
                                  state="readonly", width=10)
        level_combo.pack(side=tk.LEFT)
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Auto-scroll", variable=self.auto_scroll_var).pack(side=tk.RIGHT)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(self.frame, height=15, width=60, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different log levels
        self.log_text.tag_configure("DEBUG", foreground="gray")
        self.log_text.tag_configure("INFO", foreground="black")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")
    
    def setup_log_handler(self):
        """Setup handler to receive log messages."""
        # This would connect to the logger to receive messages
        pass
    
    def add_log_entry(self, level: str, message: str, timestamp: datetime = None):
        """Add a log entry."""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Check level filter
        if self.level_var.get() != "All" and level != self.level_var.get():
            return
        
        # Format log entry
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{time_str}] {level:8} {message}\n"
        
        # Add to text widget
        self.log_text.insert(tk.END, log_entry, level)
        
        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
    
    def clear_logs(self):
        """Clear all log entries."""
        self.log_text.delete(1.0, tk.END)
    
    def save_logs(self):
        """Save logs to file."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="Save Logs",
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to save logs: {str(e)}")