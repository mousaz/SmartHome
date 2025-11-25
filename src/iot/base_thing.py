"""
Base Thing class for all IoT devices, sensors, and actuators.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
import uuid
import time
import json
from datetime import datetime
import threading


class ThingType(Enum):
    """Types of IoT things."""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    DEVICE = "device"
    CONTROLLER = "controller"
    GATEWAY = "gateway"


class ThingStatus(Enum):
    """Thing operational status."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    INITIALIZING = "initializing"


class ConnectionType(Enum):
    """Connection types for IoT things."""
    WIFI = "wifi"
    ETHERNET = "ethernet"
    ZIGBEE = "zigbee"
    BLUETOOTH = "bluetooth"
    LORA = "lora"
    HTTP = "http"
    MQTT = "mqtt"
    COAP = "coap"


class ThingEvent:
    """Represents an event from an IoT thing."""
    
    def __init__(self, thing_id: str, event_type: str, data: Dict[str, Any], 
                 timestamp: Optional[datetime] = None, priority: str = "normal"):
        self.thing_id = thing_id
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now()
        self.priority = priority  # low, normal, high, critical
        self.event_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'thing_id': self.thing_id,
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class ConnectionInfo:
    """Information about how a thing connects to the network/system."""
    
    def __init__(self, connection_type: ConnectionType, ip_address: Optional[str] = None, 
                 port: Optional[int] = None, domain: Optional[str] = None, protocol: str = "http"):
        self.connection_type = connection_type
        self.ip_address = ip_address
        self.port = port
        self.domain = domain
        self.protocol = protocol
        self.last_seen = None
        self.signal_strength = None
        
    def get_endpoint(self) -> Optional[str]:
        """Get the connection endpoint URL."""
        if self.domain:
            base = self.domain
        elif self.ip_address:
            base = self.ip_address
        else:
            return None
            
        if self.port:
            return f"{self.protocol}://{base}:{self.port}"
        else:
            return f"{self.protocol}://{base}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'connection_type': self.connection_type.value,
            'ip_address': self.ip_address,
            'port': self.port,
            'domain': self.domain,
            'protocol': self.protocol,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'signal_strength': self.signal_strength,
            'endpoint': self.get_endpoint()
        }


class BaseThing(ABC):
    """Abstract base class for all IoT things (sensors, actuators, devices)."""
    
    def __init__(self, thing_id: Optional[str] = None, name: str = "", thing_type: Optional[ThingType] = None,
                 location: tuple = (0, 0), config: Optional[Dict[str, Any]] = None):
        self.thing_id = thing_id or str(uuid.uuid4())
        self.name = name or f"{self.get_thing_type()}_{self.thing_id[:8]}"
        self.thing_type = thing_type or self.get_thing_type()
        self.location = location
        self.config = config or {}
        self.status = ThingStatus.OFFLINE
        self.metadata = {}
        
        # Connection information
        self.connection_info = None
        self.controller_connections = []  # List of controllers this thing connects to
        
        # Event handling
        self.event_callbacks = []
        self.event_history = []
        self.max_history = 1000
        
        # Monitoring
        self.last_heartbeat = None
        self.uptime_start = None
        self.error_count = 0
        self.last_error = None
        
        # Threading
        self._lock = threading.Lock()
        self._running = False
        
    @abstractmethod
    def get_thing_type(self) -> ThingType:
        """Return the type of this thing."""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the thing. Return True if successful."""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """Start the thing operations. Return True if successful."""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stop the thing operations. Return True if successful."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities this thing supports."""
        pass
    
    def set_connection_info(self, connection_info: ConnectionInfo):
        """Set connection information for this thing."""
        with self._lock:
            self.connection_info = connection_info
    
    def add_controller_connection(self, controller_id: str, ip_address: str, 
                                port: int, domain: Optional[str] = None):
        """Add a connection to a controller."""
        connection = {
            'controller_id': controller_id,
            'ip_address': ip_address,
            'port': port,
            'domain': domain,
            'endpoint': f"http://{domain or ip_address}:{port}",
            'last_communication': None,
            'status': 'configured'
        }
        
        with self._lock:
            # Remove existing connection to same controller if exists
            self.controller_connections = [
                c for c in self.controller_connections 
                if c['controller_id'] != controller_id
            ]
            self.controller_connections.append(connection)
    
    def remove_controller_connection(self, controller_id: str):
        """Remove a connection to a controller."""
        with self._lock:
            self.controller_connections = [
                c for c in self.controller_connections 
                if c['controller_id'] != controller_id
            ]
    
    def get_controller_connections(self) -> List[Dict[str, Any]]:
        """Get all controller connections."""
        with self._lock:
            return self.controller_connections.copy()
    
    def add_event_callback(self, callback: Callable[[ThingEvent], None]):
        """Add an event callback function."""
        self.event_callbacks.append(callback)
    
    def emit_event(self, event_type: str, data: Dict[str, Any], priority: str = "normal"):
        """Emit an event."""
        event = ThingEvent(self.thing_id, event_type, data, priority=priority)
        
        # Add to history
        with self._lock:
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history = self.event_history[-self.max_history:]
        
        # Notify callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                self.handle_error(f"Error in event callback: {e}")
    
    def heartbeat(self):
        """Send a heartbeat to indicate the thing is alive."""
        with self._lock:
            self.last_heartbeat = datetime.now()
            if self.status == ThingStatus.OFFLINE:
                self.status = ThingStatus.ONLINE
        
        self.emit_event("heartbeat", {
            'timestamp': self.last_heartbeat.isoformat(),
            'uptime': self.get_uptime()
        })
    
    def get_uptime(self) -> float:
        """Get uptime in seconds."""
        if self.uptime_start:
            return (datetime.now() - self.uptime_start).total_seconds()
        return 0
    
    def handle_error(self, error_message: str):
        """Handle an error condition."""
        with self._lock:
            self.error_count += 1
            self.last_error = {
                'message': error_message,
                'timestamp': datetime.now(),
                'count': self.error_count
            }
            self.status = ThingStatus.ERROR
        
        self.emit_event("error", {
            'message': error_message,
            'error_count': self.error_count
        }, priority="high")
    
    def reset_errors(self):
        """Reset error state."""
        with self._lock:
            self.error_count = 0
            self.last_error = None
            if self.status == ThingStatus.ERROR:
                self.status = ThingStatus.ONLINE
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get comprehensive status information."""
        with self._lock:
            return {
                'thing_id': self.thing_id,
                'name': self.name,
                'type': self.thing_type.value,
                'status': self.status.value,
                'location': self.location,
                'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
                'uptime': self.get_uptime(),
                'error_count': self.error_count,
                'last_error': self.last_error,
                'connection_info': self.connection_info.to_dict() if self.connection_info else None,
                'controller_connections': self.controller_connections.copy(),
                'capabilities': self.get_capabilities(),
                'metadata': self.metadata.copy(),
                'config': self.config.copy()
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert thing to dictionary representation."""
        return self.get_status_info()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseThing':
        """Create thing instance from dictionary (to be implemented by subclasses)."""
        raise NotImplementedError("Subclasses must implement from_dict method")
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.thing_id[:8]}, name={self.name}, status={self.status.value})"
    
    def __repr__(self) -> str:
        return self.__str__()


class ThingRegistry:
    """Registry for managing IoT things."""
    
    def __init__(self):
        self._things: Dict[str, BaseThing] = {}
        self._types: Dict[ThingType, List[BaseThing]] = {}
        self._lock = threading.Lock()
    
    def register_thing(self, thing: BaseThing):
        """Register a thing in the registry."""
        with self._lock:
            self._things[thing.thing_id] = thing
            
            if thing.thing_type not in self._types:
                self._types[thing.thing_type] = []
            self._types[thing.thing_type].append(thing)
    
    def unregister_thing(self, thing_id: str):
        """Unregister a thing from the registry."""
        with self._lock:
            if thing_id in self._things:
                thing = self._things[thing_id]
                del self._things[thing_id]
                
                if thing.thing_type in self._types:
                    self._types[thing.thing_type] = [
                        t for t in self._types[thing.thing_type] 
                        if t.thing_id != thing_id
                    ]
    
    def get_thing(self, thing_id: str) -> Optional[BaseThing]:
        """Get a thing by ID."""
        return self._things.get(thing_id)
    
    def get_things_by_type(self, thing_type: ThingType) -> List[BaseThing]:
        """Get all things of a specific type."""
        with self._lock:
            return self._types.get(thing_type, []).copy()
    
    def get_all_things(self) -> List[BaseThing]:
        """Get all registered things."""
        with self._lock:
            return list(self._things.values())
    
    def get_things_by_status(self, status: ThingStatus) -> List[BaseThing]:
        """Get all things with a specific status."""
        return [thing for thing in self.get_all_things() if thing.status == status]


# Global registry instance
thing_registry = ThingRegistry()