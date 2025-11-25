"""
Device base class for home appliances and IoT devices.
"""

from abc import abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from .base_thing import BaseThing, ThingType, ThingStatus, ThingEvent


class DeviceCategory(Enum):
    """Categories of home devices."""
    LIGHTING = "lighting"
    CLIMATE = "climate" 
    SECURITY = "security"
    ENTERTAINMENT = "entertainment"
    KITCHEN = "kitchen"
    CLEANING = "cleaning"
    HVAC = "hvac"
    SMART_LOCKS = "smart_locks"
    GARAGE_DOORS = "garage_doors"
    IRRIGATION = "irrigation"
    ENERGY = "energy"
    NETWORKING = "networking"
    OTHER = "other"


class DeviceState(Enum):
    """Device operational states."""
    ON = "on"
    OFF = "off"
    STANDBY = "standby"
    SLEEP = "sleep"
    MAINTENANCE = "maintenance"
    UPDATING = "updating"
    LOCKED = "locked"
    UNLOCKED = "unlocked"


class PowerState:
    """Represents device power state and consumption."""
    
    def __init__(self, is_on: bool = False, power_consumption: float = 0.0, 
                 voltage: float = 0.0, current: float = 0.0):
        self.is_on = is_on
        self.power_consumption = power_consumption  # Watts
        self.voltage = voltage  # Volts
        self.current = current  # Amperes
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_on': self.is_on,
            'power_consumption': self.power_consumption,
            'voltage': self.voltage,
            'current': self.current,
            'last_updated': self.last_updated.isoformat()
        }


class BaseDevice(BaseThing):
    """Abstract base class for all home devices/appliances."""
    
    def __init__(self, device_id: Optional[str] = None, name: str = "", 
                 device_category: DeviceCategory = DeviceCategory.OTHER,
                 manufacturer: str = "", model: str = "", 
                 firmware_version: str = "", location: tuple = (0, 0),
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(
            thing_id=device_id, 
            name=name, 
            thing_type=ThingType.DEVICE,
            location=location,
            config=config
        )
        
        self.device_category = device_category
        self.manufacturer = manufacturer
        self.model = model
        self.firmware_version = firmware_version
        
        # Device-specific attributes
        self.device_state = DeviceState.OFF
        self.power_state = PowerState()
        self.features = []
        self.settings = {}
        self.schedules = []
        self.automation_rules = []
        
        # Device capabilities
        self.supports_dimming = False
        self.supports_color = False
        self.supports_scheduling = False
        self.supports_scenes = False
        self.supports_remote_control = False
        
        # Energy monitoring
        self.energy_usage_history = []
        self.max_power_rating = 0.0  # Maximum power consumption in watts
        
        # Maintenance info
        self.last_maintenance = None
        self.maintenance_schedule = None
        
    def get_thing_type(self) -> ThingType:
        """Return the thing type."""
        return ThingType.DEVICE
    
    @abstractmethod
    def turn_on(self) -> bool:
        """Turn the device on. Return True if successful."""
        pass
    
    @abstractmethod
    def turn_off(self) -> bool:
        """Turn the device off. Return True if successful."""
        pass
    
    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return device capabilities."""
        capabilities = ["power_control"]
        
        if self.supports_dimming:
            capabilities.append("dimming")
        if self.supports_color:
            capabilities.append("color_control")
        if self.supports_scheduling:
            capabilities.append("scheduling")
        if self.supports_scenes:
            capabilities.append("scenes")
        if self.supports_remote_control:
            capabilities.append("remote_control")
            
        return capabilities
    
    def set_device_state(self, state: DeviceState):
        """Set the device state."""
        old_state = self.device_state
        self.device_state = state
        
        self.emit_event("state_changed", {
            'old_state': old_state.value,
            'new_state': state.value,
            'timestamp': datetime.now().isoformat()
        })
    
    def update_power_state(self, is_on: bool, power_consumption: float = None, 
                          voltage: float = None, current: float = None):
        """Update the power state of the device."""
        self.power_state.is_on = is_on
        if power_consumption is not None:
            self.power_state.power_consumption = power_consumption
        if voltage is not None:
            self.power_state.voltage = voltage
        if current is not None:
            self.power_state.current = current
        self.power_state.last_updated = datetime.now()
        
        # Log energy usage
        self.energy_usage_history.append({
            'timestamp': datetime.now().isoformat(),
            'power_consumption': self.power_state.power_consumption,
            'voltage': self.power_state.voltage,
            'current': self.power_state.current
        })
        
        # Keep only last 1000 entries
        if len(self.energy_usage_history) > 1000:
            self.energy_usage_history = self.energy_usage_history[-1000:]
        
        self.emit_event("power_state_changed", self.power_state.to_dict())
    
    def add_feature(self, feature_name: str, feature_config: Dict[str, Any] = None):
        """Add a feature to the device."""
        feature = {
            'name': feature_name,
            'config': feature_config or {},
            'enabled': True,
            'added_at': datetime.now().isoformat()
        }
        self.features.append(feature)
        
        self.emit_event("feature_added", {
            'feature': feature_name,
            'config': feature_config
        })
    
    def remove_feature(self, feature_name: str):
        """Remove a feature from the device."""
        self.features = [f for f in self.features if f['name'] != feature_name]
        
        self.emit_event("feature_removed", {
            'feature': feature_name
        })
    
    def get_feature(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific feature configuration."""
        for feature in self.features:
            if feature['name'] == feature_name:
                return feature
        return None
    
    def update_setting(self, setting_name: str, value: Any):
        """Update a device setting."""
        old_value = self.settings.get(setting_name)
        self.settings[setting_name] = value
        
        self.emit_event("setting_changed", {
            'setting': setting_name,
            'old_value': old_value,
            'new_value': value
        })
    
    def get_setting(self, setting_name: str, default_value: Any = None) -> Any:
        """Get a device setting value."""
        return self.settings.get(setting_name, default_value)
    
    def add_schedule(self, schedule_name: str, schedule_config: Dict[str, Any]):
        """Add a schedule to the device."""
        schedule = {
            'name': schedule_name,
            'config': schedule_config,
            'enabled': True,
            'created_at': datetime.now().isoformat(),
            'last_run': None
        }
        self.schedules.append(schedule)
        
        self.emit_event("schedule_added", {
            'schedule': schedule_name,
            'config': schedule_config
        })
    
    def remove_schedule(self, schedule_name: str):
        """Remove a schedule from the device."""
        self.schedules = [s for s in self.schedules if s['name'] != schedule_name]
        
        self.emit_event("schedule_removed", {
            'schedule': schedule_name
        })
    
    def get_energy_statistics(self) -> Dict[str, Any]:
        """Get energy usage statistics."""
        if not self.energy_usage_history:
            return {
                'total_consumption': 0.0,
                'average_consumption': 0.0,
                'peak_consumption': 0.0,
                'usage_hours': 0.0
            }
        
        consumptions = [entry['power_consumption'] for entry in self.energy_usage_history]
        
        return {
            'total_consumption': sum(consumptions),
            'average_consumption': sum(consumptions) / len(consumptions),
            'peak_consumption': max(consumptions),
            'min_consumption': min(consumptions),
            'usage_hours': len(self.energy_usage_history),  # Approximate
            'history_entries': len(self.energy_usage_history)
        }
    
    def perform_maintenance(self, maintenance_type: str, notes: str = ""):
        """Record maintenance performed on the device."""
        maintenance_record = {
            'type': maintenance_type,
            'timestamp': datetime.now().isoformat(),
            'notes': notes,
            'performed_by': 'system'  # Could be enhanced to track user
        }
        
        self.last_maintenance = maintenance_record
        
        self.emit_event("maintenance_performed", maintenance_record)
    
    def is_due_for_maintenance(self) -> bool:
        """Check if device is due for maintenance."""
        if not self.maintenance_schedule or not self.last_maintenance:
            return True
            
        # Simple check based on days since last maintenance
        last_maintenance_date = datetime.fromisoformat(
            self.last_maintenance['timestamp'].replace('Z', '+00:00')
        )
        days_since_maintenance = (datetime.now() - last_maintenance_date).days
        
        maintenance_interval_days = self.maintenance_schedule.get('interval_days', 365)
        
        return days_since_maintenance >= maintenance_interval_days
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get comprehensive device status information."""
        base_info = super().get_status_info()
        
        device_info = {
            'device_category': self.device_category.value,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'firmware_version': self.firmware_version,
            'device_state': self.device_state.value,
            'power_state': self.power_state.to_dict(),
            'features': self.features.copy(),
            'settings': self.settings.copy(),
            'schedules': self.schedules.copy(),
            'energy_statistics': self.get_energy_statistics(),
            'last_maintenance': self.last_maintenance,
            'maintenance_due': self.is_due_for_maintenance(),
            'max_power_rating': self.max_power_rating
        }
        
        # Merge with base thing info
        base_info.update(device_info)
        return base_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary representation."""
        return self.get_status_info()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseDevice':
        """Create device instance from dictionary."""
        device = cls(
            device_id=data.get('thing_id'),
            name=data.get('name', ''),
            device_category=DeviceCategory(data.get('device_category', 'other')),
            manufacturer=data.get('manufacturer', ''),
            model=data.get('model', ''),
            firmware_version=data.get('firmware_version', ''),
            location=tuple(data.get('location', (0, 0))),
            config=data.get('config', {})
        )
        
        # Restore device-specific state
        if 'device_state' in data:
            device.device_state = DeviceState(data['device_state'])
        
        if 'power_state' in data:
            power_data = data['power_state']
            device.power_state = PowerState(
                is_on=power_data.get('is_on', False),
                power_consumption=power_data.get('power_consumption', 0.0),
                voltage=power_data.get('voltage', 0.0),
                current=power_data.get('current', 0.0)
            )
        
        device.features = data.get('features', [])
        device.settings = data.get('settings', {})
        device.schedules = data.get('schedules', [])
        device.max_power_rating = data.get('max_power_rating', 0.0)
        device.last_maintenance = data.get('last_maintenance')
        
        return device