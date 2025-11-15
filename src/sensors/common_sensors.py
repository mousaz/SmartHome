"""
Common IoT sensor implementations.
"""

import random
import math
from typing import Dict, Any
from src.sensors.base_sensor import BaseSensor, sensor_registry


class TemperatureSensor(BaseSensor):
    """Temperature sensor implementation."""
    
    def get_sensor_type(self) -> str:
        return "temperature"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'min_temp': -40.0,
            'max_temp': 85.0,
            'accuracy': 0.5,
            'units': 'celsius',
            'sample_rate': 1.0,
            'threshold_change': 0.5
        }
    
    def get_reading(self) -> Dict[str, Any]:
        # Simulate temperature with some realistic variation
        base_temp = self.config.get('base_temp', 22.0)
        variation = random.gauss(0, self.config.get('accuracy', 0.5))
        temperature = base_temp + variation
        
        # Clamp to sensor limits
        temperature = max(self.config.get('min_temp', -40.0),
                         min(temperature, self.config.get('max_temp', 85.0)))
        
        return {
            'temperature': round(temperature, 1),
            'units': self.config.get('units', 'celsius'),
            'accuracy': self.config.get('accuracy', 0.5)
        }
    
    def has_significant_change(self, new_reading: Dict[str, Any]) -> bool:
        if self.last_reading is None:
            return True
        
        threshold = self.config.get('threshold_change', 0.5)
        temp_diff = abs(new_reading['temperature'] - self.last_reading['temperature'])
        return temp_diff >= threshold
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemperatureSensor':
        """Create sensor from dictionary data."""
        return cls(
            sensor_id=data.get('sensor_id'),
            name=data.get('name', ''),
            location=tuple(data.get('location', [0, 0])),
            config=data.get('config', {})
        )


class MotionSensor(BaseSensor):
    """PIR Motion sensor implementation."""
    
    def get_sensor_type(self) -> str:
        return "motion"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'detection_range': 5.0,  # meters
            'detection_angle': 90,   # degrees
            'sensitivity': 0.7,
            'trigger_probability': 0.1,  # For simulation
            'timeout': 30  # seconds before motion stops
        }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.motion_detected = False
        self.last_motion_time = None
    
    def get_reading(self) -> Dict[str, Any]:
        # Simulate motion detection
        trigger_prob = self.config.get('trigger_probability', 0.1)
        
        if random.random() < trigger_prob:
            self.motion_detected = True
            import time
            self.last_motion_time = time.time()
        else:
            # Check if motion timeout has passed
            if self.last_motion_time:
                import time
                timeout = self.config.get('timeout', 30)
                if time.time() - self.last_motion_time > timeout:
                    self.motion_detected = False
                    self.last_motion_time = None
        
        return {
            'motion_detected': self.motion_detected,
            'detection_range': self.config.get('detection_range', 5.0),
            'sensitivity': self.config.get('sensitivity', 0.7)
        }


class DoorWindowSensor(BaseSensor):
    """Door/Window open/close sensor implementation."""
    
    def get_sensor_type(self) -> str:
        return "door_window"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'sensor_type': 'door',  # 'door' or 'window'
            'magnetic_strength': 0.8,
            'tamper_detection': True,
            'state_change_probability': 0.05  # For simulation
        }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_open = False
        self.tampered = False
    
    def get_reading(self) -> Dict[str, Any]:
        # Simulate state changes
        change_prob = self.config.get('state_change_probability', 0.05)
        
        if random.random() < change_prob:
            self.is_open = not self.is_open
        
        # Simulate occasional tamper detection
        if self.config.get('tamper_detection', True):
            self.tampered = random.random() < 0.001  # Very low probability
        
        return {
            'is_open': self.is_open,
            'sensor_type': self.config.get('sensor_type', 'door'),
            'tampered': self.tampered,
            'magnetic_strength': self.config.get('magnetic_strength', 0.8)
        }


class SmokeSensor(BaseSensor):
    """Smoke/Fire detection sensor implementation."""
    
    def get_sensor_type(self) -> str:
        return "smoke"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'smoke_threshold': 50,  # PPM
            'sensitivity': 'medium',  # low, medium, high
            'test_mode': False,
            'alarm_probability': 0.001  # Very low for safety simulation
        }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.smoke_level = 0
        self.alarm_active = False
    
    def get_reading(self) -> Dict[str, Any]:
        # Simulate smoke levels
        if not self.config.get('test_mode', False):
            alarm_prob = self.config.get('alarm_probability', 0.001)
            if random.random() < alarm_prob:
                self.smoke_level = random.randint(60, 100)
                self.alarm_active = True
            else:
                self.smoke_level = max(0, self.smoke_level - random.randint(1, 5))
                if self.smoke_level < self.config.get('smoke_threshold', 50):
                    self.alarm_active = False
        
        return {
            'smoke_level': self.smoke_level,
            'alarm_active': self.alarm_active,
            'threshold': self.config.get('smoke_threshold', 50),
            'sensitivity': self.config.get('sensitivity', 'medium')
        }


class LightSensor(BaseSensor):
    """Ambient light sensor implementation."""
    
    def get_sensor_type(self) -> str:
        return "light"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'max_lux': 10000,
            'calibration_offset': 0,
            'day_night_simulation': True,
            'threshold_change': 50  # lux
        }
    
    def get_reading(self) -> Dict[str, Any]:
        # Simulate light levels based on time of day
        if self.config.get('day_night_simulation', True):
            import datetime
            hour = datetime.datetime.now().hour
            
            if 6 <= hour <= 18:  # Daytime
                base_lux = random.randint(500, 2000)
            else:  # Nighttime
                base_lux = random.randint(0, 50)
        else:
            base_lux = random.randint(0, self.config.get('max_lux', 10000))
        
        # Add some variation
        variation = random.gauss(0, base_lux * 0.1)
        lux = max(0, base_lux + variation + self.config.get('calibration_offset', 0))
        
        return {
            'lux': round(lux, 1),
            'max_lux': self.config.get('max_lux', 10000),
            'is_dark': lux < 50
        }
    
    def has_significant_change(self, new_reading: Dict[str, Any]) -> bool:
        if self.last_reading is None:
            return True
        
        threshold = self.config.get('threshold_change', 50)
        lux_diff = abs(new_reading['lux'] - self.last_reading['lux'])
        return lux_diff >= threshold


class HumiditySensor(BaseSensor):
    """Humidity sensor implementation."""
    
    def get_sensor_type(self) -> str:
        return "humidity"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'min_humidity': 0,
            'max_humidity': 100,
            'accuracy': 2.0,
            'threshold_change': 2.0
        }
    
    def get_reading(self) -> Dict[str, Any]:
        # Simulate humidity with realistic variation
        base_humidity = self.config.get('base_humidity', 45.0)
        variation = random.gauss(0, self.config.get('accuracy', 2.0))
        humidity = base_humidity + variation
        
        # Clamp to valid range
        humidity = max(0, min(100, humidity))
        
        return {
            'humidity': round(humidity, 1),
            'units': 'percent',
            'accuracy': self.config.get('accuracy', 2.0)
        }
    
    def has_significant_change(self, new_reading: Dict[str, Any]) -> bool:
        if self.last_reading is None:
            return True
        
        threshold = self.config.get('threshold_change', 2.0)
        humidity_diff = abs(new_reading['humidity'] - self.last_reading['humidity'])
        return humidity_diff >= threshold


class PressureSensor(BaseSensor):
    """Atmospheric pressure sensor implementation."""
    
    def get_sensor_type(self) -> str:
        return "pressure"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'min_pressure': 300,   # hPa
            'max_pressure': 1100,  # hPa
            'accuracy': 1.0,
            'units': 'hPa',
            'sea_level_correction': True
        }
    
    def get_reading(self) -> Dict[str, Any]:
        # Simulate atmospheric pressure around standard values
        base_pressure = 1013.25  # Standard atmospheric pressure
        variation = random.gauss(0, self.config.get('accuracy', 1.0))
        pressure = base_pressure + variation + random.randint(-50, 50)
        
        # Clamp to sensor limits
        pressure = max(self.config.get('min_pressure', 300),
                      min(pressure, self.config.get('max_pressure', 1100)))
        
        return {
            'pressure': round(pressure, 1),
            'units': self.config.get('units', 'hPa'),
            'sea_level_corrected': self.config.get('sea_level_correction', True)
        }


class ProximitySensor(BaseSensor):
    """Ultrasonic proximity sensor implementation."""
    
    def get_sensor_type(self) -> str:
        return "proximity"
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            'max_range': 400,  # cm
            'min_range': 2,    # cm
            'accuracy': 1.0,   # cm
            'detection_angle': 30  # degrees
        }
    
    def get_reading(self) -> Dict[str, Any]:
        # Simulate distance measurement
        max_range = self.config.get('max_range', 400)
        min_range = self.config.get('min_range', 2)
        
        # Random distance within range, with some probability of no object
        if random.random() < 0.3:  # 30% chance of no object detected
            distance = max_range + 1  # Beyond range
        else:
            distance = random.randint(min_range, max_range)
        
        # Add measurement noise
        accuracy = self.config.get('accuracy', 1.0)
        noise = random.gauss(0, accuracy)
        distance += noise
        
        object_detected = distance <= max_range
        
        return {
            'distance': round(max(0, distance), 1),
            'object_detected': object_detected,
            'max_range': max_range,
            'units': 'cm'
        }


# Add from_dict methods to all sensor classes
def add_from_dict_method(cls):
    """Add from_dict class method to sensor class."""
    @classmethod
    def from_dict(cls_inner, data: Dict[str, Any]):
        return cls_inner(
            sensor_id=data.get('sensor_id'),
            name=data.get('name', ''),
            location=tuple(data.get('location', [0, 0])),
            config=data.get('config', {})
        )
    cls.from_dict = from_dict
    return cls

# Apply to all sensor classes
MotionSensor = add_from_dict_method(MotionSensor)
DoorWindowSensor = add_from_dict_method(DoorWindowSensor)
SmokeSensor = add_from_dict_method(SmokeSensor)
LightSensor = add_from_dict_method(LightSensor)
HumiditySensor = add_from_dict_method(HumiditySensor)
PressureSensor = add_from_dict_method(PressureSensor)
ProximitySensor = add_from_dict_method(ProximitySensor)

# Register all sensor types
sensor_registry.register_sensor_type(TemperatureSensor)
sensor_registry.register_sensor_type(MotionSensor)
sensor_registry.register_sensor_type(DoorWindowSensor)
sensor_registry.register_sensor_type(SmokeSensor)
sensor_registry.register_sensor_type(LightSensor)
sensor_registry.register_sensor_type(HumiditySensor)
sensor_registry.register_sensor_type(PressureSensor)
sensor_registry.register_sensor_type(ProximitySensor)