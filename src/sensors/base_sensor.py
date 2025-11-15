"""
Base sensor class providing the foundation for all sensor implementations.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, Callable
import uuid
import time
import json
from datetime import datetime


class SensorStatus(Enum):
    """Sensor operational status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class SensorEvent:
    """Represents a sensor event with timestamp and data."""
    
    def __init__(self, sensor_id: str, event_type: str, data: Dict[str, Any], 
                 timestamp: Optional[datetime] = None):
        self.sensor_id = sensor_id
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now()
        self.event_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'sensor_id': self.sensor_id,
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


class BaseSensor(ABC):
    """Abstract base class for all sensors."""
    
    def __init__(self, sensor_id: str = None, name: str = "", location: tuple = (0, 0),
                 config: Dict[str, Any] = None):
        self.sensor_id = sensor_id or str(uuid.uuid4())
        self.name = name or f"{self.get_sensor_type()}_{self.sensor_id[:8]}"
        self.location = location  # (x, y) coordinates
        self.config = config or {}
        self.status = SensorStatus.INACTIVE
        self.last_reading = None
        self.last_update = None
        self.event_callbacks = []
        self.security_level = self.config.get('security_level', 'basic')
        self.authenticated = False
        
        # Sensor metadata
        self.install_date = datetime.now()
        self.battery_level = 100.0  # Percentage
        self.firmware_version = "1.0.0"
    
    @abstractmethod
    def get_sensor_type(self) -> str:
        """Return the sensor type identifier."""
        pass
    
    @abstractmethod
    def get_reading(self) -> Dict[str, Any]:
        """Get current sensor reading."""
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration for this sensor type."""
        pass
    
    def update_config(self, config: Dict[str, Any]) -> bool:
        """Update sensor configuration."""
        try:
            self.validate_config(config)
            self.config.update(config)
            self.on_config_updated()
            return True
        except Exception as e:
            self.emit_event("config_error", {"error": str(e)})
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration parameters."""
        # Base validation - can be overridden by subclasses
        return True
    
    def on_config_updated(self):
        """Called after configuration is updated."""
        pass
    
    def activate(self) -> bool:
        """Activate the sensor."""
        if self.authenticate():
            self.status = SensorStatus.ACTIVE
            self.emit_event("sensor_activated", {})
            return True
        return False
    
    def deactivate(self):
        """Deactivate the sensor."""
        self.status = SensorStatus.INACTIVE
        self.emit_event("sensor_deactivated", {})
    
    def authenticate(self) -> bool:
        """Authenticate sensor based on security level."""
        # Basic implementation - can be enhanced by security module
        self.authenticated = True
        return True
    
    def update(self) -> Optional[Dict[str, Any]]:
        """Update sensor and return reading if status changed."""
        if self.status != SensorStatus.ACTIVE:
            return None
        
        try:
            current_reading = self.get_reading()
            
            # Check if reading has changed significantly
            if self.has_significant_change(current_reading):
                self.last_reading = current_reading
                self.last_update = datetime.now()
                
                # Emit sensor data event
                self.emit_event("sensor_data", current_reading)
                
                return current_reading
            
            return None
            
        except Exception as e:
            self.status = SensorStatus.ERROR
            self.emit_event("sensor_error", {"error": str(e)})
            return None
    
    def has_significant_change(self, new_reading: Dict[str, Any]) -> bool:
        """Determine if the new reading represents a significant change."""
        if self.last_reading is None:
            return True
        
        # Default implementation - can be overridden by specific sensors
        return new_reading != self.last_reading
    
    def add_event_callback(self, callback: Callable[[SensorEvent], None]):
        """Add callback function for sensor events."""
        self.event_callbacks.append(callback)
    
    def remove_event_callback(self, callback: Callable[[SensorEvent], None]):
        """Remove event callback."""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit a sensor event to all registered callbacks."""
        event = SensorEvent(self.sensor_id, event_type, data)
        
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get comprehensive sensor information."""
        return {
            'sensor_id': self.sensor_id,
            'name': self.name,
            'type': self.get_sensor_type(),
            'location': self.location,
            'status': self.status.value,
            'config': self.config,
            'last_reading': self.last_reading,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'battery_level': self.battery_level,
            'firmware_version': self.firmware_version,
            'install_date': self.install_date.isoformat(),
            'authenticated': self.authenticated,
            'security_level': self.security_level
        }
    
    def set_location(self, x: int, y: int):
        """Update sensor location."""
        old_location = self.location
        self.location = (x, y)
        self.emit_event("location_changed", {
            "old_location": old_location,
            "new_location": self.location
        })
    
    def simulate_battery_drain(self, drain_rate: float = 0.01):
        """Simulate battery drainage."""
        if self.status == SensorStatus.ACTIVE:
            self.battery_level = max(0, self.battery_level - drain_rate)
            if self.battery_level <= 10:
                self.emit_event("low_battery", {"battery_level": self.battery_level})
            if self.battery_level <= 0:
                self.status = SensorStatus.ERROR
                self.emit_event("battery_dead", {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize sensor to dictionary."""
        return self.get_info()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseSensor':
        """Create sensor instance from dictionary."""
        # This should be overridden by subclasses
        raise NotImplementedError("Subclasses must implement from_dict method")


class SensorRegistry:
    """Registry for managing sensor types and instances."""
    
    def __init__(self):
        self._sensor_types = {}
        self._instances = {}
    
    def register_sensor_type(self, sensor_class):
        """Register a sensor type."""
        sensor_type = sensor_class.get_sensor_type(sensor_class())
        self._sensor_types[sensor_type] = sensor_class
    
    def create_sensor(self, sensor_type: str, **kwargs) -> Optional[BaseSensor]:
        """Create a sensor instance of the specified type."""
        if sensor_type not in self._sensor_types:
            return None
        
        sensor_class = self._sensor_types[sensor_type]
        instance = sensor_class(**kwargs)
        self._instances[instance.sensor_id] = instance
        return instance
    
    def get_sensor(self, sensor_id: str) -> Optional[BaseSensor]:
        """Get sensor instance by ID."""
        return self._instances.get(sensor_id)
    
    def remove_sensor(self, sensor_id: str) -> bool:
        """Remove sensor instance."""
        if sensor_id in self._instances:
            del self._instances[sensor_id]
            return True
        return False
    
    def get_all_sensors(self) -> Dict[str, BaseSensor]:
        """Get all sensor instances."""
        return self._instances.copy()
    
    def get_available_types(self) -> Dict[str, type]:
        """Get all available sensor types."""
        return self._sensor_types.copy()


# Global sensor registry
sensor_registry = SensorRegistry()