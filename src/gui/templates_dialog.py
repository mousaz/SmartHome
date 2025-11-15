"""
Templates dialog for selecting home templates.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class TemplatesDialog:
    """Dialog for selecting home templates."""
    
    def __init__(self, parent, simulation_engine, logger):
        self.parent = parent
        self.sim_engine = simulation_engine
        self.logger = logger
        self.selected_template = None
        self.preview_photo = None  # Keep reference to PhotoImage
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the template selection dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Home Template")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.load_templates()
    
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="Choose a Home Template", font=('Arial', 14, 'bold'))
        header_label.pack(pady=(0, 10))
        
        # Template list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Template listbox with scrollbar
        self.template_listbox = tk.Listbox(list_frame, height=12)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        self.template_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.template_listbox.bind('<<ListboxSelect>>', self.on_template_select)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Template Preview", padding="5")
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create horizontal layout for preview content
        preview_content = ttk.Frame(preview_frame)
        preview_content.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Image preview (if available)
        self.image_frame = ttk.Frame(preview_content)
        self.image_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.preview_image_label = ttk.Label(self.image_frame, text="No Image")
        self.preview_image_label.pack()
        
        # Right side - Text description
        text_frame = ttk.Frame(preview_content)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.preview_text = tk.Text(text_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        preview_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="Select", command=self.select_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT)
        ttk.Button(buttons_frame, text="Create Custom", command=self.create_custom_clicked).pack(side=tk.LEFT)
    
    def load_templates(self):
        """Load available templates from JSON file."""
        try:
            # Load from JSON file - get project root from src/gui/templates_dialog.py
            current_dir = os.path.dirname(os.path.abspath(__file__))  # src/gui/
            gui_dir = os.path.dirname(current_dir)  # src/
            project_root = os.path.dirname(gui_dir)  # project root
            template_path = os.path.join(project_root, 'templates', 'home_templates.json')
            
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    self.templates = json.load(f)
                    
                # Add display names and compatibility fields if needed
                for key, template in self.templates.items():
                    if 'name' not in template:
                        template['name'] = template.get('name', key.replace('_', ' ').title())
                    if 'rooms' not in template:
                        # Extract room names from rooms data if available
                        template['rooms'] = [room.get('name', f'Room {i+1}') for i, room in enumerate(template.get('rooms', []))]
                    if 'suggested_sensors' not in template:
                        # Default suggested sensors
                        template['suggested_sensors'] = ["temperature", "motion", "door_window"]
            else:
                self.logger.warning(f"Template file not found: {template_path}")
                # Fallback to empty template
                self.templates = {
                    "Empty House": {
                        "name": "Empty House",
                        "description": "A basic empty house layout",
                        "rooms": ["Living Room"],
                        "suggested_sensors": ["temperature", "motion"],
                        "walls": [],
                        "sensors": []
                    }
                }
        except Exception as e:
            self.logger.error(f"Error loading templates: {e}")
            # Fallback to empty template
            self.templates = {
                "Empty House": {
                    "name": "Empty House", 
                    "description": "A basic empty house layout",
                    "rooms": ["Living Room"],
                    "suggested_sensors": ["temperature", "motion"],
                    "walls": [],
                    "sensors": []
                }
            }
        
        # Populate listbox
        for name, template in self.templates.items():
            display_name = template.get('name', name.replace('_', ' ').title())
            self.template_listbox.insert(tk.END, display_name)
        
        # Select first template by default
        if self.templates:
            self.template_listbox.selection_set(0)
            self.on_template_select(None)
    
    def on_template_select(self, event):
        """Handle template selection."""
        selection = self.template_listbox.curselection()
        if selection:
            template_display_name = self.template_listbox.get(selection[0])
            
            # Find template by display name
            template = None
            template_key = None
            for key, tmpl in self.templates.items():
                if tmpl.get('name', key.replace('_', ' ').title()) == template_display_name:
                    template = tmpl
                    template_key = key
                    break
            
            if template:
                # Update text preview
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete(1.0, tk.END)
                
                preview_text = f"Name: {template['name']}\n\n"
                preview_text += f"Description: {template['description']}\n\n"
                
                # Handle rooms based on structure
                rooms = template.get('rooms', [])
                if isinstance(rooms, list) and len(rooms) > 0 and isinstance(rooms[0], dict):
                    # Rooms are objects with names
                    room_names = [room.get('name', f'Room {i+1}') for i, room in enumerate(rooms)]
                else:
                    # Rooms are simple strings or already processed
                    room_names = rooms
                preview_text += f"Rooms: {', '.join(room_names)}\n\n"
                
                suggested_sensors = template.get('suggested_sensors', ['temperature', 'motion'])
                preview_text += f"Suggested Sensors: {', '.join(suggested_sensors)}\n\n"
                preview_text += f"Pre-installed Sensors: {len(template.get('sensors', []))}"
                
                self.preview_text.insert(1.0, preview_text)
                self.preview_text.config(state=tk.DISABLED)
                
                # Update image preview
                self.load_preview_image(template.get('image'))
    
    def load_preview_image(self, image_path):
        """Load and display preview image."""
        if not image_path or not PIL_AVAILABLE:
            self.preview_image_label.config(image='', text="No Image")
            self.preview_photo = None
            return
            
        try:
            # Construct full path
            if not os.path.isabs(image_path):
                # Get project root (go up from src/gui/templates_dialog.py to project root)
                current_dir = os.path.dirname(os.path.abspath(__file__))  # src/gui/
                gui_dir = os.path.dirname(current_dir)  # src/
                project_root = os.path.dirname(gui_dir)  # project root
                full_path = os.path.join(project_root, image_path)
            else:
                full_path = image_path
                
            if os.path.exists(full_path):
                # Load and resize image for preview
                image = Image.open(full_path)
                
                # Resize to fit preview area (max 150x150)
                image.thumbnail((150, 150), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.preview_photo = ImageTk.PhotoImage(image)
                
                # Update label
                self.preview_image_label.config(image=self.preview_photo, text="")
                
            else:
                self.preview_image_label.config(image='', text="Image Not Found")
                self.preview_photo = None
                
        except Exception as e:
            self.logger.warning(f"Could not load preview image: {e}")
            self.preview_image_label.config(image='', text="Image Error")
            self.preview_photo = None
    
    def select_clicked(self):
        """Handle Select button click."""
        selection = self.template_listbox.curselection()
        if selection:
            template_display_name = self.template_listbox.get(selection[0])
            
            # Find template by display name
            for key, template in self.templates.items():
                if template.get('name', key.replace('_', ' ').title()) == template_display_name:
                    self.selected_template = template.copy()
                    self.selected_template['_template_key'] = key  # Keep track of original key
                    break
            
            self.dialog.destroy()
        else:
            messagebox.showwarning("Warning", "Please select a template.")
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.selected_template = None
        self.dialog.destroy()
    
    def create_custom_clicked(self):
        """Handle Create Custom button click."""
        # Create an empty template
        empty_template = {
            "name": "Custom House",
            "description": "A custom house layout",
            "walls": [],
            "rooms": [],
            "furniture": [],
            "sensors": []
        }
        self.selected_template = empty_template
        self.dialog.destroy()
    
    def get_selected_template(self):
        """Get the selected template."""
        self.dialog.wait_window()
        return self.selected_template