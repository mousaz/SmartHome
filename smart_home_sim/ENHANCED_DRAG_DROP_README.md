# Enhanced Drag-and-Drop with Sensor Support and Real-Time Arrow Updates

## Overview
Enhanced the system view with comprehensive drag-and-drop functionality for all component types and improved real-time arrow management.

## 🎯 New Features Implemented

### 1. Universal Drag-and-Drop Support

#### All Component Types Now Draggable
- **System Components**: API Server, Database Server, MQTT Broker
- **Sensors**: Temperature, Motion, Door/Window, Light, Humidity, Pressure, etc.
- **Controllers**: Data Filters (diamond shape), Data Aggregators (circle shape)

#### Enhanced Drag Detection
```python
# Updated canvas click handler detects all draggable components
for tag in tags:
    if tag.startswith(('sensor_', 'controller_', 'system_')):
        draggable_component_id = tag.split('_', 1)[1]
```

### 2. Improved Arrow Management

#### Real-Time Arrow Clearing and Redrawing
- **Immediate Clearing**: Arrows disappear instantly when drag starts
- **Real-Time Updates**: Arrows redraw continuously during drag operations
- **Smooth Visual Feedback**: No orphaned arrows left on canvas

```python
def on_canvas_drag(self, event):
    if abs(dx) > 3 or abs(dy) > 3:
        # Clear old arrows before moving component
        self.clear_connection_arrows()
        
        self.move_component(self.drag_component_id, dx, dy)
        
        # Redraw arrows with updated positions for real-time feedback
        self.draw_system_connections()
```

#### Enhanced Arrow Clearing Method
```python
def clear_connection_arrows(self):
    """Clear all connection arrows from the canvas."""
    for line_ids in self.connection_lines.values():
        if isinstance(line_ids, list):
            for line_id in line_ids:
                self.canvas.delete(line_id)
        else:
            self.canvas.delete(line_ids)
    self.connection_lines.clear()
```

### 3. Comprehensive Right-Click Context Menus

#### Sensor Context Menus
- **Toggle Active**: Enable/disable sensor operation
- **View Data**: Display current sensor readings
- **Configure**: Open sensor configuration (extensible)
- **Remove**: Delete sensor from simulation

```python
def show_sensor_context_menu(self, event, sensor_id: str):
    context_menu.add_command(label="Toggle Active", command=lambda: self.toggle_sensor(sensor_id))
    context_menu.add_command(label="View Data", command=lambda: self.view_sensor_data(sensor_id))
    context_menu.add_command(label="Configure", command=lambda: self.configure_sensor(sensor_id))
    context_menu.add_command(label="Remove", command=lambda: self.remove_sensor(sensor_id))
```

#### Controller Context Menus
- **Configure**: Select controller for configuration
- **View Config**: Display controller configuration in dialog
- **Remove**: Delete controller from system

#### System Component Context Menus (Enhanced)
- **Start/Stop/Restart**: Component lifecycle management
- **View Logs**: Component-specific log viewing
- **Configure**: Component configuration dialogs

### 4. Enhanced User Experience Features

#### Visual Feedback Improvements
- **Status Indicators**: Color-coded component borders
  - Green: Running/Active
  - Gray: Stopped/Inactive
  - Red: Error state
  - Orange: Transitioning (starting/stopping)

#### Drag Experience Enhancements
- **Drag Threshold**: 3-pixel minimum movement prevents accidental drags
- **Smooth Movement**: Real-time position updates
- **Connection Tracking**: Arrows follow components immediately

#### Interactive Component Management
- **Click Selection**: Single-click selects components
- **Right-Click Actions**: Context-appropriate menu options
- **Real-Time Status**: Visual status updates during operations

### 5. Technical Implementation Details

#### Canvas Event System Enhancement
```python
# Enhanced event binding for all component types
for item_id in [rect_id, label_id]:
    self.canvas.tag_bind(item_id, '<Button-1>', lambda e, sid=sensor.sensor_id: self.select_component(sid))
    self.canvas.tag_bind(item_id, '<Button-3>', lambda e, sid=sensor.sensor_id: self.show_sensor_context_menu(e, sid))
```

#### Position Management System
- **Unified Storage**: All components stored in `canvas_components` dictionary
- **Multi-Item Movement**: Components with multiple canvas items move together
- **Position Persistence**: Drag positions maintained across operations

#### Connection Management
- **Dynamic Updates**: Arrows recalculate positions during drag
- **Color Coding**: Different connection types have distinct colors
- **Label Management**: Connection type labels update with arrows

### 6. Component-Specific Enhancements

#### Sensor Drag Support
```python
# Sensors now fully integrated into drag system
self.canvas_components[sensor.sensor_id] = {
    'type': 'sensor',
    'object': sensor,
    'position': (x, y),
    'canvas_ids': [rect_id, label_id]
}
```

#### Controller Drag Support
```python
# Controllers support both diamond (filter) and circle (aggregator) shapes
self.canvas_components[controller.controller_id] = {
    'type': 'controller',
    'object': controller,
    'position': (x, y),
    'canvas_ids': [shape_id, label_id]
}
```

#### System Component Enhanced Integration
- **Process Management**: Components remain functional when moved
- **Status Monitoring**: Real-time status display
- **Log Integration**: Component logs accessible via context menu

### 7. User Instructions

#### Basic Drag Operations
1. **Click and Hold**: Click any component (system, sensor, or controller)
2. **Drag**: Move mouse to desired location
3. **Release**: Drop component in new position
4. **Observe**: Watch arrows update automatically

#### Context Menu Usage
1. **Right-Click**: Right-click any component
2. **Select Action**: Choose from context-appropriate options
3. **Execute**: Action applies to the selected component

#### Visual Indicators
- **Component Colors**: Different types have distinct colors
- **Status Borders**: Border colors indicate operational status
- **Arrow Colors**: Connection types have specific colors
- **Labels**: Connection labels show relationship types

### 8. Benefits and Improvements

#### Enhanced Interactivity
- **Universal Dragging**: All components support drag operations
- **Context Actions**: Right-click provides relevant options
- **Real-Time Feedback**: Immediate visual response to user actions

#### Better Visual Management
- **Clear Data Flow**: Arrows show system relationships
- **Status Awareness**: Component states clearly visible
- **Flexible Layout**: Users arrange components optimally

#### Improved System Understanding
- **Component Relationships**: Visual connections show data flow
- **Interactive Exploration**: Click and drag to understand system
- **Status Monitoring**: Real-time operational awareness

### 9. Performance Optimizations

#### Efficient Rendering
- **Selective Updates**: Only redraw what's necessary
- **Canvas Management**: Proper cleanup of canvas items
- **Memory Efficiency**: No memory leaks from canvas operations

#### Smooth User Experience
- **Responsive Dragging**: No lag during drag operations
- **Immediate Feedback**: Arrow updates happen in real-time
- **Consistent Behavior**: All component types behave similarly

## Usage Examples

### Drag Any Component Type
```python
# System components, sensors, and controllers all support:
1. Click and drag to reposition
2. Right-click for context menu
3. Visual status indicators
4. Real-time arrow updates
```

### Context Menu Actions
```python
# Sensor example:
- Toggle Active: sensor.is_active = not sensor.is_active
- View Data: display sensor.read_data()
- Configure: open configuration dialog
- Remove: engine.remove_sensor(sensor_id)
```

This enhanced implementation provides a comprehensive, interactive system visualization where users can intuitively manage all components with consistent drag-and-drop behavior and real-time visual feedback.