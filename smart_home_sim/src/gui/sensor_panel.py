"""
Sensor panel for managing sensors in the simulation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any, Optional

from src.sensors.base_sensor import BaseSensor
from src.sensors.common_sensors import sensor_registry


class SensorConfigDialog:
    """Dialog for configuring sensor parameters."""
    
    def __init__(self, parent, sensor: BaseSensor):
        self.parent = parent
        self.sensor = sensor
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the configuration dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"Configure {self.sensor.name}")
        self.dialog.geometry("400x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Basic info frame
        info_frame = ttk.LabelFrame(main_frame, text="Basic Information", padding="5")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Sensor name
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.name_var = tk.StringVar(value=self.sensor.name)
        ttk.Entry(info_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky="ew")
        
        # Sensor type (read-only)
        ttk.Label(info_frame, text="Type:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        ttk.Label(info_frame, text=self.sensor.get_sensor_type()).grid(row=1, column=1, sticky="w")
        
        # Location
        ttk.Label(info_frame, text="Location:").grid(row=2, column=0, sticky="w", padx=(0, 5))
        location_frame = ttk.Frame(info_frame)
        location_frame.grid(row=2, column=1, sticky="ew")
        
        self.x_var = tk.IntVar(value=self.sensor.location[0])
        self.y_var = tk.IntVar(value=self.sensor.location[1])
        
        ttk.Label(location_frame, text="X:").pack(side=tk.LEFT)
        ttk.Entry(location_frame, textvariable=self.x_var, width=8).pack(side=tk.LEFT, padx=(2, 10))
        ttk.Label(location_frame, text="Y:").pack(side=tk.LEFT)
        ttk.Entry(location_frame, textvariable=self.y_var, width=8).pack(side=tk.LEFT, padx=2)
        
        info_frame.columnconfigure(1, weight=1)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration Parameters", padding="5")
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create scrollable frame for config parameters
        canvas = tk.Canvas(config_frame, height=200)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create config parameter widgets
        self.config_vars = {}
        self.create_config_widgets(scrollable_frame)
        
        # Security frame
        security_frame = ttk.LabelFrame(main_frame, text="Security Settings", padding="5")
        security_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(security_frame, text="Security Level:").grid(row=0, column=0, sticky="w")
        self.security_var = tk.StringVar(value=self.sensor.security_level)
        security_combo = ttk.Combobox(security_frame, textvariable=self.security_var, 
                                     values=["basic", "standard", "high", "critical"], 
                                     state="readonly", width=15)
        security_combo.grid(row=0, column=1, sticky="w", padx=(5, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT)
        ttk.Button(buttons_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT)
    
    def create_config_widgets(self, parent):
        """Create widgets for configuration parameters."""
        config = {**self.sensor.get_default_config(), **self.sensor.config}
        
        row = 0
        for key, value in config.items():
            ttk.Label(parent, text=f"{key}:").grid(row=row, column=0, sticky="w", padx=(0, 5))
            
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                ttk.Checkbutton(parent, variable=var).grid(row=row, column=1, sticky="w")
            elif isinstance(value, (int, float)):
                var = tk.DoubleVar(value=float(value))
                entry = ttk.Entry(parent, textvariable=var, width=15)
                entry.grid(row=row, column=1, sticky="w")
            elif isinstance(value, str):
                var = tk.StringVar(value=value)
                entry = ttk.Entry(parent, textvariable=var, width=20)
                entry.grid(row=row, column=1, sticky="w")
            else:
                var = tk.StringVar(value=str(value))
                entry = ttk.Entry(parent, textvariable=var, width=20)
                entry.grid(row=row, column=1, sticky="w")
            
            self.config_vars[key] = var
            row += 1
    
    def reset_defaults(self):
        """Reset configuration to defaults."""
        defaults = self.sensor.get_default_config()
        for key, var in self.config_vars.items():
            if key in defaults:
                if isinstance(var, tk.BooleanVar):
                    var.set(bool(defaults[key]))
                elif isinstance(var, tk.DoubleVar):
                    var.set(float(defaults[key]))
                else:
                    var.set(str(defaults[key]))
    
    def ok_clicked(self):
        """Handle OK button click."""
        try:
            # Collect configuration values
            config = {}
            for key, var in self.config_vars.items():
                value = var.get()
                
                # Try to convert to appropriate type
                original_type = type(self.sensor.get_default_config().get(key, ""))
                if original_type == int:
                    value = int(float(value))
                elif original_type == float:
                    value = float(value)
                elif original_type == bool:
                    value = bool(value)
                
                config[key] = value
            
            # Create result
            self.result = {
                'name': self.name_var.get(),
                'location': (self.x_var.get(), self.y_var.get()),
                'config': config,
                'security_level': self.security_var.get()
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid configuration: {str(e)}")
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def get_result(self):
        """Get dialog result."""
        self.dialog.wait_window()
        return self.result


class AddSensorDialog:
    """Dialog for adding a new sensor."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the add sensor dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Add New Sensor")
        self.dialog.geometry("350x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sensor type selection
        type_frame = ttk.LabelFrame(main_frame, text="Sensor Type", padding="5")
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Get available sensor types
        available_types = list(sensor_registry.get_available_types().keys())
        
        self.sensor_type_var = tk.StringVar()
        
        # Create radio buttons for each sensor type
        self.type_descriptions = {
            'temperature': 'Temperature and thermal monitoring',
            'motion': 'PIR motion detection',
            'door_window': 'Door and window open/close detection',
            'smoke': 'Smoke and fire detection',
            'light': 'Ambient light level monitoring',
            'humidity': 'Humidity and moisture monitoring',
            'pressure': 'Atmospheric pressure monitoring',
            'proximity': 'Ultrasonic distance measurement'
        }
        
        for i, sensor_type in enumerate(available_types):
            rb = ttk.Radiobutton(
                type_frame, 
                text=f"{sensor_type.title()}: {self.type_descriptions.get(sensor_type, 'Sensor')}",
                variable=self.sensor_type_var,
                value=sensor_type,
                command=self.on_type_changed
            )
            rb.pack(anchor=tk.W, pady=2)
        
        # Set default selection
        if available_types:
            self.sensor_type_var.set(available_types[0])
        
        # Basic configuration
        config_frame = ttk.LabelFrame(main_frame, text="Basic Configuration", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Sensor name
        ttk.Label(config_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.name_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.name_var, width=25).grid(row=0, column=1, sticky="ew")
        
        # Location
        ttk.Label(config_frame, text="Location:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        location_frame = ttk.Frame(config_frame)
        location_frame.grid(row=1, column=1, sticky="ew")
        
        self.x_var = tk.IntVar(value=100)
        self.y_var = tk.IntVar(value=100)
        
        ttk.Label(location_frame, text="X:").pack(side=tk.LEFT)
        ttk.Entry(location_frame, textvariable=self.x_var, width=8).pack(side=tk.LEFT, padx=(2, 10))
        ttk.Label(location_frame, text="Y:").pack(side=tk.LEFT)
        ttk.Entry(location_frame, textvariable=self.y_var, width=8).pack(side=tk.LEFT, padx=2)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Create", command=self.create_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT)
        
        # Update name when type changes
        self.on_type_changed()
    
    def on_type_changed(self):
        """Handle sensor type change."""
        sensor_type = self.sensor_type_var.get()
        if not self.name_var.get() or self.name_var.get().startswith(tuple(self.type_descriptions.keys())):
            # Auto-generate name
            self.name_var.set(f"{sensor_type}_sensor")
    
    def create_clicked(self):
        """Handle Create button click."""
        sensor_type = self.sensor_type_var.get()
        name = self.name_var.get().strip()
        
        if not sensor_type:
            messagebox.showerror("Error", "Please select a sensor type.")
            return
        
        if not name:
            messagebox.showerror("Error", "Please enter a sensor name.")
            return
        
        self.result = {
            'type': sensor_type,
            'name': name,
            'location': (self.x_var.get(), self.y_var.get())
        }
        
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def get_result(self):
        """Get dialog result."""
        self.dialog.wait_window()
        return self.result


class SensorPanel:
    """Panel for managing sensors."""
    
    def __init__(self, parent, simulation_engine, logger):
        self.parent = parent
        self.sim_engine = simulation_engine
        self.logger = logger
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Initialize the sensor panel UI."""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Sensors", padding="5")
        
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar, text="Add Sensor", command=self.show_add_sensor_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Remove", command=self.remove_selected_sensor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Configure", command=self.configure_selected_sensor).pack(side=tk.LEFT)
        
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side=tk.RIGHT)
        
        # Sensor list
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for sensor list
        columns = ("Name", "Type", "Status", "Location")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.tree.heading("Name", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Location", text="Location")
        
        self.tree.column("Name", width=100)
        self.tree.column("Type", width=80)
        self.tree.column("Status", width=60)
        self.tree.column("Location", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)
        
        # Context menu
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Configure", command=self.configure_selected_sensor)
        self.context_menu.add_command(label="Activate", command=self.activate_selected_sensor)
        self.context_menu.add_command(label="Deactivate", command=self.deactivate_selected_sensor)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove", command=self.remove_selected_sensor)
        
        # Status frame
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="0 sensors")
        self.status_label.pack(side=tk.LEFT)
        
        # Filter frame (collapsed by default)
        self.filter_frame = ttk.LabelFrame(self.frame, text="Filters")
        # Don't pack initially - can be shown/hidden
        
        self.setup_filters()
    
    def setup_filters(self):
        """Setup filter controls."""
        # Type filter
        ttk.Label(self.filter_frame, text="Type:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.type_filter_var = tk.StringVar(value="All")
        
        type_values = ["All"] + list(sensor_registry.get_available_types().keys())
        type_combo = ttk.Combobox(self.filter_frame, textvariable=self.type_filter_var,
                                 values=type_values, state="readonly", width=12)
        type_combo.grid(row=0, column=1, padx=(0, 10))
        type_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        # Status filter
        ttk.Label(self.filter_frame, text="Status:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.status_filter_var = tk.StringVar(value="All")
        
        status_values = ["All", "Active", "Inactive", "Error", "Maintenance"]
        status_combo = ttk.Combobox(self.filter_frame, textvariable=self.status_filter_var,
                                   values=status_values, state="readonly", width=12)
        status_combo.grid(row=0, column=3)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh())
    
    def show_add_sensor_dialog(self):
        """Show dialog to add a new sensor."""
        dialog = AddSensorDialog(self.frame)
        result = dialog.get_result()
        
        if result:
            try:
                # Create sensor
                sensor = sensor_registry.create_sensor(
                    result['type'],
                    name=result['name'],
                    location=result['location']
                )
                
                if sensor:
                    # Add to simulation engine
                    self.sim_engine.add_sensor(sensor)
                    self.refresh()
                    self.logger.info(f"Added new sensor: {sensor.name} ({sensor.get_sensor_type()})")
                else:
                    messagebox.showerror("Error", f"Failed to create sensor of type: {result['type']}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create sensor: {str(e)}")
    
    def configure_selected_sensor(self):
        """Configure the selected sensor."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sensor to configure.")
            return
        
        item = selection[0]
        sensor_id = self.tree.item(item)['values'][0]  # Assuming first column has ID
        sensor = self.sim_engine.get_sensor(sensor_id)
        
        if sensor:
            dialog = SensorConfigDialog(self.frame, sensor)
            result = dialog.get_result()
            
            if result:
                # Apply configuration
                sensor.name = result['name']
                sensor.set_location(result['location'][0], result['location'][1])
                sensor.config.update(result['config'])
                sensor.security_level = result['security_level']
                
                self.refresh()
                self.logger.info(f"Updated configuration for sensor: {sensor.name}")
    
    def remove_selected_sensor(self):
        """Remove the selected sensor."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a sensor to remove.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected sensor(s)?"):
            for item in selection:
                sensor_id = self.tree.item(item)['values'][0]
                self.sim_engine.remove_sensor(sensor_id)
                self.logger.info(f"Removed sensor: {sensor_id}")
            
            self.refresh()
    
    def activate_selected_sensor(self):
        """Activate the selected sensor."""
        selection = self.tree.selection()
        if selection:
            for item in selection:
                sensor_id = self.tree.item(item)['values'][0]
                sensor = self.sim_engine.get_sensor(sensor_id)
                if sensor:
                    sensor.activate()
            self.refresh()
    
    def deactivate_selected_sensor(self):
        """Deactivate the selected sensor."""
        selection = self.tree.selection()
        if selection:
            for item in selection:
                sensor_id = self.tree.item(item)['values'][0]
                sensor = self.sim_engine.get_sensor(sensor_id)
                if sensor:
                    sensor.deactivate()
            self.refresh()
    
    def refresh(self):
        """Refresh the sensor list."""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get sensors from simulation engine
        sensors = self.sim_engine.get_sensors()
        
        # Apply filters
        type_filter = self.type_filter_var.get() if hasattr(self, 'type_filter_var') else "All"
        status_filter = self.status_filter_var.get() if hasattr(self, 'status_filter_var') else "All"
        
        filtered_sensors = []
        for sensor in sensors.values():
            # Type filter
            if type_filter != "All" and sensor.get_sensor_type() != type_filter:
                continue
            
            # Status filter
            if status_filter != "All" and sensor.status.value.title() != status_filter:
                continue
            
            filtered_sensors.append(sensor)
        
        # Populate tree
        for sensor in filtered_sensors:
            location_str = f"({sensor.location[0]}, {sensor.location[1]})"
            
            self.tree.insert("", tk.END, values=(
                sensor.sensor_id,  # Hidden ID for reference
                sensor.name,
                sensor.get_sensor_type().title(),
                sensor.status.value.title(),
                location_str
            ))
        
        # Update status
        count = len(filtered_sensors)
        total = len(sensors)
        if count == total:
            self.status_label.config(text=f"{count} sensors")
        else:
            self.status_label.config(text=f"{count} of {total} sensors")
    
    def on_double_click(self, event):
        """Handle double-click on sensor item."""
        self.configure_selected_sensor()
    
    def on_right_click(self, event):
        """Handle right-click on sensor item."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_simulation_event(self, event):
        """Handle simulation events."""
        if event.event_type in ['sensor_added', 'sensor_removed', 'sensor_data', 'sensor_activated', 'sensor_deactivated']:
            self.refresh()