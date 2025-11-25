"""
Base actuator class for controlling IoT devices and systems.
"""

from abc import abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json

from ..iot.base_thing import BaseThing, ThingType, ThingStatus, ThingEvent


class ActuatorType(Enum):
    """Types of actuators."""
    SWITCH = "switch"
    DIMMER = "dimmer"
    MOTOR = "motor"
    VALVE = "valve"
    RELAY = "relay"
    SERVO = "servo"
    STEPPER = "stepper"
    SOLENOID = "solenoid"
    HEATER = "heater"
    COOLER = "cooler"
    FAN = "fan"
    PUMP = "pump"
    LOCK = "lock"
    ALARM = "alarm"
    SPEAKER = "speaker"
    LED = "led"
    DISPLAY = "display"
    OTHER = "other"


class ActuatorStatus(Enum):
    """Actuator operational status."""
    READY = "ready"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    CALIBRATING = "calibrating"


class ActuatorState(Enum):
    """Actuator control states."""
    OFF = "off"
    ON = "on"
    OPENING = "opening"
    CLOSING = "closing"
    MOVING = "moving"
    STOPPED = "stopped"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    UNKNOWN = "unknown"


class ActuatorCommand:
    """Represents a command sent to an actuator."""
    
    def __init__(self, actuator_id: str, command_type: str, parameters: Optional[Dict[str, Any]] = None,
                 priority: str = "normal", timeout: float = 30.0):
        self.actuator_id = actuator_id
        self.command_type = command_type
        self.parameters = parameters or {}
        self.priority = priority  # low, normal, high, urgent
        self.timeout = timeout
        self.timestamp = datetime.now()
        self.command_id = f"{actuator_id}_{self.timestamp.timestamp()}"
        self.status = "pending"  # pending, executing, completed, failed, timeout
        self.result: Optional[Any] = None
        self.error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary."""
        return {
            'command_id': self.command_id,
            'actuator_id': self.actuator_id,
            'command_type': self.command_type,
            'parameters': self.parameters,
            'priority': self.priority,
            'timeout': self.timeout,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'result': self.result,
            'error_message': self.error_message
        }


class BaseActuator(BaseThing):
    """Abstract base class for all actuators."""
    
    def __init__(self, actuator_id: Optional[str] = None, name: str = "", 
                 actuator_type: ActuatorType = ActuatorType.OTHER,
                 location: tuple = (0, 0), config: Optional[Dict[str, Any]] = None):
        super().__init__(
            thing_id=actuator_id,
            name=name or f"{actuator_type.value}_{(actuator_id or 'unknown')[:8]}",
            thing_type=ThingType.ACTUATOR,
            location=location,
            config=config
        )
        
        self.actuator_type = actuator_type
        self.actuator_id = self.thing_id  # Alias for backward compatibility
        
        # Actuator-specific status and state
        self._actuator_status = ActuatorStatus.READY
        self.actuator_state = ActuatorState.UNKNOWN
        
        # Control parameters
        self.current_value = 0.0  # Current actuator value/position
        self.target_value = 0.0   # Target actuator value/position
        self.min_value = 0.0      # Minimum value/position
        self.max_value = 100.0    # Maximum value/position
        
        # Operation settings
        self.operation_speed = 1.0    # Speed/rate of operation
        self.precision = 0.1          # Precision of positioning
        self.safety_limits = True     # Whether safety limits are enforced
        
        # Command handling
        self.command_queue: List[ActuatorCommand] = []
        self.current_command: Optional[ActuatorCommand] = None
        self.command_history = []
        self.max_command_history = 100
        
        # Feedback and monitoring
        self.feedback_enabled = True
        self.position_feedback = True
        self.force_feedback = False
        self.last_operation = None
        
        # Safety features
        self.emergency_stop = False
        self.safety_interlocks = []
        self.max_operation_time = 300.0  # Maximum operation time in seconds
        
        # Calibration
        self.calibrated = False
        self.calibration_data = {}
        
    def get_thing_type(self) -> ThingType:
        """Return the thing type (actuator)."""
        return ThingType.ACTUATOR
    
    # Actuator status management
    @property
    def status(self) -> ActuatorStatus:
        return self._actuator_status
    
    @status.setter 
    def status(self, value: ActuatorStatus):
        self.set_actuator_status(value)
        
    def get_actuator_status(self) -> ActuatorStatus:
        """Get actuator status."""
        return self._actuator_status
        
    def set_actuator_status(self, value: ActuatorStatus):
        """Set actuator status and sync with thing status."""
        old_status = self._actuator_status
        self._actuator_status = value
        
        # Sync with base thing status
        thing_status_mapping = {
            ActuatorStatus.READY: ThingStatus.ONLINE,
            ActuatorStatus.ACTIVE: ThingStatus.ONLINE,
            ActuatorStatus.BUSY: ThingStatus.ONLINE,
            ActuatorStatus.ERROR: ThingStatus.ERROR,
            ActuatorStatus.MAINTENANCE: ThingStatus.MAINTENANCE,
            ActuatorStatus.CALIBRATING: ThingStatus.ONLINE
        }
        
        new_thing_status = thing_status_mapping.get(value, ThingStatus.OFFLINE)
        # Update the base thing status directly
        object.__setattr__(self, 'status', new_thing_status)
        
        # Emit status change event
        if old_status != value:
            self.emit_event("status_changed", {
                'old_status': old_status.value,
                'new_status': value.value
            })
    
    @abstractmethod
    def get_actuator_type(self) -> ActuatorType:
        """Return the actuator type."""
        pass
    
    @abstractmethod
    def execute_command(self, command: ActuatorCommand) -> bool:
        """Execute a command on the actuator. Return True if successful."""
        pass
    
    @abstractmethod
    def get_position(self) -> float:
        """Get current position/value of the actuator."""
        pass
    
    @abstractmethod
    def set_position(self, position: float) -> bool:
        """Set target position/value of the actuator. Return True if successful."""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop actuator operation immediately. Return True if successful."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return actuator capabilities."""
        capabilities = ["control", "positioning"]
        
        if self.feedback_enabled:
            capabilities.append("feedback")
        if self.position_feedback:
            capabilities.append("position_feedback")
        if self.force_feedback:
            capabilities.append("force_feedback")
        if hasattr(self, 'supports_speed_control') and getattr(self, 'supports_speed_control', False):
            capabilities.append("speed_control")
        if self.safety_limits:
            capabilities.append("safety_limits")
        
        return capabilities
    
    def initialize(self) -> bool:
        """Initialize the actuator."""
        try:
            self.set_actuator_status(ActuatorStatus.READY)
            self.actuator_state = ActuatorState.STOPPED
            self.emergency_stop = False
            
            # Initialize position if feedback is available
            if self.position_feedback:
                self.current_value = self.get_position()
            
            self.emit_event("initialized", {
                'actuator_type': self.actuator_type.value,
                'current_position': self.current_value
            })
            
            return True
        except Exception as e:
            self.handle_error(f"Initialization failed: {e}")
            return False
    
    def start(self) -> bool:
        """Start the actuator operations."""
        try:
            if self.emergency_stop:
                return False
                
            if self.initialize():
                self.uptime_start = datetime.now()
                return True
            return False
        except Exception as e:
            self.handle_error(f"Start failed: {e}")
            return False
    
    def stop_operations(self) -> bool:
        """Stop actuator operations gracefully."""
        try:
            # Stop current operation
            success = self.stop()
            
            # Clear command queue
            self.command_queue.clear()
            self.current_command = None
            
            self.set_actuator_status(ActuatorStatus.READY)
            self.actuator_state = ActuatorState.STOPPED
            
            return success
        except Exception as e:
            self.handle_error(f"Stop operations failed: {e}")
            return False
    
    def emergency_stop_activate(self):
        """Activate emergency stop."""
        self.emergency_stop = True
        self.stop()
        self.set_actuator_status(ActuatorStatus.ERROR)
        self.actuator_state = ActuatorState.STOPPED
        
        self.emit_event("emergency_stop", {
            'timestamp': datetime.now().isoformat(),
            'reason': 'Emergency stop activated'
        }, priority="critical")
    
    def emergency_stop_release(self):
        """Release emergency stop."""
        self.emergency_stop = False
        self.set_actuator_status(ActuatorStatus.READY)
        
        self.emit_event("emergency_stop_released", {
            'timestamp': datetime.now().isoformat()
        })
    
    def add_command(self, command: ActuatorCommand) -> bool:
        """Add a command to the queue."""
        if self.emergency_stop:
            command.status = "failed"
            command.error_message = "Emergency stop active"
            return False
        
        # Check safety interlocks
        if not self.check_safety_interlocks(command):
            command.status = "failed"
            command.error_message = "Safety interlock violation"
            return False
        
        self.command_queue.append(command)
        self.emit_event("command_queued", command.to_dict())
        
        return True
    
    def process_commands(self):
        """Process commands in the queue."""
        if self.emergency_stop or not self.command_queue:
            return
        
        if self.current_command is None:
            # Start next command
            self.current_command = self.command_queue.pop(0)
            self.current_command.status = "executing"
            
            self.emit_event("command_started", self.current_command.to_dict())
            
            # Execute the command
            try:
                success = self.execute_command(self.current_command)
                
                if success:
                    self.current_command.status = "completed"
                    self.emit_event("command_completed", self.current_command.to_dict())
                else:
                    self.current_command.status = "failed"
                    self.emit_event("command_failed", self.current_command.to_dict())
                
                # Move to history
                self.command_history.append(self.current_command)
                if len(self.command_history) > self.max_command_history:
                    self.command_history = self.command_history[-self.max_command_history:]
                
                self.current_command = None
                
            except Exception as e:
                if self.current_command is not None:
                    self.current_command.status = "failed"
                    self.current_command.error_message = str(e)
                    self.emit_event("command_error", self.current_command.to_dict())
                self.current_command = None
    
    def check_safety_interlocks(self, command: ActuatorCommand) -> bool:
        """Check safety interlocks before executing command."""
        # Basic safety checks
        if self.emergency_stop:
            return False
        
        # Check position limits for positioning commands
        if command.command_type in ["move_to", "set_position"]:
            target_pos = command.parameters.get("position", 0)
            if not (self.min_value <= target_pos <= self.max_value):
                return False
        
        # Custom safety interlock checks
        for interlock in self.safety_interlocks:
            if not interlock(command):
                return False
        
        return True
    
    def add_safety_interlock(self, interlock_function):
        """Add a safety interlock function."""
        self.safety_interlocks.append(interlock_function)
    
    def calibrate(self) -> bool:
        """Calibrate the actuator."""
        try:
            self.set_actuator_status(ActuatorStatus.CALIBRATING)
            
            # Perform calibration (to be implemented by subclasses)
            success = self.perform_calibration()
            
            if success:
                self.calibrated = True
                self.set_actuator_status(ActuatorStatus.READY)
                self.emit_event("calibration_completed", {
                    'timestamp': datetime.now().isoformat(),
                    'calibration_data': self.calibration_data
                })
            else:
                self.set_actuator_status(ActuatorStatus.ERROR)
                self.emit_event("calibration_failed", {
                    'timestamp': datetime.now().isoformat()
                })
            
            return success
            
        except Exception as e:
            self.handle_error(f"Calibration failed: {e}")
            return False
    
    def perform_calibration(self) -> bool:
        """Perform actuator-specific calibration (override in subclasses)."""
        # Default implementation - just mark as calibrated
        return True
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get comprehensive actuator status information."""
        base_info = super().get_status_info()
        
        actuator_info = {
            'actuator_type': self.actuator_type.value,
            'actuator_status': self._actuator_status.value,
            'actuator_state': self.actuator_state.value,
            'current_value': self.current_value,
            'target_value': self.target_value,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'operation_speed': self.operation_speed,
            'precision': self.precision,
            'calibrated': self.calibrated,
            'emergency_stop': self.emergency_stop,
            'feedback_enabled': self.feedback_enabled,
            'position_feedback': self.position_feedback,
            'safety_limits': self.safety_limits,
            'command_queue_length': len(self.command_queue),
            'current_command': self.current_command.to_dict() if self.current_command else None,
            'last_operation': self.last_operation
        }
        
        # Merge with base thing info
        base_info.update(actuator_info)
        return base_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert actuator to dictionary representation."""
        return self.get_status_info()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseActuator':
        """Create actuator instance from dictionary."""
        actuator = cls(
            actuator_id=data.get('thing_id'),
            name=data.get('name', ''),
            actuator_type=ActuatorType(data.get('actuator_type', 'other')),
            location=tuple(data.get('location', (0, 0))),
            config=data.get('config', {})
        )
        
        # Restore actuator-specific state
        if 'actuator_status' in data:
            actuator._actuator_status = ActuatorStatus(data['actuator_status'])
        
        if 'actuator_state' in data:
            actuator.actuator_state = ActuatorState(data['actuator_state'])
        
        actuator.current_value = data.get('current_value', 0.0)
        actuator.target_value = data.get('target_value', 0.0)
        actuator.min_value = data.get('min_value', 0.0)
        actuator.max_value = data.get('max_value', 100.0)
        actuator.operation_speed = data.get('operation_speed', 1.0)
        actuator.precision = data.get('precision', 0.1)
        actuator.calibrated = data.get('calibrated', False)
        actuator.emergency_stop = data.get('emergency_stop', False)
        
        return actuator