"""
Logs panel for displaying logs from selected components.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from datetime import datetime
from typing import Optional, Dict, Any, List
import threading
import queue


class LogsPanel:
    """Panel for displaying logs from selected components."""
    
    def __init__(self, parent, simulation_engine, logger):
        self.parent = parent
        self.sim_engine = simulation_engine
        self.logger = logger
        
        # Currently selected component
        self.selected_component_id: Optional[str] = None
        self.selected_component_name: str = "No component selected"
        
        # Log filtering and display
        self.log_buffer: List[Dict[str, Any]] = []
        self.max_log_entries = 1000
        
        # Thread-safe log queue
        self.log_queue = queue.Queue()
        
        self.setup_ui()
        self.setup_log_monitoring()
        
    def setup_ui(self):
        """Initialize the logs panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Component Logs", padding="5")
        
        # Header with selected component info
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="Showing logs for:").pack(side=tk.LEFT)
        self.selected_label = ttk.Label(header_frame, text=self.selected_component_name, 
                                       font=("Arial", 9, "bold"))
        self.selected_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Clear", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Refresh", command=self.refresh_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Export", command=self.export_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # Log level filter
        ttk.Label(toolbar, text="Level:").pack(side=tk.LEFT, padx=(15, 5))
        self.level_var = tk.StringVar(value="All")
        level_combo = ttk.Combobox(toolbar, textvariable=self.level_var,
                                  values=["All", "DEBUG", "INFO", "WARNING", "ERROR"],
                                  state="readonly", width=10)
        level_combo.pack(side=tk.LEFT)
        level_combo.bind('<<ComboboxSelected>>', self.on_level_filter_changed)
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Auto-scroll", variable=self.auto_scroll_var).pack(side=tk.RIGHT)
        
        # Search functionality
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        ttk.Button(search_frame, text="Clear Search", command=self.clear_search).pack(side=tk.LEFT)
        
        # Log text area with syntax highlighting
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(text_frame, height=20, width=80, 
                                                 wrap=tk.WORD, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different log levels and highlighting
        self.setup_text_tags()
        
        # Status bar
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.log_count_label = ttk.Label(status_frame, text="Logs: 0")
        self.log_count_label.pack(side=tk.LEFT)
        
        self.last_update_label = ttk.Label(status_frame, text="Last update: Never")
        self.last_update_label.pack(side=tk.RIGHT)
        
    def setup_text_tags(self):
        """Configure text tags for syntax highlighting."""
        # Log level colors
        self.log_text.tag_configure("DEBUG", foreground="#666666")
        self.log_text.tag_configure("INFO", foreground="#000000")
        self.log_text.tag_configure("WARNING", foreground="#ff8c00", background="#fff8dc")
        self.log_text.tag_configure("ERROR", foreground="#dc143c", background="#ffe4e1")
        
        # Special highlighting
        self.log_text.tag_configure("timestamp", foreground="#4169e1")
        self.log_text.tag_configure("component", foreground="#228b22", font=("Consolas", 9, "bold"))
        self.log_text.tag_configure("search_match", background="#ffff00")
        
    def setup_log_monitoring(self):
        """Set up log monitoring and periodic updates."""
        # Start periodic log processing
        self.process_log_queue()
        
    def process_log_queue(self):
        """Process logs from the queue (called periodically)."""
        try:
            # Process up to 10 log entries at once to avoid UI blocking
            for _ in range(10):
                log_entry = self.log_queue.get_nowait()
                self.add_log_entry(log_entry)
        except queue.Empty:
            pass
        finally:
            # Schedule next processing
            self.frame.after(100, self.process_log_queue)
            
    def set_selected_component(self, component_id: str, component_name: str):
        """Set the currently selected component to show logs for."""
        if component_id != self.selected_component_id:
            self.selected_component_id = component_id
            self.selected_component_name = component_name
            
            # Update UI
            self.selected_label.config(text=component_name)
            self.frame.config(text=f"Component Logs - {component_name}")
            
            # Clear and refresh logs
            self.clear_logs()
            self.refresh_logs()
            
    def add_log_entry(self, log_entry: Dict[str, Any]):
        """Add a single log entry to the display."""
        # Check if this log is relevant to selected component
        if not self.is_relevant_log(log_entry):
            return
            
        # Add to buffer
        self.log_buffer.append(log_entry)
        
        # Maintain buffer size
        if len(self.log_buffer) > self.max_log_entries:
            self.log_buffer = self.log_buffer[-self.max_log_entries:]
            
        # Format and display the log entry
        self.display_log_entry(log_entry)
        
        # Update status
        self.update_status()
        
    def is_relevant_log(self, log_entry: Dict[str, Any]) -> bool:
        """Check if a log entry is relevant to the selected component."""
        if not self.selected_component_id:
            return False
            
        # Check if log entry mentions the component
        message = log_entry.get('message', '').lower()
        component_id = self.selected_component_id.lower()
        
        # Look for component ID or name in the log message
        if component_id in message or self.selected_component_name.lower() in message:
            return True
            
        # Check if log has component metadata
        component = log_entry.get('component')
        if component and component.lower() == component_id:
            return True
            
        return False
        
    def display_log_entry(self, log_entry: Dict[str, Any]):
        """Display a single log entry in the text widget."""
        # Apply level filter
        level_filter = self.level_var.get()
        log_level = log_entry.get('level', 'INFO')
        
        if level_filter != "All" and log_level != level_filter:
            return
            
        # Format timestamp
        timestamp = log_entry.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp_str = timestamp
        else:
            timestamp_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            
        # Format log message
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '')
        component = log_entry.get('component', self.selected_component_name)
        
        log_line = f"[{timestamp_str}] {level:<7} [{component}] {message}\n"
        
        # Insert with appropriate tags
        start_index = self.log_text.index(tk.END)
        self.log_text.insert(tk.END, log_line)
        
        # Apply formatting tags
        line_start = f"{start_index} linestart"
        line_end = f"{start_index} lineend"
        
        # Timestamp tag
        ts_end = f"{line_start}+{len(timestamp_str)+2}c"
        self.log_text.tag_add("timestamp", line_start, ts_end)
        
        # Level tag
        level_start = f"{ts_end}+1c"
        level_end = f"{level_start}+{len(level)}c"
        self.log_text.tag_add(level, level_start, level_end)
        
        # Component tag
        comp_start = f"{level_end}+2c"
        comp_end = f"{comp_start}+{len(component)+1}c"
        self.log_text.tag_add("component", comp_start, comp_end)
        
        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
            
        # Apply search highlighting if active
        self.apply_search_highlighting()
        
    def on_level_filter_changed(self, event=None):
        """Handle log level filter change."""
        self.refresh_display()
        
    def on_search_changed(self, event=None):
        """Handle search text change."""
        self.apply_search_highlighting()
        
    def apply_search_highlighting(self):
        """Apply search highlighting to visible text."""
        # Remove previous search highlighting
        self.log_text.tag_remove("search_match", "1.0", tk.END)
        
        search_term = self.search_var.get().strip()
        if not search_term:
            return
            
        # Find and highlight search matches
        start = "1.0"
        while True:
            pos = self.log_text.search(search_term, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(search_term)}c"
            self.log_text.tag_add("search_match", pos, end)
            start = end
            
    def clear_search(self):
        """Clear search text and highlighting."""
        self.search_var.set("")
        self.apply_search_highlighting()
        
    def refresh_display(self):
        """Refresh the log display with current filters."""
        self.log_text.delete("1.0", tk.END)
        
        for log_entry in self.log_buffer:
            self.display_log_entry(log_entry)
            
        self.update_status()
        
    def clear_logs(self):
        """Clear all displayed logs."""
        self.log_buffer.clear()
        self.log_text.delete("1.0", tk.END)
        self.update_status()
        
    def refresh_logs(self):
        """Refresh logs from the simulation engine."""
        if not self.selected_component_id:
            return
            
        # Get component-specific logs from the simulation engine
        self.get_component_logs_from_engine()
        
        # Also simulate some logs for demonstration
        self.simulate_component_logs()
        
    def get_component_logs_from_engine(self):
        """Get logs from the simulation engine for the selected component."""
        if not self.selected_component_id or not self.sim_engine:
            return
            
        # Try to get sensor or component from the simulation engine
        try:
            sensors = self.sim_engine.get_sensors()
            for sensor in sensors:
                if hasattr(sensor, 'sensor_id') and sensor.sensor_id == self.selected_component_id:
                    # Generate logs based on sensor state
                    self.generate_sensor_logs(sensor)
                    break
        except Exception as e:
            # If there's an error getting logs, create an error log entry
            error_log = {
                'timestamp': datetime.now(),
                'level': 'ERROR',
                'message': f'Failed to retrieve logs: {str(e)}',
                'component': self.selected_component_id
            }
            self.add_log_entry(error_log)
            
    def generate_sensor_logs(self, sensor):
        """Generate realistic logs for a sensor component."""
        try:
            # Get sensor information for log generation
            sensor_info = sensor.get_info() if hasattr(sensor, 'get_info') else {}
            sensor_status = sensor_info.get('status', 'unknown')
            last_reading = sensor_info.get('last_reading')
            
            # Generate initialization log
            init_log = {
                'timestamp': datetime.now(),
                'level': 'INFO',
                'message': f'Sensor initialized - Type: {sensor.get_sensor_type()}, Status: {sensor_status}',
                'component': self.selected_component_id
            }
            self.add_log_entry(init_log)
            
            # Generate reading logs if available
            if last_reading:
                reading_log = {
                    'timestamp': datetime.now(),
                    'level': 'DEBUG',
                    'message': f'Latest reading: {last_reading}',
                    'component': self.selected_component_id
                }
                self.add_log_entry(reading_log)
                
            # Generate status logs
            if sensor_status == 'active':
                status_log = {
                    'timestamp': datetime.now(),
                    'level': 'INFO',
                    'message': 'Sensor is active and collecting data',
                    'component': self.selected_component_id
                }
            else:
                status_log = {
                    'timestamp': datetime.now(),
                    'level': 'WARNING',
                    'message': f'Sensor status: {sensor_status}',
                    'component': self.selected_component_id
                }
            self.add_log_entry(status_log)
            
        except Exception as e:
            error_log = {
                'timestamp': datetime.now(),
                'level': 'ERROR',
                'message': f'Error generating sensor logs: {str(e)}',
                'component': self.selected_component_id
            }
            self.add_log_entry(error_log)
        
    def simulate_component_logs(self):
        """Simulate some component logs for demonstration."""
        if not self.selected_component_id:
            return
            
        sample_logs = [
            {
                'timestamp': datetime.now(),
                'level': 'INFO',
                'message': f'Component {self.selected_component_name} initialized successfully',
                'component': self.selected_component_id
            },
            {
                'timestamp': datetime.now(),
                'level': 'DEBUG',
                'message': f'Component status: ONLINE',
                'component': self.selected_component_id
            },
            {
                'timestamp': datetime.now(),
                'level': 'INFO',
                'message': f'Configuration updated for {self.selected_component_name}',
                'component': self.selected_component_id
            }
        ]
        
        for log_entry in sample_logs:
            self.add_log_entry(log_entry)
            
    def export_logs(self):
        """Export current logs to a file."""

        
        if not self.log_buffer:
            messagebox.showinfo("Export Logs", "No logs to export.")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export Logs",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Component Logs for: {self.selected_component_name}\n")
                    f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    
                    for log_entry in self.log_buffer:
                        timestamp = log_entry.get('timestamp', datetime.now())
                        if isinstance(timestamp, str):
                            ts_str = timestamp
                        else:
                            ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                            
                        level = log_entry.get('level', 'INFO')
                        message = log_entry.get('message', '')
                        component = log_entry.get('component', self.selected_component_name)
                        
                        f.write(f"[{ts_str}] {level:<7} [{component}] {message}\n")
                        
                messagebox.showinfo("Export Logs", f"Logs exported successfully to:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export logs:\n{str(e)}")
                
    def update_status(self):
        """Update the status bar with current log statistics."""
        filtered_count = len([log for log in self.log_buffer 
                             if self.level_var.get() == "All" or 
                             log.get('level') == self.level_var.get()])
        
        total_count = len(self.log_buffer)
        
        if self.level_var.get() == "All":
            count_text = f"Logs: {total_count}"
        else:
            count_text = f"Logs: {filtered_count}/{total_count} ({self.level_var.get()})"
            
        self.log_count_label.config(text=count_text)
        
        if self.log_buffer:
            last_log = self.log_buffer[-1]
            timestamp = last_log.get('timestamp', datetime.now())
            if isinstance(timestamp, str):
                last_update = timestamp
            else:
                last_update = timestamp.strftime("%H:%M:%S")
            self.last_update_label.config(text=f"Last update: {last_update}")
        else:
            self.last_update_label.config(text="Last update: Never")
            
    def on_simulation_event(self, event):
        """Handle simulation events and add relevant logs."""
        # Convert simulation events to log entries
        log_entry = {
            'timestamp': datetime.now(),
            'level': 'INFO',
            'message': f"Event: {event.get('type', 'unknown')} - {event.get('message', '')}",
            'component': event.get('component_id', 'system')
        }
        
        # Add to queue for processing
        self.log_queue.put(log_entry)