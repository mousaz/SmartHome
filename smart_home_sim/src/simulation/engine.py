"""
Main simulation engine that orchestrates the smart home simulation.
"""

import threading
import time
import json
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum

from src.sensors.base_sensor import BaseSensor, SensorEvent, sensor_registry
from src.sensors.common_sensors import *


class SimulationState(Enum):
    """Simulation state enumeration."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class SimulationEngine:
    """Core simulation engine managing sensors, rules, and events."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.state = SimulationState.STOPPED
        
        # Core components
        self.sensors = {}  # sensor_id -> BaseSensor
        self.rules = {}    # rule_id -> Rule
        self.event_callbacks = []
        
        # Simulation parameters
        self.simulation_speed = 1.0  # 1.0 = real-time
        self.update_interval = 1.0   # seconds
        self.start_time = None
        self.simulation_time = datetime.now()
        
        # Threading
        self.simulation_thread = None
        self.stop_event = threading.Event()
        
        # Statistics
        self.total_events = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        
        # Project management
        self.project_modified = False
        
        self.log_info("Simulation engine initialized")
    
    def log_info(self, message: str):
        """Log an info message."""
        if self.logger:
            self.logger.info(message)
        else:
            print(f"INFO: {message}")
    
    def log_error(self, message: str):
        """Log an error message."""
        if self.logger:
            self.logger.error(message)
        else:
            print(f"ERROR: {message}")
    
    # Sensor management
    def add_sensor(self, sensor: BaseSensor) -> bool:
        """Add a sensor to the simulation."""
        try:
            if sensor.sensor_id in self.sensors:
                self.log_error(f"Sensor {sensor.sensor_id} already exists")
                return False
            
            # Add event callback to sensor
            sensor.add_event_callback(self.on_sensor_event)
            
            # Store sensor
            self.sensors[sensor.sensor_id] = sensor
            
            # Emit add event
            self.emit_event("sensor_added", {
                "sensor_id": sensor.sensor_id,
                "sensor_type": sensor.get_sensor_type(),
                "location": sensor.location
            })
            
            self.project_modified = True
            self.log_info(f"Added sensor: {sensor.name} ({sensor.get_sensor_type()})")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to add sensor: {str(e)}")
            return False
    
    def remove_sensor(self, sensor_id: str) -> bool:
        """Remove a sensor from the simulation."""
        try:
            if sensor_id not in self.sensors:
                self.log_error(f"Sensor {sensor_id} not found")
                return False
            
            sensor = self.sensors[sensor_id]
            
            # Remove from sensors dict
            del self.sensors[sensor_id]
            
            # Emit remove event
            self.emit_event("sensor_removed", {
                "sensor_id": sensor_id,
                "sensor_type": sensor.get_sensor_type()
            })
            
            self.project_modified = True
            self.log_info(f"Removed sensor: {sensor.name}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to remove sensor: {str(e)}")
            return False
    
    def get_sensor(self, sensor_id: str) -> Optional[BaseSensor]:
        """Get a sensor by ID."""
        return self.sensors.get(sensor_id)
    
    def get_sensors(self) -> Dict[str, BaseSensor]:
        """Get all sensors."""
        return self.sensors.copy()
    
    def get_sensors_by_type(self, sensor_type: str) -> List[BaseSensor]:
        """Get all sensors of a specific type."""
        return [sensor for sensor in self.sensors.values() 
                if sensor.get_sensor_type() == sensor_type]
    
    def create_sensor_from_template(self, sensor_data: Dict[str, Any]) -> Optional[BaseSensor]:
        """Create a sensor instance from template data."""
        try:
            sensor_type = sensor_data.get('type')
            if not sensor_type:
                self.log_error("Sensor template missing 'type' field")
                return None
            
            # Create sensor using registry
            sensor = sensor_registry.create_sensor(
                sensor_type,
                name=sensor_data.get('name', f"{sensor_type}_sensor"),
                location=tuple(sensor_data.get('location', [100, 100])),
                config=sensor_data.get('config', {})
            )
            
            if sensor:
                # Apply additional template properties
                if 'sensor_id' in sensor_data:
                    sensor.sensor_id = sensor_data['sensor_id']
                
                if 'status' in sensor_data:
                    sensor.status = sensor_data['status']
                
                self.log_info(f"Created sensor from template: {sensor.name} ({sensor_type})")
                return sensor
            else:
                self.log_error(f"Failed to create sensor of type: {sensor_type}")
                return None
                
        except Exception as e:
            self.log_error(f"Error creating sensor from template: {str(e)}")
            return None
    
    # Rules management (placeholder)
    def add_rule(self, rule) -> bool:
        """Add an automation rule."""
        # Placeholder - full implementation would be in rules module
        return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove an automation rule."""
        # Placeholder
        return True
    
    def get_rules(self) -> Dict:
        """Get all rules."""
        return self.rules.copy()
    
    # Event system
    def add_event_callback(self, callback: Callable[[SensorEvent], None]):
        """Add callback for simulation events."""
        self.event_callbacks.append(callback)
    
    def remove_event_callback(self, callback: Callable[[SensorEvent], None]):
        """Remove event callback."""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit a simulation event."""
        event = SensorEvent("simulation", event_type, data)
        self.total_events += 1
        
        # Call all registered callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.log_error(f"Error in event callback: {str(e)}")
    
    def on_sensor_event(self, event: SensorEvent):
        """Handle events from sensors."""
        # Forward sensor events to simulation callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.log_error(f"Error forwarding sensor event: {str(e)}")
        
        # Process rules (placeholder)
        self.process_rules(event)
    
    def process_rules(self, event: SensorEvent):
        """Process automation rules for an event."""
        # Placeholder for rule processing
        pass
    
    # Simulation control
    def start(self):
        """Start the simulation."""
        if self.state == SimulationState.RUNNING:
            self.log_info("Simulation already running")
            return
        
        self.state = SimulationState.RUNNING
        self.start_time = datetime.now()
        self.stop_event.clear()
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        
        # Activate all sensors
        for sensor in self.sensors.values():
            sensor.activate()
        
        self.emit_event("simulation_started", {"start_time": self.start_time.isoformat()})
        self.log_info("Simulation started")
    
    def pause(self):
        """Pause the simulation."""
        if self.state == SimulationState.RUNNING:
            self.state = SimulationState.PAUSED
            self.emit_event("simulation_paused", {})
            self.log_info("Simulation paused")
    
    def stop(self):
        """Stop the simulation."""
        if self.state == SimulationState.STOPPED:
            return
        
        self.state = SimulationState.STOPPED
        self.stop_event.set()
        
        # Wait for simulation thread to finish
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=2.0)
        
        # Deactivate all sensors
        for sensor in self.sensors.values():
            sensor.deactivate()
        
        self.emit_event("simulation_stopped", {})
        self.log_info("Simulation stopped")
    
    def reset(self):
        """Reset the simulation."""
        was_running = self.state == SimulationState.RUNNING
        
        if was_running:
            self.stop()
        
        # Reset simulation time
        self.simulation_time = datetime.now()
        self.start_time = None
        self.total_events = 0
        self.fps_counter = 0
        
        # Reset sensors
        for sensor in self.sensors.values():
            sensor.last_reading = None
            sensor.last_update = None
            sensor.battery_level = 100.0
        
        self.emit_event("simulation_reset", {})
        self.log_info("Simulation reset")
        
        if was_running:
            self.start()
    
    def _simulation_loop(self):
        """Main simulation loop running in separate thread."""
        last_update_time = time.time()
        
        while not self.stop_event.is_set() and self.state != SimulationState.STOPPED:
            loop_start_time = time.time()
            
            # Check if paused
            if self.state == SimulationState.PAUSED:
                time.sleep(0.1)
                continue
            
            # Calculate time delta
            current_time = time.time()
            time_delta = (current_time - last_update_time) * self.simulation_speed
            
            # Update simulation time
            self.simulation_time += timedelta(seconds=time_delta)
            
            # Update all sensors
            self._update_sensors()
            
            # Update FPS counter
            self._update_fps_counter()
            
            # Sleep to maintain update interval
            loop_duration = time.time() - loop_start_time
            sleep_time = max(0, self.update_interval - loop_duration)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            last_update_time = current_time
    
    def _update_sensors(self):
        """Update all sensors in the simulation."""
        for sensor in self.sensors.values():
            try:
                # Update sensor and get reading if changed
                reading = sensor.update()
                
                # Simulate battery drain
                sensor.simulate_battery_drain(0.001)  # Very slow drain
                
            except Exception as e:
                self.log_error(f"Error updating sensor {sensor.sensor_id}: {str(e)}")
    
    def _update_fps_counter(self):
        """Update FPS counter."""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:  # Update every second
            self.current_fps = self.fps_counter / (current_time - self.last_fps_time)
            self.fps_counter = 0
            self.last_fps_time = current_time
    
    # Template and project management
    def load_template(self, template_data: Dict[str, Any]):
        """Load a home template."""
        try:
            # Clear existing sensors
            self.sensors.clear()
            
            # Load sensors from template
            for sensor_data in template_data.get('sensors', []):
                sensor = self.create_sensor(sensor_data)
                
                if sensor:
                    self.add_sensor(sensor)
            
            self.emit_event("template_loaded", {"template": template_data.get('name', 'Unknown')})
            self.log_info(f"Loaded template: {template_data.get('name', 'Unknown')}")
            
        except Exception as e:
            self.log_error(f"Failed to load template: {str(e)}")

    def create_sensor(self, sensor_data: Dict[str, Any]):
        return sensor_registry.create_sensor(
                    sensor_data['type'],
                    name=sensor_data.get('name', f"{sensor_data['type']}_sensor"),
                    location=tuple(sensor_data.get('location', [100, 100])),
                    config=sensor_data.get('config', {})
                )
    
    def save_project(self, filename: str):
        """Save current project to file."""
        try:
            project_data = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'sensors': [sensor.to_dict() for sensor in self.sensors.values()],
                'rules': list(self.rules.values()),
                'settings': {
                    'simulation_speed': self.simulation_speed,
                    'update_interval': self.update_interval
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            self.project_modified = False
            self.log_info(f"Project saved to: {filename}")
            
        except Exception as e:
            self.log_error(f"Failed to save project: {str(e)}")
            raise
    
    def load_project(self, filename: str):
        """Load project from file."""
        try:
            with open(filename, 'r') as f:
                project_data = json.load(f)
            
            # Clear current state
            self.stop()
            self.sensors.clear()
            self.rules.clear()
            
            # Load sensors
            for sensor_data in project_data.get('sensors', []):
                # Recreate sensor from data
                sensor_class = sensor_registry.get_available_types().get(sensor_data.get('type'))
                if sensor_class:
                    sensor = sensor_class.from_dict(sensor_data)
                    self.add_sensor(sensor)
            
            # Load settings
            settings = project_data.get('settings', {})
            self.simulation_speed = settings.get('simulation_speed', 1.0)
            self.update_interval = settings.get('update_interval', 1.0)
            
            self.project_modified = False
            self.log_info(f"Project loaded from: {filename}")
            
        except Exception as e:
            self.log_error(f"Failed to load project: {str(e)}")
            raise
    
    # Getters for UI
    def get_simulation_time(self) -> str:
        """Get formatted simulation time."""
        if self.start_time:
            elapsed = self.simulation_time - self.start_time
            hours, remainder = divmod(elapsed.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        return "00:00:00"
    
    def get_fps(self) -> float:
        """Get current FPS."""
        return self.current_fps
    
    def get_state(self) -> SimulationState:
        """Get current simulation state."""
        return self.state
    
    def is_modified(self) -> bool:
        """Check if project has been modified."""
        return self.project_modified
    
    def set_simulation_speed(self, speed: float):
        """Set simulation speed multiplier."""
        self.simulation_speed = max(0.1, min(10.0, speed))
        self.emit_event("speed_changed", {"speed": self.simulation_speed})
    
    def set_update_interval(self, interval: float):
        """Set simulation update interval."""
        self.update_interval = max(0.1, min(10.0, interval))