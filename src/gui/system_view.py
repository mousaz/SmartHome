"""
System view for managing sensors, connections, and data flow configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, List, Optional, Set, Tuple
import json

from src.sensors.base_sensor import BaseSensor
from src.system.components import (
    ComponentManager, APIServer, DatabaseServer, MQTTBroker, 
    SystemComponent, ComponentStatus, ComponentType
)


class ConnectionType:
    """Types of connections between components."""
    HTTP = "HTTP"
    MQTT = "MQTT"
    WEBSOCKET = "WebSocket"
    TCP = "TCP"
    UDP = "UDP"


class ConnectionMode:
    """Connection transmission modes."""
    WIRED = "Wired"
    WIRELESS = "Wireless"


class DataFormat:
    """Supported data output formats."""
    JSON = "JSON"
    XML = "XML"
    CSV = "CSV"
    BINARY = "Binary"


class Controller:
    """Base class for data controllers/filters."""
    
    def __init__(self, controller_id: str, name: str, controller_type: str):
        self.controller_id = controller_id
        self.name = name
        self.controller_type = controller_type
        self.config = {}
    
    def to_dict(self):
        return {
            'id': self.controller_id,
            'name': self.name,
            'type': self.controller_type,
            'config': self.config
        }


class DataFilter(Controller):
    """Data filtering controller."""
    
    def __init__(self, controller_id: str, name: str):
        super().__init__(controller_id, name, "Data Filter")
        self.config = {
            'filter_type': 'threshold',  # threshold, range, regex
            'threshold': 0,
            'min_value': 0,
            'max_value': 100,
            'regex_pattern': '',
            'enabled': True
        }


class DataAggregator(Controller):
    """Data aggregation controller."""
    
    def __init__(self, controller_id: str, name: str):
        super().__init__(controller_id, name, "Data Aggregator")
        self.config = {
            'aggregation_type': 'average',  # average, sum, min, max, count
            'window_size': 10,
            'enabled': True
        }


class Connection:
    """Represents a connection between components."""
    
    def __init__(self, connection_id: str, source_id: str, target_id: str,
                 connection_type: str = ConnectionType.HTTP,
                 mode: str = ConnectionMode.WIRED,
                 data_format: str = DataFormat.JSON):
        self.connection_id = connection_id
        self.source_id = source_id
        self.target_id = target_id
        self.connection_type = connection_type
        self.mode = mode
        self.data_format = data_format
        self.config = {}
        self.controllers = []  # List of controller IDs
    
    def to_dict(self):
        return {
            'id': self.connection_id,
            'source': self.source_id,
            'target': self.target_id,
            'type': self.connection_type,
            'mode': self.mode,
            'format': self.data_format,
            'config': self.config,
            'controllers': self.controllers
        }


class SystemView:
    """System view for managing sensor connections and data flow."""
    
    def __init__(self, parent, simulation_engine, logger):
        self.parent = parent
        self.sim_engine = simulation_engine
        self.logger = logger
        
        self.connections = {}  # connection_id -> Connection
        self.controllers = {}  # controller_id -> Controller
        self.selected_component = None
        self.canvas_components = {}  # component_id -> canvas item info
        
        # Drag and drop variables
        self.drag_item = None
        self.drag_component_id = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.last_click_pos = (0, 0)
        
        # Connection drawing variables
        self.connection_lines = {}  # connection_id -> line_id
        
        # Initialize component manager
        self.component_manager = ComponentManager(logger)
        self.setup_system_components()
        
        self.setup_ui()
    
    def setup_system_components(self):
        """Initialize system components."""
        # Create and register system components
        api_server = APIServer()
        database = DatabaseServer()
        mqtt_broker = MQTTBroker()
        
        self.component_manager.register_component(api_server)
        self.component_manager.register_component(database)
        self.component_manager.register_component(mqtt_broker)
        
        self.logger.info("System components initialized")
    
    def setup_ui(self):
        """Initialize the system view UI."""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area with paned window
        content_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        content_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - System diagram canvas
        self.create_diagram_panel(content_paned)
        
        # Right panel - Configuration panel
        self.create_config_panel(content_paned)
        
        content_paned.add(self.diagram_frame, weight=3)
        content_paned.add(self.config_frame, weight=1)
    
    def create_toolbar(self):
        """Create toolbar with system view actions."""
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # System components
        ttk.Label(toolbar, text="System:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="Start All", command=self.start_all_components).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Stop All", command=self.stop_all_components).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Component management
        ttk.Label(toolbar, text="Components:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="Add Controller", command=self.add_controller).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Connection", command=self.add_connection).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Layout controls
        ttk.Label(toolbar, text="Layout:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="Auto Layout", command=self.auto_layout).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Reset View", command=self.reset_view).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Export/Import
        ttk.Button(toolbar, text="Export Config", command=self.export_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Import Config", command=self.import_config).pack(side=tk.LEFT, padx=2)
    
    def create_diagram_panel(self, parent):
        """Create the system diagram canvas."""
        self.diagram_frame = ttk.LabelFrame(parent, text="System Architecture", padding="5")
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(self.diagram_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=800, height=600)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Pack canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind canvas events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Button-3>', self.on_canvas_right_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        
        # Context menu
        self.canvas_context_menu = tk.Menu(self.frame, tearoff=0)
        self.canvas_context_menu.add_command(label="Add Controller Here", command=self.add_controller_at_position)
        self.canvas_context_menu.add_separator()
        self.canvas_context_menu.add_command(label="Auto Layout", command=self.auto_layout)
    
    def create_config_panel(self, parent):
        """Create the configuration panel."""
        self.config_frame = ttk.LabelFrame(parent, text="Configuration", padding="5")
        
        # Create notebook for different configuration tabs
        self.config_notebook = ttk.Notebook(self.config_frame)
        self.config_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Component configuration tab
        self.component_config_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.component_config_frame, text="Component")
        self.create_component_config()
        
        # Connection configuration tab
        self.connection_config_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.connection_config_frame, text="Connections")
        self.create_connection_config()
        
        # Data flow configuration tab
        self.dataflow_config_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.dataflow_config_frame, text="Data Flow")
        self.create_dataflow_config()
    
    def create_component_config(self):
        """Create component configuration interface."""
        # Component selection
        selection_frame = ttk.LabelFrame(self.component_config_frame, text="Selected Component", padding="5")
        selection_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.selected_component_label = ttk.Label(selection_frame, text="No component selected")
        self.selected_component_label.pack()
        
        # Component properties
        props_frame = ttk.LabelFrame(self.component_config_frame, text="Properties", padding="5")
        props_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(props_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.component_name_var = tk.StringVar()
        self.component_name_entry = ttk.Entry(props_frame, textvariable=self.component_name_var)
        self.component_name_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Type (for controllers)
        ttk.Label(props_frame, text="Type:").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.component_type_var = tk.StringVar()
        self.component_type_combo = ttk.Combobox(props_frame, textvariable=self.component_type_var,
                                               values=["Data Filter", "Data Aggregator"], state="readonly")
        self.component_type_combo.grid(row=1, column=1, sticky="ew", padx=5)
        
        # Configuration text area
        ttk.Label(props_frame, text="Configuration:").grid(row=2, column=0, sticky="nw", padx=(0, 5), pady=(10, 0))
        
        config_text_frame = ttk.Frame(props_frame)
        config_text_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)
        
        self.component_config_text = tk.Text(config_text_frame, height=8, width=40)
        config_scroll = ttk.Scrollbar(config_text_frame, orient=tk.VERTICAL, command=self.component_config_text.yview)
        self.component_config_text.configure(yscrollcommand=config_scroll.set)
        
        self.component_config_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        config_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(props_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Apply", command=self.apply_component_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete", command=self.delete_component).pack(side=tk.LEFT, padx=2)
        
        props_frame.grid_columnconfigure(1, weight=1)
        props_frame.grid_rowconfigure(3, weight=1)
    
    def create_connection_config(self):
        """Create connection configuration interface."""
        # Connection list
        list_frame = ttk.LabelFrame(self.connection_config_frame, text="Connections", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for connections
        columns = ('Source', 'Target', 'Type', 'Mode', 'Format')
        self.connection_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.connection_tree.heading(col, text=col)
            self.connection_tree.column(col, width=100)
        
        # Scrollbar for connection tree
        conn_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.connection_tree.yview)
        self.connection_tree.configure(yscrollcommand=conn_scroll.set)
        
        self.connection_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        conn_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.connection_tree.bind('<<TreeviewSelect>>', self.on_connection_select)
        
        # Connection details
        details_frame = ttk.LabelFrame(self.connection_config_frame, text="Connection Details", padding="5")
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Connection type
        ttk.Label(details_frame, text="Type:").grid(row=0, column=0, sticky="w")
        self.conn_type_var = tk.StringVar()
        self.conn_type_combo = ttk.Combobox(details_frame, textvariable=self.conn_type_var,
                                          values=[ConnectionType.HTTP, ConnectionType.MQTT,
                                                ConnectionType.WEBSOCKET, ConnectionType.TCP, ConnectionType.UDP])
        self.conn_type_combo.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Connection mode
        ttk.Label(details_frame, text="Mode:").grid(row=1, column=0, sticky="w")
        self.conn_mode_var = tk.StringVar()
        self.conn_mode_combo = ttk.Combobox(details_frame, textvariable=self.conn_mode_var,
                                          values=[ConnectionMode.WIRED, ConnectionMode.WIRELESS])
        self.conn_mode_combo.grid(row=1, column=1, sticky="ew", padx=5)
        
        # Data format
        ttk.Label(details_frame, text="Format:").grid(row=2, column=0, sticky="w")
        self.data_format_var = tk.StringVar()
        self.data_format_combo = ttk.Combobox(details_frame, textvariable=self.data_format_var,
                                            values=[DataFormat.JSON, DataFormat.XML, DataFormat.CSV, DataFormat.BINARY])
        self.data_format_combo.grid(row=2, column=1, sticky="ew", padx=5)
        
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Buttons
        conn_button_frame = ttk.Frame(details_frame)
        conn_button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(conn_button_frame, text="Update Connection", command=self.update_connection).pack(side=tk.LEFT, padx=2)
        ttk.Button(conn_button_frame, text="Delete Connection", command=self.delete_connection).pack(side=tk.LEFT, padx=2)
    
    def create_dataflow_config(self):
        """Create data flow configuration interface."""
        # Controllers list
        controllers_frame = ttk.LabelFrame(self.dataflow_config_frame, text="Data Controllers", padding="5")
        controllers_frame.pack(fill=tk.BOTH, expand=True)
        
        # Controller treeview
        ctrl_columns = ('Name', 'Type', 'Status')
        self.controller_tree = ttk.Treeview(controllers_frame, columns=ctrl_columns, show='headings', height=8)
        
        for col in ctrl_columns:
            self.controller_tree.heading(col, text=col)
            self.controller_tree.column(col, width=80)
        
        ctrl_scroll = ttk.Scrollbar(controllers_frame, orient=tk.VERTICAL, command=self.controller_tree.yview)
        self.controller_tree.configure(yscrollcommand=ctrl_scroll.set)
        
        self.controller_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ctrl_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Controller actions
        ctrl_actions_frame = ttk.Frame(controllers_frame)
        ctrl_actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(ctrl_actions_frame, text="Add Filter", 
                  command=lambda: self.add_controller("filter")).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_actions_frame, text="Add Aggregator", 
                  command=lambda: self.add_controller("aggregator")).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_actions_frame, text="Configure", 
                  command=self.configure_controller).pack(side=tk.LEFT, padx=2)
    
    def refresh_diagram(self):
        """Refresh the system diagram."""
        self.canvas.delete("all")
        self.canvas_components.clear()
        
        # Draw system components
        system_components = list(self.component_manager.components.values())
        system_positions = self.calculate_system_component_positions(system_components)
        
        for i, component in enumerate(system_components):
            x, y = system_positions[i]
            self.draw_system_component(component, x, y)
        
        # Draw sensors
        sensors = self.sim_engine.get_sensors()
        sensor_positions = self.calculate_sensor_positions(list(sensors.values()))
        
        for i, sensor in enumerate(sensors.values()):
            x, y = sensor_positions[i]
            self.draw_sensor(sensor, x, y)
        
        # Draw controllers
        controller_positions = self.calculate_controller_positions()
        for i, controller in enumerate(self.controllers.values()):
            x, y = controller_positions[i]
            self.draw_controller(controller, x, y)
        
        # Draw connections
        self.draw_connections()
        self.draw_system_connections()
        
        # Update canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def draw_sensor(self, sensor: BaseSensor, x: int, y: int):
        """Draw a sensor on the canvas."""
        # Sensor colors by type
        colors = {
            'temperature': '#FF6B6B',
            'motion': '#4ECDC4',
            'door_window': '#45B7D1',
            'smoke': '#FFA07A',
            'light': '#FFD93D',
            'humidity': '#6BCF7F',
            'pressure': '#DDA0DD',
            'proximity': '#98D8C8'
        }
        
        color = colors.get(sensor.get_sensor_type(), '#CCCCCC')
        
        # Draw sensor rectangle
        rect_id = self.canvas.create_rectangle(
            x-40, y-20, x+40, y+20,
            fill=color, outline='black', width=2, tags=f"sensor_{sensor.sensor_id}"
        )
        
        # Draw sensor label
        label_id = self.canvas.create_text(
            x, y, text=sensor.name[:12] + ('...' if len(sensor.name) > 12 else ''),
            font=('Arial', 8, 'bold'), tags=f"sensor_{sensor.sensor_id}"
        )
        
        # Store component info
        self.canvas_components[sensor.sensor_id] = {
            'type': 'sensor',
            'object': sensor,
            'position': (x, y),
            'canvas_ids': [rect_id, label_id]
        }
        
        # Bind events
        for item_id in [rect_id, label_id]:
            self.canvas.tag_bind(item_id, '<Button-1>', lambda e, sid=sensor.sensor_id: self.select_component(sid))
    
    def draw_controller(self, controller: Controller, x: int, y: int):
        """Draw a controller on the canvas."""
        # Controller shape (diamond for filters, circle for aggregators)
        if controller.controller_type == "Data Filter":
            # Diamond shape
            points = [x, y-25, x+35, y, x, y+25, x-35, y]
            shape_id = self.canvas.create_polygon(points, fill='lightblue', outline='blue', width=2,
                                                tags=f"controller_{controller.controller_id}")
        else:
            # Circle shape
            shape_id = self.canvas.create_oval(x-30, y-20, x+30, y+20,
                                             fill='lightgreen', outline='green', width=2,
                                             tags=f"controller_{controller.controller_id}")
        
        # Controller label
        label_id = self.canvas.create_text(
            x, y, text=controller.name[:8] + ('...' if len(controller.name) > 8 else ''),
            font=('Arial', 8, 'bold'), tags=f"controller_{controller.controller_id}"
        )
        
        # Store component info
        self.canvas_components[controller.controller_id] = {
            'type': 'controller',
            'object': controller,
            'position': (x, y),
            'canvas_ids': [shape_id, label_id]
        }
        
        # Bind events
        for item_id in [shape_id, label_id]:
            self.canvas.tag_bind(item_id, '<Button-1>', lambda e, cid=controller.controller_id: self.select_component(cid))
    
    def draw_connections(self):
        """Draw connections between components."""
        for connection in self.connections.values():
            source_info = self.canvas_components.get(connection.source_id)
            target_info = self.canvas_components.get(connection.target_id)
            
            if source_info and target_info:
                sx, sy = source_info['position']
                tx, ty = target_info['position']
                
                # Draw connection line
                line_color = 'red' if connection.mode == ConnectionMode.WIRELESS else 'blue'
                line_width = 3 if connection.connection_type in [ConnectionType.HTTP, ConnectionType.WEBSOCKET] else 2
                
                line_id = self.canvas.create_line(sx, sy, tx, ty, fill=line_color, width=line_width,
                                                tags=f"connection_{connection.connection_id}")
                
                # Draw arrow
                mid_x, mid_y = (sx + tx) // 2, (sy + ty) // 2
                arrow_id = self.canvas.create_polygon([mid_x-5, mid_y-5, mid_x+5, mid_y, mid_x-5, mid_y+5],
                                                   fill=line_color, tags=f"connection_{connection.connection_id}")
                
                # Connection label
                label_text = f"{connection.connection_type}\n{connection.data_format}"
                label_id = self.canvas.create_text(mid_x, mid_y-20, text=label_text, font=('Arial', 6),
                                                 tags=f"connection_{connection.connection_id}")
    
    def calculate_sensor_positions(self, sensors: List[BaseSensor]) -> List[Tuple[int, int]]:
        """Calculate positions for sensors in a grid layout."""
        if not sensors:
            return []
        
        # Simple grid layout
        cols = int((len(sensors) ** 0.5)) + 1
        positions = []
        
        for i, sensor in enumerate(sensors):
            row = i // cols
            col = i % cols
            x = 100 + col * 120
            y = 100 + row * 80
            positions.append((x, y))
        
        return positions
    
    def calculate_controller_positions(self) -> List[Tuple[int, int]]:
        """Calculate positions for controllers."""
        if not self.controllers:
            return []
        
        # Place controllers in a separate area
        positions = []
        for i, controller in enumerate(self.controllers.values()):
            x = 600 + (i % 3) * 120
            y = 300 + (i // 3) * 80
            positions.append((x, y))
        
        return positions
    
    def calculate_system_component_positions(self, components: List[SystemComponent]) -> List[Tuple[int, int]]:
        """Calculate positions for system components."""
        if not components:
            return []
        
        # Place system components at the top
        positions = []
        for i, component in enumerate(components):
            x = 150 + i * 180
            y = 50
            positions.append((x, y))
        
        return positions
    
    def draw_system_component(self, component: SystemComponent, x: int, y: int):
        """Draw a system component on the canvas."""
        # Component colors by type
        colors = {
            ComponentType.API_SERVER: '#FF9999',
            ComponentType.DATABASE: '#99FF99', 
            ComponentType.MQTT_BROKER: '#9999FF',
            ComponentType.WEB_INTERFACE: '#FFFF99'
        }
        
        color = colors.get(component.component_type, '#DDDDDD')
        
        # Status border colors
        status_colors = {
            ComponentStatus.RUNNING: 'green',
            ComponentStatus.STOPPED: 'gray',
            ComponentStatus.ERROR: 'red',
            ComponentStatus.STARTING: 'orange',
            ComponentStatus.STOPPING: 'orange'
        }
        
        border_color = status_colors.get(component.status, 'black')
        
        # Draw component rectangle (larger than sensors)
        rect_id = self.canvas.create_rectangle(
            x-60, y-30, x+60, y+30,
            fill=color, outline=border_color, width=3, tags=f"system_{component.component_id}"
        )
        
        # Draw component icon/type indicator
        icon_id = self.canvas.create_oval(
            x-50, y-20, x-30, y+20,
            fill='white', outline=border_color, width=2, tags=f"system_{component.component_id}"
        )
        
        # Draw component label
        label_id = self.canvas.create_text(
            x, y, text=component.name,
            font=('Arial', 10, 'bold'), tags=f"system_{component.component_id}"
        )
        
        # Draw status indicator
        status_text = component.status.value.upper()
        status_id = self.canvas.create_text(
            x, y+40, text=status_text,
            font=('Arial', 8), fill=border_color, tags=f"system_{component.component_id}"
        )
        
        # Store component info
        self.canvas_components[component.component_id] = {
            'type': 'system_component',
            'object': component,
            'position': (x, y),
            'canvas_ids': [rect_id, icon_id, label_id, status_id]
        }
        
        # Bind events
        for item_id in [rect_id, icon_id, label_id, status_id]:
            self.canvas.tag_bind(item_id, '<Button-1>', lambda e, cid=component.component_id: self.select_component(cid))
            self.canvas.tag_bind(item_id, '<Button-3>', lambda e, cid=component.component_id: self.show_component_context_menu(e, cid))
    
    def show_component_context_menu(self, event, component_id: str):
        """Show context menu for system component."""
        component = self.component_manager.components.get(component_id)
        if not component:
            return
            
        # Create context menu
        context_menu = tk.Menu(self.frame, tearoff=0)
        
        if component.status == ComponentStatus.STOPPED:
            context_menu.add_command(label="Start", command=lambda: self.start_component(component_id))
        elif component.status == ComponentStatus.RUNNING:
            context_menu.add_command(label="Stop", command=lambda: self.stop_component(component_id))
            context_menu.add_command(label="Restart", command=lambda: self.restart_component(component_id))
        
        context_menu.add_separator()
        context_menu.add_command(label="View Logs", command=lambda: self.view_component_logs(component_id))
        context_menu.add_command(label="Configure", command=lambda: self.configure_component(component_id))
        
        context_menu.post(event.x_root, event.y_root)
    
    def start_component(self, component_id: str):
        """Start a system component."""
        if component_id in self.component_manager.components:
            self.component_manager.start_component(component_id)
            self.refresh_diagram()
    
    def stop_component(self, component_id: str):
        """Stop a system component."""
        if component_id in self.component_manager.components:
            self.component_manager.stop_component(component_id)
            self.refresh_diagram()
    
    def restart_component(self, component_id: str):
        """Restart a system component."""
        if component_id in self.component_manager.components:
            self.component_manager.restart_component(component_id)
            self.refresh_diagram()
    
    def view_component_logs(self, component_id: str):
        """View logs for a specific component."""
        # Switch to log viewer tab and filter by component
        if hasattr(self.config_notebook, 'logs_frame'):
            # Select logs tab
            for i in range(self.config_notebook.index("end")):
                if self.config_notebook.tab(i, "text") == "Logs":
                    self.config_notebook.select(i)
                    break
        
        # Apply component filter if log viewer supports it
        # This would be implemented when the log viewer is created
        pass
    
    def configure_component(self, component_id: str):
        """Open configuration dialog for a component."""
        component = self.component_manager.components.get(component_id)
        if not component:
            return
            
        # Create configuration dialog
        config_dialog = tk.Toplevel(self.frame)
        config_dialog.title(f"Configure {component.name}")
        config_dialog.geometry("400x300")
        config_dialog.transient(self.frame.winfo_toplevel())
        config_dialog.grab_set()
        
        # Configuration frame
        config_frame = ttk.Frame(config_dialog)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Component type-specific configuration
        if component.component_type == ComponentType.API_SERVER:
            ttk.Label(config_frame, text="Port:").grid(row=0, column=0, sticky="w", pady=5)
            port_var = tk.StringVar(value=str(component.config.get('port', 5000)))
            ttk.Entry(config_frame, textvariable=port_var).grid(row=0, column=1, sticky="ew", pady=5)
            
            ttk.Label(config_frame, text="Host:").grid(row=1, column=0, sticky="w", pady=5)
            host_var = tk.StringVar(value=component.config.get('host', 'localhost'))
            ttk.Entry(config_frame, textvariable=host_var).grid(row=1, column=1, sticky="ew", pady=5)
            
        elif component.component_type == ComponentType.DATABASE:
            ttk.Label(config_frame, text="Database File:").grid(row=0, column=0, sticky="w", pady=5)
            db_var = tk.StringVar(value=component.config.get('database', 'smart_home.db'))
            ttk.Entry(config_frame, textvariable=db_var).grid(row=0, column=1, sticky="ew", pady=5)
            
        elif component.component_type == ComponentType.MQTT_BROKER:
            ttk.Label(config_frame, text="Port:").grid(row=0, column=0, sticky="w", pady=5)
            port_var = tk.StringVar(value=str(component.config.get('port', 1883)))
            ttk.Entry(config_frame, textvariable=port_var).grid(row=0, column=1, sticky="ew", pady=5)
            
            ttk.Label(config_frame, text="Keep Alive:").grid(row=1, column=0, sticky="w", pady=5)
            keepalive_var = tk.StringVar(value=str(component.config.get('keepalive', 60)))
            ttk.Entry(config_frame, textvariable=keepalive_var).grid(row=1, column=1, sticky="ew", pady=5)
        
        config_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(config_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def save_config():
            # Update component configuration
            if component.component_type == ComponentType.API_SERVER:
                component.config['port'] = int(port_var.get())
                component.config['host'] = host_var.get()
            elif component.component_type == ComponentType.DATABASE:
                component.config['database'] = db_var.get()
            elif component.component_type == ComponentType.MQTT_BROKER:
                component.config['port'] = int(port_var.get())
                component.config['keepalive'] = int(keepalive_var.get())
            
            config_dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=config_dialog.destroy).pack(side=tk.RIGHT)
    
    def start_all_components(self):
        """Start all system components."""
        self.component_manager.start_all_components()
        self.refresh_diagram()
    
    def stop_all_components(self):
        """Stop all system components."""
        self.component_manager.stop_all_components()
        self.refresh_diagram()
    
    def auto_layout(self):
        """Automatically arrange components in a logical layout."""
        self.refresh_diagram()
    
    def reset_view(self):
        """Reset the view to default."""
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.refresh_diagram()
    
    def select_component(self, component_id: str):
        """Select a component and update configuration panel."""
        self.selected_component = component_id
        
        # Update selection highlight
        self.canvas.delete("selection")
        
        if component_id in self.canvas_components:
            info = self.canvas_components[component_id]
            x, y = info['position']
            
            # Highlight selected component
            self.canvas.create_rectangle(x-45, y-25, x+45, y+25, outline='red', width=3, tags="selection")
            
            # Update configuration panel
            self.update_config_panel(component_id, info)
    
    def update_config_panel(self, component_id: str, component_info: dict):
        """Update the configuration panel with selected component details."""
        obj = component_info['object']
        comp_type = component_info['type']
        
        if comp_type == 'sensor':
            self.selected_component_label.config(text=f"Sensor: {obj.name}")
            self.component_name_var.set(obj.name)
            self.component_type_combo.config(state='disabled')
            
            # Show sensor configuration
            config_dict = {
                'type': obj.get_sensor_type(),
                'location': obj.location,
                'status': obj.status.value,
                'config': getattr(obj, 'config', {})
            }
            self.component_config_text.delete(1.0, tk.END)
            self.component_config_text.insert(1.0, json.dumps(config_dict, indent=2))
            
        elif comp_type == 'controller':
            self.selected_component_label.config(text=f"Controller: {obj.name}")
            self.component_name_var.set(obj.name)
            self.component_type_var.set(obj.controller_type)
            self.component_type_combo.config(state='readonly')
            
            # Show controller configuration
            self.component_config_text.delete(1.0, tk.END)
            self.component_config_text.insert(1.0, json.dumps(obj.config, indent=2))
    
    # Event handlers
    def on_canvas_click(self, event):
        """Handle canvas click."""
        # Store click position
        self.last_click_pos = (event.x, event.y)
        
        # Find clicked item
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item)
        
        # Check if clicking on a draggable component
        draggable_component_id = None
        for tag in tags:
            if tag.startswith(('sensor_', 'controller_', 'system_')):
                # Extract component ID from tag
                draggable_component_id = tag.split('_', 1)[1] if '_' in tag else None
                break
        
        if draggable_component_id:
            # Set up for potential drag
            self.drag_item = item
            self.drag_component_id = draggable_component_id
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            
            # Select the component
            self.select_component(draggable_component_id)
        else:
            # Clear selection if clicking on empty space
            self.selected_component = None
            self.canvas.delete("selection")
            self.selected_component_label.config(text="No component selected")
            
            # Clear drag state
            self.drag_item = None
            self.drag_component_id = None
    
    def on_canvas_right_click(self, event):
        """Handle canvas right-click."""
        self.click_x = event.x
        self.click_y = event.y
        self.canvas_context_menu.post(event.x_root, event.y_root)
    
    def on_canvas_drag(self, event):
        """Handle canvas dragging."""
        if self.drag_item and self.drag_component_id:
            # Calculate drag distance
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            
            # Only start drag if moved far enough (prevents accidental drags)
            if abs(dx) > 3 or abs(dy) > 3:
                self.move_component(self.drag_component_id, dx, dy)
                
                # Update drag start position for continuous dragging
                self.drag_start_x = event.x
                self.drag_start_y = event.y
    
    def on_canvas_release(self, event):
        """Handle canvas mouse release."""
        if self.drag_item and self.drag_component_id:
            # Update component position in storage
            self.update_component_position(self.drag_component_id)
            
            # Redraw connections to update arrow positions
            self.redraw_connections()
        
        # Clear drag state
        self.drag_item = None
        self.drag_component_id = None
    
    def move_component(self, component_id: str, dx: int, dy: int):
        """Move a component by the specified offset."""
        if component_id in self.canvas_components:
            component_info = self.canvas_components[component_id]
            
            # Move all canvas items for this component
            for canvas_id in component_info['canvas_ids']:
                self.canvas.move(canvas_id, dx, dy)
            
            # Update stored position
            old_x, old_y = component_info['position']
            component_info['position'] = (old_x + dx, old_y + dy)
    
    def update_component_position(self, component_id: str):
        """Update the stored position of a component after dragging."""
        if component_id in self.canvas_components:
            component_info = self.canvas_components[component_id]
            # Position is already updated in move_component, but we could
            # trigger additional actions here if needed
            self.logger.debug(f"Component {component_id} moved to {component_info['position']}")
    
    def redraw_connections(self):
        """Redraw all connection arrows after components have moved."""
        # Clear existing connection lines
        for line_id in self.connection_lines.values():
            self.canvas.delete(line_id)
        self.connection_lines.clear()
        
        # Redraw all connections
        self.draw_system_connections()
    
    def draw_system_connections(self):
        """Draw connection arrows between system components."""
        # Define default connections between system components
        default_connections = [
            ('api_server', 'database', 'HTTP'),
            ('mqtt_broker', 'api_server', 'MQTT'),
            ('database', 'mqtt_broker', 'DATA')
        ]
        
        # Draw default system connections
        for source_id, target_id, conn_type in default_connections:
            if source_id in self.canvas_components and target_id in self.canvas_components:
                self.draw_connection_arrow(source_id, target_id, conn_type)
        
        # Draw user-defined connections
        for connection in self.connections.values():
            if (connection.source_id in self.canvas_components and 
                connection.target_id in self.canvas_components):
                self.draw_connection_arrow(connection.source_id, connection.target_id, 
                                         connection.connection_type, connection.connection_id)
    
    def draw_connection_arrow(self, source_id: str, target_id: str, 
                             connection_type: str, connection_id: Optional[str] = None):
        """Draw an arrow connection between two components."""
        if source_id not in self.canvas_components or target_id not in self.canvas_components:
            return None
            
        source_pos = self.canvas_components[source_id]['position']
        target_pos = self.canvas_components[target_id]['position']
        
        # Calculate connection points (edge of components rather than center)
        source_x, source_y = source_pos
        target_x, target_y = target_pos
        
        # Offset from component center to edge
        component_radius = 60  # Half the width of component rectangles
        
        # Calculate direction vector
        import math
        dx = target_x - source_x
        dy = target_y - source_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return None
            
        # Normalize direction vector
        dx_norm = dx / distance
        dy_norm = dy / distance
        
        # Calculate start and end points at component edges
        start_x = source_x + dx_norm * component_radius
        start_y = source_y + dy_norm * component_radius
        end_x = target_x - dx_norm * component_radius
        end_y = target_y - dy_norm * component_radius
        
        # Connection colors by type
        connection_colors = {
            'HTTP': '#FF6B6B',
            'MQTT': '#4ECDC4', 
            'DATA': '#45B7D1',
            'TCP': '#96CEB4',
            'UDP': '#FFEAA7',
            'WebSocket': '#DDA0DD'
        }
        
        color = connection_colors.get(connection_type, '#666666')
        
        # Draw the line
        line_id = self.canvas.create_line(
            start_x, start_y, end_x, end_y,
            fill=color, width=2, arrow=tk.LAST, arrowshape=(16, 20, 6),
            tags=f"connection_{connection_id or f'{source_id}_{target_id}'}"
        )
        
        # Draw connection label
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Offset label slightly to avoid overlapping with line
        label_offset = 15
        label_x = mid_x + label_offset if dx >= 0 else mid_x - label_offset
        label_y = mid_y - label_offset
        
        label_id = self.canvas.create_text(
            label_x, label_y, text=connection_type,
            font=('Arial', 8), fill=color,
            tags=f"connection_{connection_id or f'{source_id}_{target_id}'}"
        )
        
        # Store connection line IDs
        conn_key = connection_id or f"{source_id}_{target_id}"
        self.connection_lines[conn_key] = [line_id, label_id]
        
        return line_id
    
    def on_connection_select(self, event):
        """Handle connection selection in tree view."""
        selection = self.connection_tree.selection()
        if selection:
            item = selection[0]
            # Get connection ID and update details
            # Implementation depends on how you store connection data in tree
    
    # Action methods
    def add_controller(self, controller_type=None):
        """Add a new controller."""
        if controller_type is None:
            controller_type = simpledialog.askstring("Controller Type", 
                                                   "Enter controller type (filter/aggregator):")
        
        if controller_type:
            name = simpledialog.askstring("Controller Name", "Enter controller name:")
            if name:
                controller_id = f"ctrl_{len(self.controllers)}"
                
                if controller_type.lower() in ['filter', 'data filter']:
                    controller = DataFilter(controller_id, name)
                elif controller_type.lower() in ['aggregator', 'data aggregator']:
                    controller = DataAggregator(controller_id, name)
                else:
                    controller = Controller(controller_id, name, controller_type)
                
                self.controllers[controller_id] = controller
                self.refresh_diagram()
                self.logger.info(f"Added controller: {name} ({controller_type})")
    
    def add_controller_at_position(self):
        """Add controller at clicked position."""
        if hasattr(self, 'click_x') and hasattr(self, 'click_y'):
            self.add_controller()
    
    def add_connection(self):
        """Add a new connection between components."""
        # This would open a dialog to select source and target components
        messagebox.showinfo("Add Connection", "Connection dialog not yet implemented")
    
    def apply_component_config(self):
        """Apply configuration changes to selected component."""
        if not self.selected_component:
            messagebox.showwarning("Warning", "No component selected")
            return
        
        try:
            config_text = self.component_config_text.get(1.0, tk.END).strip()
            config_dict = json.loads(config_text)
            
            # Apply configuration based on component type
            component_info = self.canvas_components[self.selected_component]
            obj = component_info['object']
            
            if component_info['type'] == 'controller':
                obj.config = config_dict
                obj.name = self.component_name_var.get()
            
            messagebox.showinfo("Success", "Configuration applied successfully")
            self.refresh_diagram()
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON configuration: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply configuration: {e}")
    
    def delete_component(self):
        """Delete selected component."""
        if not self.selected_component:
            messagebox.showwarning("Warning", "No component selected")
            return
        
        result = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this component?")
        if result:
            component_info = self.canvas_components[self.selected_component]
            
            if component_info['type'] == 'controller':
                del self.controllers[self.selected_component]
            
            # Remove related connections
            connections_to_remove = [
                conn_id for conn_id, conn in self.connections.items()
                if conn.source_id == self.selected_component or conn.target_id == self.selected_component
            ]
            
            for conn_id in connections_to_remove:
                del self.connections[conn_id]
            
            self.selected_component = None
            self.refresh_diagram()
    
    def update_connection(self):
        """Update selected connection configuration."""
        messagebox.showinfo("Update Connection", "Connection update not yet implemented")
    
    def delete_connection(self):
        """Delete selected connection."""
        messagebox.showinfo("Delete Connection", "Connection deletion not yet implemented")
    
    def configure_controller(self):
        """Configure selected controller."""
        messagebox.showinfo("Configure Controller", "Controller configuration dialog not yet implemented")
    
    def export_config(self):
        """Export system configuration."""
        config = {
            'controllers': [ctrl.to_dict() for ctrl in self.controllers.values()],
            'connections': [conn.to_dict() for conn in self.connections.values()]
        }
        
        # This would open a file dialog to save the configuration
        messagebox.showinfo("Export", f"Would export {len(self.controllers)} controllers and {len(self.connections)} connections")
    
    def import_config(self):
        """Import system configuration."""
        # This would open a file dialog to load configuration
        messagebox.showinfo("Import", "Configuration import not yet implemented")
    
    def refresh(self):
        """Refresh the system view."""
        self.refresh_diagram()
        # Refresh other components as needed