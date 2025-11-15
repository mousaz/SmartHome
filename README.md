# Smart Home Simulation Application

A comprehensive Python-based smart home simulation application that provides a realistic IoT environment for testing, learning, and development.

## Features

### 🏠 Interactive Home Layout
- Top-down view of home with customizable layouts
- **Background Image Support** - Real house floor plans and layouts as background
- Drag-and-drop sensor placement and configuration  
- Pre-built home templates (Studio Apartment, Family House, Office Space) with images
- Visual indicators for sensor status and activity
- Zoom and pan controls for detailed view
- Toggle controls for background images and room labels
- Smart rendering: Images replace architectural drawings when available

### 📡 Extensible Sensor Framework
- **Temperature Sensors** - Monitor ambient temperature with configurable accuracy
- **Motion Sensors** - PIR motion detection with adjustable sensitivity
- **Door/Window Sensors** - Magnetic contact sensors for entry monitoring
- **Smoke Detectors** - Fire safety simulation with alarm capabilities
- **Light Sensors** - Ambient light level monitoring with day/night simulation
- **Humidity Sensors** - Moisture level tracking
- **Pressure Sensors** - Atmospheric pressure monitoring
- **Proximity Sensors** - Ultrasonic distance measurement

### 🤖 Automation & Rules (Framework Ready)
- Rule-based automation system (extensible architecture)
- Event-driven triggers and conditions
- Customizable actions and responses
- Rule management and testing interface

### 🔐 Security Features
- Multi-level security system (Basic, Standard, High, Critical)
- Sensor authentication simulation
- Security event logging and monitoring
- Access control and permission management
- Encrypted communication simulation

### 📊 Real-time Simulation
- Configurable simulation speed (0.1x to 10x real-time)
- Live sensor data updates
- Battery simulation and monitoring
- Performance metrics (FPS, event counts)
- Start/Pause/Stop/Reset controls

### 📝 Comprehensive Logging
- Live log viewer with filtering
- Event categorization (General, Sensor, Rule, Security, Simulation)
- Historical data analysis
- Export capabilities (JSON, CSV, TXT formats)
- Search and filter functionality

### 💾 Project Management
- Save/Load simulation projects
- Template-based quick setup
- Configuration import/export
- Auto-save functionality

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (tested platform)

### Setup
1. **Clone or download** the application to your local machine

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Dependencies
- `tkinter` - GUI framework (included with Python)
- `numpy` - Numerical computations
- `matplotlib` - Plotting and visualization
- `Pillow` - Image processing
- `cryptography` - Security features
- `pyjwt` - JSON Web Tokens
- `bcrypt` - Password hashing
- `jsonschema` - Configuration validation

## Quick Start Guide

### 1. Launch Application
```bash
cd smart_home_sim
python main.py
```

### 2. Select Home Template
- Click "Select Template" in toolbar
- Choose from Studio Apartment, Family House, or Office Space (with background images)
- Preview shows template description and house image
- Background images replace drawn walls/furniture for realistic view
- Or select "Empty House" to start from scratch

### 3. Add Sensors
- Click "Add Sensor" button
- Select sensor type (Temperature, Motion, etc.)
- Configure name and location
- Place sensor on home layout

### 4. Configure Sensors
- Double-click any sensor to configure
- Adjust parameters like accuracy, thresholds, security level
- Modify location by dragging sensors

### 5. Start Simulation
- Click "▶ Start" to begin simulation
- Monitor sensor readings and events in real-time
- View logs in the Log Viewer panel
- Check security events in Security panel

### 6. Save Your Work
- Use File → Save Project to save your configuration
- Projects include all sensors, rules, and settings
- Load projects later with File → Open Project

## User Interface Guide

### Main Window Layout
```
┌─────────────────────────────────────────────────────────────┐
│ [File] [Edit] [Simulation] [Security] [View] [Help]        │
├─────────────────────────────────────────────────────────────┤
│ [▶Start] [⏸Pause] [⏹Stop] [Template] [+Sensor] [Rules]    │ 
├─────────────────────┬───────────────────────────────────────┤
│                     │ ┌─ Sensors ──────────────────────┐   │
│    Home Layout      │ │ [Add] [Remove] [Configure]     │   │
│    (Top View)       │ │ ┌─────┬─────┬────────┬──────┐  │   │
│                     │ │ │Name │Type │Status  │Loc   │  │   │
│                     │ │ └─────┴─────┴────────┴──────┘  │   │
│                     │ └────────────────────────────────┘   │
│                     │ ┌─ Automation Rules ─────────────┐   │
│                     │ │ [Add Rule] [Edit] [Delete]     │   │
│                     │ │ ┌──────────────────────────────┐ │ │
│                     │ │ │ Rule list and status         │ │ │
│                     │ │ └──────────────────────────────┘ │ │
│                     │ └────────────────────────────────┘   │
├─────────────────────┴───────────────────────────────────────┤
│ Ready | Sensors: 5 | Rules: 2 | Time: 00:15:30 | FPS: 60  │
└─────────────────────────────────────────────────────────────┘
```

### Keyboard Shortcuts
- `Ctrl+N` - New Project
- `Ctrl+O` - Open Project  
- `Ctrl+S` - Save Project
- `Ctrl+Q` - Exit Application
- `F11` - Toggle Full Screen

### Mouse Controls
- **Left Click** - Select sensor
- **Right Click** - Context menu
- **Double Click** - Configure sensor
- **Drag** - Move sensor
- **Mouse Wheel** - Scroll view
- **Ctrl+Wheel** - Zoom in/out

### View Controls (Home Layout)
- **Zoom In/Out** - Adjust view scale
- **Reset View** - Return to default zoom and position
- **Show Background** - Toggle template background images on/off
- **Room Labels** - Show/hide room names (when using background images)

## Architecture

### Directory Structure
```
smart_home_sim/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── gui/              # User interface components
│   │   ├── main_window.py    # Main application window
│   │   ├── home_view.py      # Home layout viewer
│   │   ├── sensor_panel.py   # Sensor management panel
│   │   ├── rules_panel.py    # Rules management panel
│   │   ├── log_viewer.py     # Log display widget
│   │   ├── security_panel.py # Security management
│   │   └── templates_dialog.py # Template selection
│   ├── sensors/          # Sensor implementations
│   │   ├── base_sensor.py    # Base sensor class and registry
│   │   └── common_sensors.py # IoT sensor implementations
│   ├── simulation/       # Simulation engine
│   │   └── engine.py         # Main simulation controller
│   ├── log_system/       # Logging system
│   │   └── logger.py         # Smart home logger
│   ├── rules/           # Automation rules (framework)
│   └── security/        # Security modules (framework)
├── templates/           # Home templates
│   └── home_templates.json  # Pre-built layouts
├── config/             # Configuration files
│   └── default_settings.json # Default settings
└── logs/               # Log files (created at runtime)
```

### Extensibility

#### Adding New Sensor Types
1. Create new sensor class inheriting from `BaseSensor`
2. Implement required methods: `get_sensor_type()`, `get_reading()`, `get_default_config()`
3. Register with `sensor_registry.register_sensor_type()`

```python
class CustomSensor(BaseSensor):
    def get_sensor_type(self) -> str:
        return "custom"
    
    def get_reading(self) -> Dict[str, Any]:
        return {"value": 42}
    
    def get_default_config(self) -> Dict[str, Any]:
        return {"param1": "default"}

# Register the new sensor type
sensor_registry.register_sensor_type(CustomSensor)
```

#### Creating Custom Templates
1. Edit `templates/home_templates.json`
2. Add new template with walls, rooms, and sensors
3. Template will appear in selection dialog

## Troubleshooting

### Common Issues

**ImportError on startup:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version is 3.8+

**GUI doesn't appear:**
- Ensure tkinter is available (should be included with Python)
- Try installing python3-tk on Linux systems

**Simulation runs slowly:**
- Reduce simulation speed in Simulation menu
- Close unnecessary panels to improve performance
- Reduce number of active sensors

**Can't save/load projects:**
- Check file permissions in project directory
- Ensure sufficient disk space

### Performance Tips
- Use simulation speeds < 5x for smooth operation
- Limit active sensors to < 50 for optimal performance  
- Enable auto-scroll in log viewer for better responsiveness
- Close unused panels to reduce CPU usage

### Log Files
Application logs are stored in the `logs/` directory:
- `smarthome.log` - General application logs (rotated daily)
- `errors.log` - Error logs only (kept for 30 days)

## Development

### Contributing
The application is designed with extensibility in mind:
- Sensor framework supports easy addition of new sensor types
- Rule engine provides foundation for automation logic
- Security framework allows implementation of various auth methods
- GUI components are modular and reusable

### Future Enhancements
- Complete rule engine implementation
- Network simulation capabilities  
- Cloud integration simulation
- Machine learning integration
- Mobile device simulation
- Energy consumption modeling

## License

This project is created for educational and development purposes. Feel free to modify and extend according to your needs.

## Support

For issues, suggestions, or contributions, please refer to the project documentation or create appropriate issue reports.