"""
Home view widget showing top-down view of the home with sensors.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import os
from typing import Dict, List, Tuple, Optional

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from src.sensors.base_sensor import BaseSensor


class SensorWidget:
    """Visual representation of a sensor in the home view."""
    
    def __init__(self, canvas: tk.Canvas, sensor: BaseSensor, x: int, y: int):
        self.canvas = canvas
        self.sensor = sensor
        self.x = x
        self.y = y
        self.size = 20
        self.selected = False
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.create_visual()
        self.bind_events()
    
    def create_visual(self):
        """Create the visual representation of the sensor."""
        # Get sensor type color
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
        
        color = colors.get(self.sensor.get_sensor_type(), '#CCCCCC')
        
        # Create main circle
        self.circle_id = self.canvas.create_oval(
            self.x - self.size//2, self.y - self.size//2,
            self.x + self.size//2, self.y + self.size//2,
            fill=color, outline='black', width=2
        )
        
        # Create status indicator (smaller circle)
        status_colors = {
            'active': 'green',
            'inactive': 'gray',
            'error': 'red',
            'maintenance': 'orange'
        }
        status_color = status_colors.get(self.sensor.status.value, 'gray')
        
        self.status_id = self.canvas.create_oval(
            self.x + self.size//4, self.y - self.size//2,
            self.x + self.size//2, self.y - self.size//4,
            fill=status_color, outline='white', width=1
        )
        
        # Create label
        self.label_id = self.canvas.create_text(
            self.x, self.y + self.size//2 + 10,
            text=self.sensor.name[:8] + ('...' if len(self.sensor.name) > 8 else ''),
            font=('Arial', 8), anchor=tk.N
        )
        
        # Create selection indicator (initially hidden)
        self.selection_id = self.canvas.create_rectangle(
            self.x - self.size//2 - 3, self.y - self.size//2 - 3,
            self.x + self.size//2 + 3, self.y + self.size//2 + 3,
            outline='blue', width=3, state=tk.HIDDEN
        )
    
    def bind_events(self):
        """Bind mouse events to the sensor widgets."""
        for widget_id in [self.circle_id, self.status_id, self.label_id]:
            self.canvas.tag_bind(widget_id, '<Button-1>', self.on_click)
            self.canvas.tag_bind(widget_id, '<B1-Motion>', self.on_drag)
            self.canvas.tag_bind(widget_id, '<ButtonRelease-1>', self.on_release)
            self.canvas.tag_bind(widget_id, '<Button-3>', self.on_right_click)
            self.canvas.tag_bind(widget_id, '<Double-Button-1>', self.on_double_click)
    
    def on_click(self, event):
        """Handle mouse click on sensor."""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.dragging = False
        
        # Select this sensor
        self.canvas.master.select_sensor(self.sensor.sensor_id)
    
    def on_drag(self, event):
        """Handle mouse drag on sensor."""
        if not self.dragging:
            # Check if movement threshold is exceeded
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            if abs(dx) > 3 or abs(dy) > 3:
                self.dragging = True
        
        if self.dragging:
            # Calculate new position
            new_x = self.x + (event.x - self.drag_start_x)
            new_y = self.y + (event.y - self.drag_start_y)
            
            # Update position
            self.move_to(new_x, new_y)
            
            # Update drag start position
            self.drag_start_x = event.x
            self.drag_start_y = event.y
    
    def on_release(self, event):
        """Handle mouse release."""
        if self.dragging:
            # Update sensor location
            self.sensor.set_location(self.x, self.y)
            self.dragging = False
    
    def on_right_click(self, event):
        """Handle right-click context menu."""
        self.canvas.master.show_sensor_context_menu(event, self.sensor)
    
    def on_double_click(self, event):
        """Handle double-click to configure sensor."""
        self.canvas.master.configure_sensor(self.sensor)
    
    def move_to(self, x: int, y: int):
        """Move sensor widget to new position."""
        dx = x - self.x
        dy = y - self.y
        
        # Move all parts of the widget
        for widget_id in [self.circle_id, self.status_id, self.label_id, self.selection_id]:
            self.canvas.move(widget_id, dx, dy)
        
        # Update position
        self.x = x
        self.y = y
    
    def set_selected(self, selected: bool):
        """Set selection state."""
        self.selected = selected
        if selected:
            self.canvas.itemconfig(self.selection_id, state=tk.NORMAL)
        else:
            self.canvas.itemconfig(self.selection_id, state=tk.HIDDEN)
    
    def update_status(self):
        """Update visual status indicator."""
        status_colors = {
            'active': 'green',
            'inactive': 'gray',
            'error': 'red',
            'maintenance': 'orange'
        }
        status_color = status_colors.get(self.sensor.status.value, 'gray')
        self.canvas.itemconfig(self.status_id, fill=status_color)
    
    def update_reading_indicator(self, reading: Dict):
        """Update visual indicators based on sensor reading."""
        # Create temporary visual effects based on sensor readings
        if self.sensor.get_sensor_type() == 'motion' and reading.get('motion_detected'):
            # Flash motion sensor
            self.canvas.create_oval(
                self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size,
                outline='red', width=3, tags='motion_flash'
            )
            self.canvas.after(500, lambda: self.canvas.delete('motion_flash'))
        
        elif self.sensor.get_sensor_type() == 'door_window' and reading.get('is_open'):
            # Change color when door/window is open
            self.canvas.itemconfig(self.circle_id, fill='orange')
            self.canvas.after(1000, lambda: self.canvas.itemconfig(self.circle_id, fill='#45B7D1'))
        
        elif self.sensor.get_sensor_type() == 'smoke' and reading.get('alarm_active'):
            # Flash smoke alarm
            self.canvas.create_oval(
                self.x - self.size*1.5, self.y - self.size*1.5,
                self.x + self.size*1.5, self.y + self.size*1.5,
                outline='red', width=5, tags='smoke_alarm'
            )
            self.canvas.after(2000, lambda: self.canvas.delete('smoke_alarm'))
    
    def destroy(self):
        """Remove sensor widget from canvas."""
        for widget_id in [self.circle_id, self.status_id, self.label_id, self.selection_id]:
            self.canvas.delete(widget_id)


class HomeView:
    """Main home view showing top-down layout with sensors."""
    
    def __init__(self, parent, simulation_engine, logger):
        self.parent = parent
        self.sim_engine = simulation_engine
        self.logger = logger
        
        self.sensor_widgets = {}  # sensor_id -> SensorWidget
        self.selected_sensor_id = None
        self.home_template = None
        self.background_image = None  # PIL Image object
        self.background_photo = None  # PhotoImage for tkinter
        self.background_image_id = None  # Canvas image item ID
        
        self.setup_ui()
        self.setup_context_menu()
    
    def setup_ui(self):
        """Initialize the home view UI."""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Header with controls
        header = ttk.Frame(self.frame)
        header.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header, text="Home Layout", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # View controls
        controls = ttk.Frame(header)
        controls.pack(side=tk.RIGHT)
        
        ttk.Button(controls, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls, text="Reset View", command=self.reset_view).pack(side=tk.LEFT, padx=2)
        
        # Background image toggle
        self.show_background = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls, text="Show Background", 
                       variable=self.show_background, 
                       command=self.toggle_background).pack(side=tk.LEFT, padx=2)
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas
        self.canvas = tk.Canvas(
            canvas_frame, 
            bg='white', 
            width=800, 
            height=600,
            scrollregion=(0, 0, 1200, 900)
        )
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bind canvas events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<Button-3>', self.on_canvas_right_click)
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # Initialize zoom
        self.zoom_factor = 1.0
        
        # Draw default home layout
        self.draw_home_layout()
    
    def setup_context_menu(self):
        """Create context menus."""
        # Canvas context menu
        self.canvas_context_menu = tk.Menu(self.frame, tearoff=0)
        self.canvas_context_menu.add_command(label="Add Sensor Here", command=self.add_sensor_at_position)
        self.canvas_context_menu.add_separator()
        self.canvas_context_menu.add_command(label="Paste Sensor", command=self.paste_sensor, state=tk.DISABLED)
        
        # Sensor context menu
        self.sensor_context_menu = tk.Menu(self.frame, tearoff=0)
        self.sensor_context_menu.add_command(label="Configure", command=self.configure_selected_sensor)
        self.sensor_context_menu.add_command(label="Copy", command=self.copy_sensor)
        self.sensor_context_menu.add_command(label="Cut", command=self.cut_sensor)
        self.sensor_context_menu.add_separator()
        self.sensor_context_menu.add_command(label="Delete", command=self.delete_selected_sensor)
    
    def draw_home_layout(self):
        """Draw the home layout background."""
        # Clear existing layout and background elements
        self.canvas.delete('layout')
        self.canvas.delete('background')
        
        if self.home_template:
            self.draw_template_layout()
        else:
            self.draw_default_layout()
    
    def draw_default_layout(self):
        """Draw a simple default home layout."""
        # Outer walls
        self.canvas.create_rectangle(50, 50, 750, 550, outline='black', width=3, tags='layout')
        
        # Interior walls
        # Living room separator
        self.canvas.create_line(300, 50, 300, 250, fill='black', width=2, tags='layout')
        # Kitchen separator  
        self.canvas.create_line(300, 350, 750, 350, fill='black', width=2, tags='layout')
        # Bedroom separator
        self.canvas.create_line(500, 250, 500, 350, fill='black', width=2, tags='layout')
        
        # Doors (gaps in walls)
        # Main entrance
        self.canvas.create_rectangle(375, 47, 425, 53, fill='white', outline='white', tags='layout')
        # Interior doors
        self.canvas.create_rectangle(297, 275, 303, 325, fill='white', outline='white', tags='layout')
        self.canvas.create_rectangle(475, 347, 525, 353, fill='white', outline='white', tags='layout')
        
        # Room labels
        self.canvas.create_text(175, 150, text="Living Room", font=('Arial', 14), tags='layout')
        self.canvas.create_text(625, 150, text="Bedroom", font=('Arial', 14), tags='layout')
        self.canvas.create_text(400, 450, text="Kitchen", font=('Arial', 14), tags='layout')
        self.canvas.create_text(625, 300, text="Bathroom", font=('Arial', 10), tags='layout')
        
        # Furniture outlines (optional)
        # Sofa in living room
        self.canvas.create_rectangle(70, 200, 170, 230, outline='gray', fill='lightgray', tags='layout')
        # Bed in bedroom
        self.canvas.create_rectangle(520, 70, 620, 150, outline='gray', fill='lightgray', tags='layout')
        # Kitchen counter
        self.canvas.create_rectangle(320, 370, 720, 400, outline='gray', fill='lightgray', tags='layout')
    
    def draw_template_layout(self):
        """Draw layout from selected template."""
        template = self.home_template
        
        # Draw background image if available
        image_loaded = self.draw_background_image()
        
        # If an image is loaded, don't draw any architectural elements or labels
        # The image serves as the complete house layout
        if image_loaded:
            self.logger.info("Background image loaded - skipping architectural drawing")
            return
        
        # If no image, draw the traditional layout elements
        # Draw walls
        for wall in template.get('walls', []):
            self.canvas.create_line(
                wall['x1'], wall['y1'], wall['x2'], wall['y2'],
                fill='black', width=wall.get('width', 2), tags='layout'
            )
        
        # Draw rooms
        for room in template.get('rooms', []):
            if 'bounds' in room:
                bounds = room['bounds']
                self.canvas.create_rectangle(
                    bounds['x'], bounds['y'], 
                    bounds['x'] + bounds['width'], bounds['y'] + bounds['height'],
                    outline='gray', fill=room.get('color', 'white'), 
                    stipple=room.get('pattern', ''), tags='layout'
                )
            
            # Room label
            if 'label_pos' in room:
                pos = room['label_pos']
                self.canvas.create_text(
                    pos['x'], pos['y'], text=room['name'],
                    font=('Arial', 12), tags='layout'
                )
        
        # Draw furniture
        for furniture in template.get('furniture', []):
            bounds = furniture['bounds']
            self.canvas.create_rectangle(
                bounds['x'], bounds['y'],
                bounds['x'] + bounds['width'], bounds['y'] + bounds['height'],
                outline='gray', fill=furniture.get('color', 'lightgray'), tags='layout'
            )
    
    def draw_background_image(self):
        """Draw background image from template if available. Returns True if image loaded successfully."""
        if not PIL_AVAILABLE:
            self.logger.warning("PIL not available for image loading")
            return False
            
        if not self.home_template:
            self.logger.debug("No template available for image loading")
            return False
            
        image_path = self.home_template.get('image')
        if not image_path:
            self.logger.debug("No image path in template")
            return False
            
        self.logger.info(f"Attempting to load image: {image_path}")
            
        try:
            # Construct full path
            if not os.path.isabs(image_path):
                # Get project root (go up from src/gui/home_view.py to project root)
                # Current file is in src/gui/, so we need to go up 2 levels to get to project root
                current_dir = os.path.dirname(os.path.abspath(__file__))  # src/gui/
                gui_dir = os.path.dirname(current_dir)  # src/
                project_root = os.path.dirname(gui_dir)  # project root
                full_image_path = os.path.join(project_root, image_path)
            else:
                full_image_path = image_path
                
            self.logger.info(f"Full image path: {full_image_path}")
            
            if not os.path.exists(full_image_path):
                self.logger.error(f"Image file not found: {full_image_path}")
                return False
                
            # Load and resize image to fit canvas
            image = Image.open(full_image_path)
            self.logger.info(f"Image opened successfully - size: {image.size}")
            
            # Get canvas size (use scrollregion if set)
            canvas_width = 800  # Default canvas width
            canvas_height = 600  # Default canvas height
            
            # Resize image to fit canvas while maintaining aspect ratio
            image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            self.logger.info(f"Image resized to: {image.size}")
            
            # Convert to PhotoImage
            self.background_photo = ImageTk.PhotoImage(image)
            
            # Remove existing background image
            if self.background_image_id:
                self.canvas.delete(self.background_image_id)
            
            # Add to canvas (center the image in the visible area)
            self.background_image_id = self.canvas.create_image(
                400, 300, anchor=tk.CENTER, image=self.background_photo, tags='background'
            )
            
            # Ensure background image is behind other elements but visible
            self.canvas.tag_lower('background')
            
            # Force visibility - make sure it's not hidden
            self.canvas.itemconfig(self.background_image_id, state='normal')
            
            # Update canvas scroll region to include the image
            bbox = self.canvas.bbox(self.background_image_id)
            if bbox:
                x1, y1, x2, y2 = bbox
                self.canvas.configure(scrollregion=(x1-50, y1-50, x2+50, y2+50))
            
            # Apply visibility setting only after ensuring it's properly positioned
            if hasattr(self, 'show_background') and not self.show_background.get():
                self.canvas.itemconfig(self.background_image_id, state='hidden')
            
            self.logger.info(f"✓ Background image loaded successfully: {os.path.basename(full_image_path)}")
            return True
                
        except Exception as e:
            self.logger.error(f"Error loading background image {image_path}: {e}")
            import traceback
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            return False
    
    def load_background_image(self, image_path: str):
        """Load a background image for the home view."""
        if not PIL_AVAILABLE:
            self.logger.warning("PIL/Pillow not available for image support")
            return False
            
        try:
            # Construct full path if relative
            if not os.path.isabs(image_path):
                # Get project root (go up from src/gui/home_view.py to project root)
                current_dir = os.path.dirname(os.path.abspath(__file__))  # src/gui/
                gui_dir = os.path.dirname(current_dir)  # src/
                project_root = os.path.dirname(gui_dir)  # project root
                full_path = os.path.join(project_root, image_path)
            else:
                full_path = image_path
                
            if os.path.exists(full_path):
                # Update template with image path
                if not self.home_template:
                    self.home_template = {}
                self.home_template['image'] = image_path
                
                # Redraw layout with new image
                self.draw_home_layout()
                return True
            else:
                self.logger.error(f"Image file not found: {full_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading background image: {e}")
            return False
    
    def toggle_background(self):
        """Toggle background image visibility."""
        if self.background_image_id:
            if self.show_background.get():
                self.canvas.itemconfig(self.background_image_id, state='normal')
            else:
                self.canvas.itemconfig(self.background_image_id, state='hidden')
    
    def add_sensor(self, sensor: BaseSensor):
        """Add a sensor to the home view."""
        if sensor.sensor_id not in self.sensor_widgets:
            x, y = sensor.location
            widget = SensorWidget(self.canvas, sensor, x, y)
            self.sensor_widgets[sensor.sensor_id] = widget
            
            self.logger.info(f"Added sensor {sensor.name} to home view at ({x}, {y})")
    
    def remove_sensor(self, sensor_id: str):
        """Remove a sensor from the home view."""
        if sensor_id in self.sensor_widgets:
            widget = self.sensor_widgets[sensor_id]
            widget.destroy()
            del self.sensor_widgets[sensor_id]
            
            if self.selected_sensor_id == sensor_id:
                self.selected_sensor_id = None
    
    def update_sensor(self, sensor_id: str, reading: Dict):
        """Update sensor visual representation."""
        if sensor_id in self.sensor_widgets:
            widget = self.sensor_widgets[sensor_id]
            widget.update_status()
            widget.update_reading_indicator(reading)
    
    def select_sensor(self, sensor_id: str):
        """Select a sensor."""
        # Deselect previous
        if self.selected_sensor_id and self.selected_sensor_id in self.sensor_widgets:
            self.sensor_widgets[self.selected_sensor_id].set_selected(False)
        
        # Select new
        self.selected_sensor_id = sensor_id
        if sensor_id and sensor_id in self.sensor_widgets:
            self.sensor_widgets[sensor_id].set_selected(True)
    
    def on_canvas_click(self, event):
        """Handle canvas click (deselect sensors)."""
        self.select_sensor(None)
    
    def on_canvas_right_click(self, event):
        """Handle canvas right-click."""
        self.click_x = self.canvas.canvasx(event.x)
        self.click_y = self.canvas.canvasy(event.y)
        
        # Check if we can paste
        if hasattr(self, 'copied_sensor'):
            self.canvas_context_menu.entryconfig("Paste Sensor", state=tk.NORMAL)
        
        self.canvas_context_menu.post(event.x_root, event.y_root)
    
    def show_sensor_context_menu(self, event, sensor):
        """Show context menu for sensor."""
        self.select_sensor(sensor.sensor_id)
        self.sensor_context_menu.post(event.x_root, event.y_root)
    
    def configure_sensor(self, sensor):
        """Open sensor configuration dialog."""
        # This would open a configuration dialog
        messagebox.showinfo("Configure Sensor", f"Configure {sensor.name}")
    
    # Context menu actions
    def add_sensor_at_position(self):
        """Add sensor at clicked position."""
        if hasattr(self, 'click_x') and hasattr(self, 'click_y'):
            # This would open sensor selection dialog
            messagebox.showinfo("Add Sensor", f"Add sensor at ({self.click_x:.0f}, {self.click_y:.0f})")
    
    def configure_selected_sensor(self):
        """Configure currently selected sensor."""
        if self.selected_sensor_id:
            sensor = self.sim_engine.get_sensor(self.selected_sensor_id)
            if sensor:
                self.configure_sensor(sensor)
    
    def copy_sensor(self):
        """Copy selected sensor."""
        if self.selected_sensor_id:
            sensor = self.sim_engine.get_sensor(self.selected_sensor_id)
            if sensor:
                self.copied_sensor = sensor.to_dict()
    
    def cut_sensor(self):
        """Cut selected sensor."""
        self.copy_sensor()
        self.delete_selected_sensor()
    
    def paste_sensor(self):
        """Paste copied sensor at clicked position."""
        if hasattr(self, 'copied_sensor') and hasattr(self, 'click_x') and hasattr(self, 'click_y'):
            # Create new sensor from copied data
            sensor_data = self.copied_sensor.copy()
            sensor_data['location'] = (self.click_x, self.click_y)
            
            # This would create a new sensor instance
            messagebox.showinfo("Paste Sensor", f"Paste sensor at ({self.click_x:.0f}, {self.click_y:.0f})")
    
    def delete_selected_sensor(self):
        """Delete selected sensor."""
        if self.selected_sensor_id:
            result = messagebox.askyesno("Delete Sensor", "Are you sure you want to delete this sensor?")
            if result:
                self.sim_engine.remove_sensor(self.selected_sensor_id)
                self.remove_sensor(self.selected_sensor_id)
    
    # View controls
    def zoom_in(self):
        """Zoom in the view."""
        self.zoom_factor *= 1.2
        self.canvas.scale("all", 0, 0, 1.2, 1.2)
    
    def zoom_out(self):
        """Zoom out the view."""
        self.zoom_factor /= 1.2
        self.canvas.scale("all", 0, 0, 1/1.2, 1/1.2)
    
    def reset_view(self):
        """Reset zoom and pan."""
        if self.zoom_factor != 1.0:
            self.canvas.scale("all", 0, 0, 1/self.zoom_factor, 1/self.zoom_factor)
            self.zoom_factor = 1.0
        
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming."""
        if event.state & 0x4:  # Ctrl is held
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            # Normal scroll
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def load_template(self, template_data):
        """Load a home template."""
        self.logger.info(f"Loading template: {template_data.get('name', 'Unknown')}")
        self.home_template = template_data
        
        # Log image info
        if 'image' in template_data:
            self.logger.info(f"Template has image: {template_data['image']}")
        else:
            self.logger.info("Template has no image")
            
        self.draw_home_layout()
        
        # Check what was created
        if hasattr(self, 'background_image_id') and self.background_image_id:
            self.logger.info(f"Background image created with ID: {self.background_image_id}")
            
            # Check canvas items
            all_items = self.canvas.find_all()
            self.logger.info(f"Canvas has {len(all_items)} items total")
            
            bg_items = self.canvas.find_withtag('background')
            self.logger.info(f"Canvas has {len(bg_items)} background items")
            
            # Check image state
            try:
                state = self.canvas.itemcget(self.background_image_id, 'state')
                self.logger.info(f"Background image state: {state}")
                
                # Get image coordinates
                coords = self.canvas.coords(self.background_image_id)
                self.logger.info(f"Background image coordinates: {coords}")
                
                # Check if PhotoImage reference exists
                if self.background_photo:
                    self.logger.info("PhotoImage reference exists")
                else:
                    self.logger.error("PhotoImage reference is None!")
                    
            except Exception as e:
                self.logger.error(f"Error checking image state: {e}")
        
        # Add template sensors
        for sensor_data in template_data.get('sensors', []):
            # This would create sensor instances from template
            pass
    
    def refresh(self):
        """Refresh the view with current simulation state."""
        # Update all sensor widgets
        for sensor_id, widget in self.sensor_widgets.items():
            widget.update_status()
        
        # Redraw layout if needed
        if not self.canvas.find_withtag('layout'):
            self.draw_home_layout()
    
    def on_simulation_event(self, event):
        """Handle simulation events."""
        if event.event_type == 'sensor_data':
            self.update_sensor(event.sensor_id, event.data)
        elif event.event_type == 'sensor_added':
            sensor = self.sim_engine.get_sensor(event.sensor_id)
            if sensor:
                self.add_sensor(sensor)
        elif event.event_type == 'sensor_removed':
            self.remove_sensor(event.sensor_id)