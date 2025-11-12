"""
Main application window with menu, toolbar, and layout management.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Optional

from src.gui.home_view import HomeView
from src.gui.sensor_panel import SensorPanel
from src.gui.rules_panel import RulesPanel
from src.gui.log_viewer import LogViewer
from src.gui.security_panel import SecurityPanel
from src.gui.templates_dialog import TemplatesDialog


class SmartHomeMainWindow:
    """Main application window."""
    
    def __init__(self, root: tk.Tk, simulation_engine, logger):
        self.root = root
        self.sim_engine = simulation_engine
        self.logger = logger
        
        self.current_template = None
        self.project_file = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_layout()
        self.setup_status_bar()
        
        # Connect simulation engine callbacks
        self.sim_engine.add_event_callback(self.on_simulation_event)
        
        # Load default template or show template selection
        self.show_template_selection()
    
    def setup_ui(self):
        """Initialize UI components."""
        # Configure main window
        self.root.configure(bg='#f0f0f0')
        
        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned windows for resizable layout
        self.main_paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.right_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
    
    def setup_menu(self):
        """Create application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Project", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Project", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="Save Project As...", command=self.save_project_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export Configuration", command=self.export_config)
        file_menu.add_command(label="Import Configuration", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Select Template", command=self.show_template_selection)
        edit_menu.add_separator()
        edit_menu.add_command(label="Add Sensor", command=self.add_sensor_dialog)
        edit_menu.add_command(label="Clear All Sensors", command=self.clear_all_sensors)
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences", command=self.show_preferences)
        
        # Simulation Menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Start", command=self.start_simulation)
        sim_menu.add_command(label="Pause", command=self.pause_simulation)
        sim_menu.add_command(label="Stop", command=self.stop_simulation)
        sim_menu.add_command(label="Reset", command=self.reset_simulation)
        sim_menu.add_separator()
        sim_menu.add_command(label="Simulation Speed", command=self.show_speed_dialog)
        
        # Security Menu
        security_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Security", menu=security_menu)
        security_menu.add_command(label="Security Settings", command=self.show_security_settings)
        security_menu.add_command(label="Authenticate Sensors", command=self.authenticate_sensors)
        security_menu.add_command(label="Security Logs", command=self.show_security_logs)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show Log Viewer", command=self.toggle_log_viewer)
        view_menu.add_command(label="Show Sensor Panel", command=self.toggle_sensor_panel)
        view_menu.add_command(label="Show Rules Panel", command=self.toggle_rules_panel)
        view_menu.add_command(label="Show Security Panel", command=self.toggle_security_panel)
        view_menu.add_separator()
        view_menu.add_command(label="Full Screen", command=self.toggle_fullscreen, accelerator="F11")
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="Sensor Documentation", command=self.show_sensor_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind_all("<Control-n>", lambda e: self.new_project())
        self.root.bind_all("<Control-o>", lambda e: self.open_project())
        self.root.bind_all("<Control-s>", lambda e: self.save_project())
        self.root.bind_all("<Control-Shift-S>", lambda e: self.save_project_as())
        self.root.bind_all("<Control-q>", lambda e: self.on_closing())
        self.root.bind_all("<F11>", lambda e: self.toggle_fullscreen())
    
    def setup_toolbar(self):
        """Create application toolbar."""
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Simulation controls
        sim_frame = ttk.LabelFrame(self.toolbar, text="Simulation")
        sim_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        self.start_btn = ttk.Button(sim_frame, text="▶ Start", command=self.start_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = ttk.Button(sim_frame, text="⏸ Pause", command=self.pause_simulation, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(sim_frame, text="⏹ Stop", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        # Status indicator
        self.sim_status = ttk.Label(sim_frame, text="Stopped", foreground="red")
        self.sim_status.pack(side=tk.LEFT, padx=10)
        
        # Template selection
        template_frame = ttk.LabelFrame(self.toolbar, text="Template")
        template_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        ttk.Button(template_frame, text="Select Template", command=self.show_template_selection).pack(side=tk.LEFT, padx=2)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(self.toolbar, text="Quick Actions")
        actions_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        ttk.Button(actions_frame, text="+ Sensor", command=self.add_sensor_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Rules", command=self.show_rules_panel).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Security", command=self.show_security_panel).pack(side=tk.LEFT, padx=2)
    
    def setup_layout(self):
        """Setup main layout with panels."""
        # Left panel - Home view (main area)
        self.home_view = HomeView(self.main_paned, self.sim_engine, self.logger)
        self.main_paned.add(self.home_view.frame, weight=3)
        
        # Right panels
        self.main_paned.add(self.right_paned, weight=1)
        
        # Sensor panel
        self.sensor_panel = SensorPanel(self.right_paned, self.sim_engine, self.logger)
        self.right_paned.add(self.sensor_panel.frame, weight=1)
        
        # Connect bidirectional selection between home view and sensor panel
        self.home_view.set_selection_callback(self.on_home_view_selection_changed)
        self.sensor_panel.set_selection_callback(self.on_sensor_panel_selection_changed)
        
        # Rules panel
        self.rules_panel = RulesPanel(self.right_paned, self.sim_engine, self.logger)
        self.right_paned.add(self.rules_panel.frame, weight=1)
        
        # Log viewer (initially hidden)
        self.log_viewer = LogViewer(self.right_paned, self.logger)
        # Don't add to paned window initially - will be toggled
        
        # Security panel (initially hidden)
        self.security_panel = SecurityPanel(self.right_paned, self.sim_engine, self.logger)
        # Don't add to paned window initially - will be toggled
    
    def setup_status_bar(self):
        """Create status bar."""
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status labels
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Sensor count
        self.sensor_count_label = ttk.Label(self.status_bar, text="Sensors: 0")
        self.sensor_count_label.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Active rules
        self.rules_count_label = ttk.Label(self.status_bar, text="Rules: 0")
        self.rules_count_label.pack(side=tk.LEFT, padx=5)
        
        # Right side - simulation time and FPS
        self.sim_time_label = ttk.Label(self.status_bar, text="Time: 00:00:00")
        self.sim_time_label.pack(side=tk.RIGHT, padx=5)
        
        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        self.fps_label = ttk.Label(self.status_bar, text="FPS: 0")
        self.fps_label.pack(side=tk.RIGHT, padx=5)
    
    # File operations
    def new_project(self):
        """Create a new project."""
        if self.confirm_unsaved_changes():
            self.sim_engine.reset()
            self.project_file = None
            self.current_template = None
            self.update_title()
            self.show_template_selection()
    
    def open_project(self):
        """Open an existing project."""
        if not self.confirm_unsaved_changes():
            return
        
        filename = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("Smart Home Projects", "*.shp"), ("All Files", "*.*")],
            defaultextension=".shp"
        )
        
        if filename:
            try:
                self.sim_engine.load_project(filename)
                self.project_file = filename
                self.update_title()
                self.refresh_all_panels()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open project: {str(e)}")
    
    def save_project(self):
        """Save current project."""
        if self.project_file:
            try:
                self.sim_engine.save_project(self.project_file)
                self.update_title()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save project: {str(e)}")
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Save project with new filename."""
        filename = filedialog.asksaveasfilename(
            title="Save Project As",
            filetypes=[("Smart Home Projects", "*.shp"), ("All Files", "*.*")],
            defaultextension=".shp"
        )
        
        if filename:
            try:
                self.sim_engine.save_project(filename)
                self.project_file = filename
                self.update_title()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save project: {str(e)}")
    
    # Simulation controls
    def start_simulation(self):
        """Start the simulation."""
        self.sim_engine.start()
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.sim_status.config(text="Running", foreground="green")
    
    def pause_simulation(self):
        """Pause the simulation."""
        self.sim_engine.pause()
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.sim_status.config(text="Paused", foreground="orange")
    
    def stop_simulation(self):
        """Stop the simulation."""
        self.sim_engine.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.sim_status.config(text="Stopped", foreground="red")
    
    def reset_simulation(self):
        """Reset the simulation."""
        self.sim_engine.reset()
        self.stop_simulation()
    
    # Dialog methods
    def show_template_selection(self):
        """Show template selection dialog."""
        dialog = TemplatesDialog(self.root, self.sim_engine, self.logger)
        template = dialog.get_selected_template()
        
        if template:
            self.current_template = template
            self.sim_engine.load_template(template)
            self.home_view.load_template(template)
            self.refresh_all_panels()
    
    def add_sensor_dialog(self):
        """Show add sensor dialog."""
        self.sensor_panel.show_add_sensor_dialog()
    
    def show_rules_panel(self):
        """Show/focus rules panel."""
        self.toggle_rules_panel()
    
    def show_security_panel(self):
        """Show/focus security panel."""
        self.toggle_security_panel()
    
    # Panel toggle methods
    def toggle_log_viewer(self):
        """Toggle log viewer panel."""
        # Implementation depends on panel management
        pass
    
    def toggle_sensor_panel(self):
        """Toggle sensor panel."""
        pass
    
    def toggle_rules_panel(self):
        """Toggle rules panel."""
        pass
    
    def toggle_security_panel(self):
        """Toggle security panel."""
        pass
    
    # Event handlers
    def on_simulation_event(self, event):
        """Handle simulation events."""
        self.update_status_bar()
        # Forward to relevant panels
        self.home_view.on_simulation_event(event)
        self.sensor_panel.on_simulation_event(event)
        self.rules_panel.on_simulation_event(event)
    
    def update_status_bar(self):
        """Update status bar information."""
        sensor_count = len(self.sim_engine.get_sensors())
        rules_count = len(self.sim_engine.get_rules())
        
        self.sensor_count_label.config(text=f"Sensors: {sensor_count}")
        self.rules_count_label.config(text=f"Rules: {rules_count}")
        
        # Update simulation time and FPS if running
        if hasattr(self.sim_engine, 'get_simulation_time'):
            sim_time = self.sim_engine.get_simulation_time()
            self.sim_time_label.config(text=f"Time: {sim_time}")
        
        if hasattr(self.sim_engine, 'get_fps'):
            fps = self.sim_engine.get_fps()
            self.fps_label.config(text=f"FPS: {fps:.1f}")
    
    def refresh_all_panels(self):
        """Refresh all panels with current data."""
        self.home_view.refresh()
        self.sensor_panel.refresh()
        self.rules_panel.refresh()
        self.update_status_bar()
    
    def update_title(self):
        """Update window title."""
        title = "Smart Home Simulation"
        if self.project_file:
            title += f" - {os.path.basename(self.project_file)}"
        if hasattr(self.sim_engine, 'is_modified') and self.sim_engine.is_modified():
            title += " *"
        self.root.title(title)
    
    def confirm_unsaved_changes(self) -> bool:
        """Confirm if user wants to discard unsaved changes."""
        if hasattr(self.sim_engine, 'is_modified') and self.sim_engine.is_modified():
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before continuing?"
            )
            if result is True:  # Yes, save
                self.save_project()
                return True
            elif result is False:  # No, don't save
                return True
            else:  # Cancel
                return False
        return True
    
    # Selection synchronization between home view and sensor panel
    def on_home_view_selection_changed(self, sensor_id: str):
        """Handle selection change from home view."""
        # Update sensor panel selection without triggering callback
        self.sensor_panel.select_sensor_external(sensor_id)
    
    def on_sensor_panel_selection_changed(self, sensor_id: str):
        """Handle selection change from sensor panel."""
        # Update home view selection without triggering callback
        self.home_view.select_sensor_external(sensor_id)
    
    # Placeholder methods for menu items
    def export_config(self): pass
    def import_config(self): pass
    def clear_all_sensors(self): pass
    def show_preferences(self): pass
    def show_speed_dialog(self): pass
    def show_security_settings(self): pass
    def authenticate_sensors(self): pass
    def show_security_logs(self): pass
    def toggle_fullscreen(self): pass
    def show_help(self): pass
    def show_sensor_help(self): pass
    def show_about(self): pass
    
    def on_closing(self):
        """Handle application closing."""
        if self.confirm_unsaved_changes():
            self.sim_engine.stop()
            self.root.destroy()