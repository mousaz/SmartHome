"""
Controller HTTP Server for managing IoT sensors and devices.
"""

import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

from ..system.components import SystemComponent, ComponentType
from ..iot.base_thing import BaseThing, ThingType, ThingStatus, thing_registry


class ControllerType(Enum):
    """Types of IoT controllers."""
    SENSOR_CONTROLLER = "sensor_controller"
    DEVICE_CONTROLLER = "device_controller" 
    AUTOMATION_CONTROLLER = "automation_controller"
    SECURITY_CONTROLLER = "security_controller"
    CLIMATE_CONTROLLER = "climate_controller"
    LIGHTING_CONTROLLER = "lighting_controller"
    GENERAL_CONTROLLER = "general_controller"


class ControllerCommand:
    """Represents a command sent to a controller."""
    
    def __init__(self, thing_id: str, command_type: str, parameters: Optional[Dict[str, Any]] = None):
        self.thing_id = thing_id
        self.command_type = command_type
        self.parameters = parameters or {}
        self.timestamp = datetime.now()
        self.command_id = f"cmd_{int(self.timestamp.timestamp() * 1000)}"
        self.status = "pending"
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'command_id': self.command_id,
            'thing_id': self.thing_id,
            'command_type': self.command_type,
            'parameters': self.parameters,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'result': self.result,
            'error': self.error
        }


class ControllerServer(SystemComponent):
    """HTTP Server for controlling IoT sensors and devices."""
    
    def __init__(self, component_id: str = "controller", name: str = "Controller Server",
                 controller_type: ControllerType = ControllerType.GENERAL_CONTROLLER):
        super().__init__(component_id, name, ComponentType.CONTROLLER)
        self.controller_type = controller_type
        self.port = 8090  # Different from API server
        
        self.config = {
            'host': '0.0.0.0',
            'port': self.port,
            'controller_type': controller_type.value,
            'max_concurrent_commands': 50,
            'command_timeout': 30.0,
            'auth_required': False,
            'cors_enabled': True,
            'debug': False
        }
        
        # Controller state
        self.connected_things: Dict[str, BaseThing] = {}
        self.active_commands: Dict[str, ControllerCommand] = {}
        self.command_history: List[ControllerCommand] = []
        self.max_history = 1000
        
        # Statistics
        self.total_commands = 0
        self.successful_commands = 0
        self.failed_commands = 0
        
        # Routes and handlers
        self.routes = {}
        self._setup_default_routes()
    
    def _setup_default_routes(self):
        """Setup default HTTP routes for the controller."""
        self.routes = {
            '/': {'method': 'GET', 'handler': 'handle_index'},
            '/status': {'method': 'GET', 'handler': 'handle_status'},
            '/things': {'method': 'GET', 'handler': 'handle_list_things'},
            '/things/{thing_id}': {'method': 'GET', 'handler': 'handle_get_thing'},
            '/things/{thing_id}/command': {'method': 'POST', 'handler': 'handle_send_command'},
            '/things/{thing_id}/connect': {'method': 'POST', 'handler': 'handle_connect_thing'},
            '/things/{thing_id}/disconnect': {'method': 'POST', 'handler': 'handle_disconnect_thing'},
            '/commands': {'method': 'GET', 'handler': 'handle_list_commands'},
            '/commands/{command_id}': {'method': 'GET', 'handler': 'handle_get_command'},
            '/health': {'method': 'GET', 'handler': 'handle_health'},
            '/metrics': {'method': 'GET', 'handler': 'handle_metrics'}
        }
    
    def _start_process(self):
        """Start the controller HTTP server process."""
        try:
            # Create controller server script
            server_script = self._create_controller_script()
            
            # Start the controller process
            import subprocess
            self.process = subprocess.Popen([
                'python', '-c', server_script
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Start log monitoring thread
            self._start_log_monitoring()
            
            # Wait a moment and check if process is still running
            time.sleep(2)
            return self.process.poll() is None
            
        except Exception as e:
            self.emit_log("ERROR", f"Failed to start controller server: {str(e)}")
            return False
    
    def _create_controller_script(self):
        """Create the controller HTTP server script."""
        return f"""
import json
import time
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import re

class ControllerHTTPHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, controller_server=None, **kwargs):
        self.controller_server = controller_server
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = format % args
        print(f"[{{timestamp}}] CONTROLLER INFO: {{message}}")
    
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_PUT(self):
        self.handle_request('PUT')
    
    def do_DELETE(self):
        self.handle_request('DELETE')
    
    def handle_request(self, method):
        try:
            path = urlparse(self.path).path
            query = parse_qs(urlparse(self.path).query)
            
            # CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Route matching
            response = self.route_request(method, path, query)
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {{
                'error': 'Internal Server Error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def route_request(self, method, path, query):
        # Health check
        if path == '/health':
            return {{
                'status': 'healthy',
                'controller_type': '{self.controller_type.value}',
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - server.start_time
            }}
        
        # Controller status
        elif path == '/status':
            return {{
                'controller_id': '{self.component_id}',
                'controller_type': '{self.controller_type.value}',
                'name': '{self.name}',
                'status': 'running',
                'connected_things': len(getattr(server, 'connected_things', {{}})),
                'active_commands': len(getattr(server, 'active_commands', {{}})),
                'total_commands': getattr(server, 'total_commands', 0),
                'config': {json.dumps(self.config)},
                'timestamp': datetime.now().isoformat()
            }}
        
        # List connected things
        elif path == '/things':
            return {{
                'things': [
                    {{
                        'thing_id': thing_id,
                        'name': f'Thing_{{thing_id[:8]}}',
                        'type': 'simulated',
                        'status': 'online',
                        'last_seen': datetime.now().isoformat()
                    }}
                    for thing_id in getattr(server, 'connected_things', {{}}).keys()
                ],
                'count': len(getattr(server, 'connected_things', {{}})),
                'timestamp': datetime.now().isoformat()
            }}
        
        # Get specific thing
        elif path.startswith('/things/') and not path.endswith('/command') and not path.endswith('/connect') and not path.endswith('/disconnect'):
            thing_id = path.split('/')[-1]
            return {{
                'thing_id': thing_id,
                'name': f'Thing_{{thing_id[:8]}}',
                'type': 'simulated',
                'status': 'online',
                'last_seen': datetime.now().isoformat(),
                'capabilities': ['control', 'monitoring'],
                'controller_id': '{self.component_id}'
            }}
        
        # Send command to thing
        elif path.endswith('/command') and method == 'POST':
            thing_id = path.split('/')[-2]
            
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode() if content_length > 0 else '{{}}'
            
            try:
                command_data = json.loads(body)
            except json.JSONDecodeError:
                return {{'error': 'Invalid JSON in request body'}}
            
            command_id = f"cmd_{{int(time.time() * 1000)}}"
            
            # Simulate command execution
            result = {{
                'command_id': command_id,
                'thing_id': thing_id,
                'command_type': command_data.get('command_type', 'unknown'),
                'parameters': command_data.get('parameters', {{}}),
                'status': 'completed',
                'result': {{
                    'success': True,
                    'message': f'Command executed on {{thing_id}}',
                    'execution_time': 0.05
                }},
                'timestamp': datetime.now().isoformat()
            }}
            
            # Increment command counter
            if not hasattr(server, 'total_commands'):
                server.total_commands = 0
            server.total_commands += 1
            
            print(f"[{{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}] CONTROLLER INFO: Command {{command_id}} executed on {{thing_id}}")
            
            return result
        
        # Connect thing
        elif path.endswith('/connect') and method == 'POST':
            thing_id = path.split('/')[-2]
            
            if not hasattr(server, 'connected_things'):
                server.connected_things = {{}}
            
            server.connected_things[thing_id] = {{
                'connected_at': datetime.now().isoformat(),
                'status': 'online'
            }}
            
            print(f"[{{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}] CONTROLLER INFO: Thing {{thing_id}} connected")
            
            return {{
                'thing_id': thing_id,
                'status': 'connected',
                'controller_id': '{self.component_id}',
                'timestamp': datetime.now().isoformat()
            }}
        
        # Disconnect thing
        elif path.endswith('/disconnect') and method == 'POST':
            thing_id = path.split('/')[-2]
            
            if hasattr(server, 'connected_things') and thing_id in server.connected_things:
                del server.connected_things[thing_id]
            
            print(f"[{{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}] CONTROLLER INFO: Thing {{thing_id}} disconnected")
            
            return {{
                'thing_id': thing_id,
                'status': 'disconnected',
                'timestamp': datetime.now().isoformat()
            }}
        
        # Metrics endpoint
        elif path == '/metrics':
            return {{
                'controller_metrics': {{
                    'total_commands': getattr(server, 'total_commands', 0),
                    'connected_things': len(getattr(server, 'connected_things', {{}})),
                    'uptime': time.time() - server.start_time,
                    'requests_per_minute': getattr(server, 'requests_per_minute', 0)
                }},
                'timestamp': datetime.now().isoformat()
            }}
        
        # Default response
        else:
            return {{
                'controller_id': '{self.component_id}',
                'name': '{self.name}',
                'type': '{self.controller_type.value}',
                'status': 'running',
                'message': 'IoT Controller Server',
                'endpoints': [
                    '/health',
                    '/status', 
                    '/things',
                    '/things/{{thing_id}}',
                    '/things/{{thing_id}}/command',
                    '/things/{{thing_id}}/connect',
                    '/things/{{thing_id}}/disconnect',
                    '/metrics'
                ],
                'timestamp': datetime.now().isoformat()
            }}

# Create custom handler class with controller reference
def make_handler(controller_ref):
    class Handler(ControllerHTTPHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, controller_server=controller_ref, **kwargs)
    return Handler

# Start the controller server
server = HTTPServer(('{self.config['host']}', {self.config['port']}), make_handler(None))
server.start_time = time.time()
server.connected_things = {{}}
server.total_commands = 0

print(f"[{{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}] CONTROLLER INFO: Controller server starting")
print(f"[{{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}] CONTROLLER INFO: Type: {self.controller_type.value}")
print(f"[{{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}] CONTROLLER INFO: Listening on {self.config['host']}:{self.config['port']}")

try:
    # Run server with periodic heartbeat
    def heartbeat():
        while True:
            time.sleep(30)
            print(f"[{{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}] CONTROLLER INFO: Heartbeat - Connected things: {{len(server.connected_things)}}, Total commands: {{server.total_commands}}")
    
    heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
    heartbeat_thread.start()
    
    server.serve_forever()
    
except KeyboardInterrupt:
    print(f"[{{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}] CONTROLLER INFO: Controller server shutting down")
finally:
    server.server_close()
"""
    
    def _start_log_monitoring(self):
        """Start monitoring logs from the controller process."""
        def monitor_logs():
            while self.process and self.process.poll() is None:
                try:
                    if self.process.stdout:
                        output = self.process.stdout.readline()
                    else:
                        break
                    if output:
                        line = output.strip()
                        if "] CONTROLLER " in line:
                            parts = line.split("] CONTROLLER ")
                            if len(parts) >= 2:
                                level_msg = parts[1]
                                if ": " in level_msg:
                                    level, message = level_msg.split(": ", 1)
                                    self.emit_log(level, message)
                except Exception as e:
                    self.emit_log("ERROR", f"Log monitoring error: {str(e)}")
                    break
        
        self.log_thread = threading.Thread(target=monitor_logs, daemon=True)
        self.log_thread.start()
    
    def connect_thing(self, thing: BaseThing) -> bool:
        """Connect a thing to this controller."""
        try:
            self.connected_things[thing.thing_id] = thing
            
            # Add controller connection to the thing
            thing.add_controller_connection(
                controller_id=self.component_id,
                ip_address=self.config['host'], 
                port=self.config['port']
            )
            
            self.emit_log("INFO", f"Thing {thing.thing_id} ({thing.name}) connected")
            return True
            
        except Exception as e:
            self.emit_log("ERROR", f"Failed to connect thing {thing.thing_id}: {e}")
            return False
    
    def disconnect_thing(self, thing_id: str) -> bool:
        """Disconnect a thing from this controller."""
        try:
            if thing_id in self.connected_things:
                thing = self.connected_things[thing_id]
                thing.remove_controller_connection(self.component_id)
                del self.connected_things[thing_id]
                
                self.emit_log("INFO", f"Thing {thing_id} disconnected")
                return True
            else:
                self.emit_log("WARNING", f"Thing {thing_id} not found for disconnection")
                return False
                
        except Exception as e:
            self.emit_log("ERROR", f"Failed to disconnect thing {thing_id}: {e}")
            return False
    
    def send_command(self, thing_id: str, command_type: str, 
                    parameters: Optional[Dict[str, Any]] = None) -> ControllerCommand:
        """Send a command to a connected thing."""
        command = ControllerCommand(thing_id, command_type, parameters)
        
        try:
            if thing_id not in self.connected_things:
                command.status = "failed"
                command.error = f"Thing {thing_id} not connected to this controller"
                return command
            
            thing = self.connected_things[thing_id]
            
            # Execute command based on thing type and command type
            success = self._execute_thing_command(thing, command)
            
            if success:
                command.status = "completed"
                command.result = {"success": True, "timestamp": datetime.now().isoformat()}
                self.successful_commands += 1
            else:
                command.status = "failed"
                command.error = "Command execution failed"
                self.failed_commands += 1
            
            self.total_commands += 1
            
            # Add to history
            self.command_history.append(command)
            if len(self.command_history) > self.max_history:
                self.command_history = self.command_history[-self.max_history:]
            
            self.emit_log("INFO", f"Command {command.command_id} {command.status} for thing {thing_id}")
            
        except Exception as e:
            command.status = "error"
            command.error = str(e)
            self.failed_commands += 1
            self.emit_log("ERROR", f"Command execution error: {e}")
        
        return command
    
    def _execute_thing_command(self, thing: BaseThing, command: ControllerCommand) -> bool:
        """Execute a command on a thing based on its type."""
        try:
            if thing.thing_type == ThingType.SENSOR:
                return self._execute_sensor_command(thing, command)
            elif thing.thing_type == ThingType.ACTUATOR:
                return self._execute_actuator_command(thing, command)
            elif thing.thing_type == ThingType.DEVICE:
                return self._execute_device_command(thing, command)
            else:
                command.error = f"Unsupported thing type: {thing.thing_type}"
                return False
                
        except Exception as e:
            command.error = str(e)
            return False
    
    def _execute_sensor_command(self, sensor, command: ControllerCommand) -> bool:
        """Execute commands specific to sensors."""
        if command.command_type == "get_reading":
            # Simulate getting sensor reading
            command.result = {
                "reading": {"value": 23.5, "unit": "celsius", "timestamp": datetime.now().isoformat()},
                "sensor_id": sensor.thing_id,
                "sensor_type": getattr(sensor, 'get_sensor_type', lambda: 'unknown')()
            }
            return True
        elif command.command_type == "calibrate":
            # Simulate calibration
            command.result = {"calibrated": True, "timestamp": datetime.now().isoformat()}
            return True
        elif command.command_type == "set_config":
            # Update sensor configuration
            config = command.parameters.get('config', {})
            sensor.config.update(config)
            command.result = {"config_updated": True, "new_config": sensor.config}
            return True
        else:
            command.error = f"Unknown sensor command: {command.command_type}"
            return False
    
    def _execute_actuator_command(self, actuator, command: ControllerCommand) -> bool:
        """Execute commands specific to actuators."""
        if command.command_type == "set_position":
            position = command.parameters.get('position', 0)
            # Simulate setting position
            command.result = {
                "position_set": position,
                "current_position": position,
                "timestamp": datetime.now().isoformat()
            }
            return True
        elif command.command_type == "stop":
            # Simulate stopping actuator
            command.result = {"stopped": True, "timestamp": datetime.now().isoformat()}
            return True
        elif command.command_type == "emergency_stop":
            # Simulate emergency stop
            command.result = {"emergency_stopped": True, "timestamp": datetime.now().isoformat()}
            return True
        else:
            command.error = f"Unknown actuator command: {command.command_type}"
            return False
    
    def _execute_device_command(self, device, command: ControllerCommand) -> bool:
        """Execute commands specific to devices."""
        if command.command_type == "turn_on":
            # Simulate turning device on
            command.result = {"state": "on", "timestamp": datetime.now().isoformat()}
            return True
        elif command.command_type == "turn_off":
            # Simulate turning device off
            command.result = {"state": "off", "timestamp": datetime.now().isoformat()}
            return True
        elif command.command_type == "get_status":
            # Get device status
            command.result = {
                "device_id": device.thing_id,
                "status": getattr(device, 'status', 'unknown'),
                "timestamp": datetime.now().isoformat()
            }
            return True
        else:
            command.error = f"Unknown device command: {command.command_type}"
            return False
    
    def get_controller_status(self) -> Dict[str, Any]:
        """Get comprehensive controller status."""
        base_status = self.get_status_info()
        
        controller_status = {
            'controller_type': self.controller_type.value,
            'connected_things': len(self.connected_things),
            'thing_types': {},
            'active_commands': len(self.active_commands),
            'total_commands': self.total_commands,
            'successful_commands': self.successful_commands,
            'failed_commands': self.failed_commands,
            'success_rate': (self.successful_commands / max(self.total_commands, 1)) * 100,
            'endpoints': list(self.routes.keys())
        }
        
        # Count things by type
        for thing in self.connected_things.values():
            thing_type = thing.thing_type.value
            controller_status['thing_types'][thing_type] = controller_status['thing_types'].get(thing_type, 0) + 1
        
        base_status.update(controller_status)
        return base_status