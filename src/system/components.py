"""
System components that run as separate processes.
"""

import subprocess
import threading
import time
import queue
import json
import sqlite3
import os
from typing import Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime


class ComponentType(Enum):
    """Types of system components."""
    SENSOR = "sensor"
    API_SERVER = "api_server"
    DATABASE = "database"
    CONTROLLER = "controller"
    WEB_INTERFACE = "web_interface"
    MQTT_BROKER = "mqtt_broker"


class ComponentStatus(Enum):
    """Component operational status."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    CRASHED = "crashed"


class LogEntry:
    """Represents a log entry from a component."""
    
    def __init__(self, component_id: str, timestamp: datetime, level: str, message: str):
        self.component_id = component_id
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.entry_id = f"{component_id}_{timestamp.timestamp()}"
    
    def to_dict(self):
        return {
            'id': self.entry_id,
            'component_id': self.component_id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message
        }


class SystemComponent:
    """Base class for system components."""
    
    def __init__(self, component_id: str, name: str, component_type: ComponentType):
        self.component_id = component_id
        self.name = name
        self.component_type = component_type
        self.status = ComponentStatus.STOPPED
        self.process = None
        self.log_queue = queue.Queue()
        self.log_thread = None
        self.config = {}
        self.port = None
        self.log_callbacks = []
        self.startup_time = None
        
    def add_log_callback(self, callback: Callable[[LogEntry], None]):
        """Add a callback for log entries."""
        self.log_callbacks.append(callback)
    
    def emit_log(self, level: str, message: str):
        """Emit a log entry."""
        entry = LogEntry(self.component_id, datetime.now(), level, message)
        for callback in self.log_callbacks:
            try:
                callback(entry)
            except Exception as e:
                print(f"Error in log callback: {e}")
    
    def start(self):
        """Start the component."""
        if self.status != ComponentStatus.STOPPED:
            return False
            
        self.status = ComponentStatus.STARTING
        self.startup_time = datetime.now()
        self.emit_log("INFO", f"Starting {self.name}")
        
        try:
            success = self._start_process()
            if success:
                self.status = ComponentStatus.RUNNING
                self.emit_log("INFO", f"{self.name} started successfully")
                return True
            else:
                self.status = ComponentStatus.ERROR
                self.emit_log("ERROR", f"Failed to start {self.name}")
                return False
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.emit_log("ERROR", f"Exception starting {self.name}: {str(e)}")
            return False
    
    def stop(self):
        """Stop the component."""
        if self.status not in [ComponentStatus.RUNNING, ComponentStatus.ERROR]:
            return False
            
        self.status = ComponentStatus.STOPPING
        self.emit_log("INFO", f"Stopping {self.name}")
        
        try:
            success = self._stop_process()
            self.status = ComponentStatus.STOPPED
            if success:
                self.emit_log("INFO", f"{self.name} stopped successfully")
            else:
                self.emit_log("WARNING", f"{self.name} may not have stopped cleanly")
            return True
        except Exception as e:
            self.status = ComponentStatus.ERROR
            self.emit_log("ERROR", f"Exception stopping {self.name}: {str(e)}")
            return False
    
    def restart(self):
        """Restart the component."""
        self.emit_log("INFO", f"Restarting {self.name}")
        self.stop()
        time.sleep(1)  # Brief pause
        return self.start()
    
    def get_status_info(self):
        """Get detailed status information."""
        uptime = None
        if self.startup_time and self.status == ComponentStatus.RUNNING:
            uptime = datetime.now() - self.startup_time
            
        return {
            'component_id': self.component_id,
            'name': self.name,
            'type': self.component_type.value,
            'status': self.status.value,
            'port': self.port,
            'uptime': str(uptime) if uptime else None,
            'config': self.config
        }
    
    def _start_process(self):
        """Override in subclasses to implement process starting."""
        return True
    
    def _stop_process(self):
        """Override in subclasses to implement process stopping."""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            return True
        return True


class APIServer(SystemComponent):
    """API Server component."""
    
    def __init__(self, component_id: str = "api_server", name: str = "API Server"):
        super().__init__(component_id, name, ComponentType.API_SERVER)
        self.port = 8080
        self.config = {
            'host': '0.0.0.0',
            'port': self.port,
            'debug': False,
            'cors_enabled': True,
            'auth_required': False
        }
    
    def _start_process(self):
        """Start the API server process."""
        try:
            # Create a simple Flask API server script
            server_script = self._create_server_script()
            
            # Start the server process
            self.process = subprocess.Popen([
                'python', '-c', server_script
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Start log monitoring thread
            self._start_log_monitoring()
            
            # Wait a moment and check if process is still running
            time.sleep(2)
            if self.process.poll() is None:
                return True
            else:
                return False
                
        except Exception as e:
            self.emit_log("ERROR", f"Failed to start API server: {str(e)}")
            return False
    
    def _create_server_script(self):
        """Create the API server script."""
        return f"""
import time
import threading
from datetime import datetime

class SimpleAPIServer:
    def __init__(self, port={self.port}):
        self.port = port
        self.running = False
    
    def log(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{{timestamp}}] API_SERVER {{level}}: {{message}}")
    
    def start(self):
        self.running = True
        self.log("INFO", "API Server starting on port {{self.port}}")
        
        # Simulate API server operations
        while self.running:
            time.sleep(5)
            self.log("INFO", f"API Server heartbeat - Active connections: {{hash(time.time()) % 10}}")
            
            # Simulate some API calls
            if hash(time.time()) % 3 == 0:
                self.log("INFO", "GET /api/sensors - 200 OK")
            elif hash(time.time()) % 5 == 0:
                self.log("INFO", "POST /api/data - 201 Created")

server = SimpleAPIServer()
try:
    server.start()
except KeyboardInterrupt:
    server.log("INFO", "API Server shutting down")
except Exception as e:
    server.log("ERROR", f"API Server error: {{e}}")
"""
    
    def _start_log_monitoring(self):
        """Start monitoring logs from the process."""
        def monitor_logs():
            while self.process and self.process.poll() is None:
                try:
                    if self.process.stdout:
                        output = self.process.stdout.readline()
                    else:
                        break
                    if output:
                        # Parse the log line and emit it
                        line = output.strip()
                        if "] API_SERVER " in line:
                            parts = line.split("] API_SERVER ")
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


class DatabaseServer(SystemComponent):
    """Enhanced Database Server component supporting SQLite and MongoDB."""
    
    def __init__(self, component_id: str = "database", name: str = "Database Server", 
                 db_type: str = "sqlite"):
        super().__init__(component_id, name, ComponentType.DATABASE)
        self.db_type = db_type.lower()
        
        if self.db_type == "sqlite":
            self.port = None  # SQLite doesn't use network port
            self.db_path = "data/smart_home.db"
            self.config = {
                'type': 'sqlite',
                'path': self.db_path,
                'max_connections': 20,
                'backup_enabled': True,
                'backup_interval': 3600,
                'pragma_settings': {
                    'journal_mode': 'WAL',
                    'synchronous': 'NORMAL',
                    'cache_size': 10000
                }
            }
        elif self.db_type == "mongodb":
            self.port = 27017
            self.config = {
                'type': 'mongodb',
                'host': 'localhost',
                'port': self.port,
                'database': 'smart_home',
                'max_connections': 100,
                'auth_enabled': False,
                'username': '',
                'password': '',
                'backup_enabled': True,
                'backup_interval': 3600,
                'collections': ['sensors', 'devices', 'readings', 'events', 'users']
            }
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        self.active_connections = 0
        self.total_queries = 0
        self.database_size = 0
    
    def _start_process(self):
        """Start the database server process."""
        try:
            if self.db_type == "sqlite":
                return self._start_sqlite_process()
            elif self.db_type == "mongodb":
                return self._start_mongodb_process()
            else:
                self.emit_log("ERROR", f"Unsupported database type: {self.db_type}")
                return False
                
        except Exception as e:
            self.emit_log("ERROR", f"Failed to start database server: {str(e)}")
            return False
    
    def _start_sqlite_process(self):
        """Start SQLite database process."""
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config['path']), exist_ok=True)
        
        # Create SQLite server simulation script
        server_script = self._create_sqlite_script()
        
        # Start the SQLite process
        self.process = subprocess.Popen([
            'python', '-c', server_script
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Start log monitoring thread
        self._start_log_monitoring()
        
        # Wait a moment and check if process is still running
        time.sleep(1)
        return self.process.poll() is None
    
    def _start_mongodb_process(self):
        """Start MongoDB simulation process."""
        # Create MongoDB server simulation script
        server_script = self._create_mongodb_script()
        
        # Start the MongoDB simulation process
        self.process = subprocess.Popen([
            'python', '-c', server_script
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Start log monitoring thread
        self._start_log_monitoring()
        
        # Wait a moment and check if process is still running
        time.sleep(1)
        return self.process.poll() is None
    
    def _create_sqlite_script(self):
        """Create SQLite database server script."""
        return f"""
import sqlite3
import time
import threading
import os
from datetime import datetime

class DatabaseServer:
    def __init__(self, db_path="{self.db_path}"):
        self.db_path = db_path
        self.running = False
        self.connections = 0
        
    def log(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{{timestamp}}] DATABASE {{level}}: {{message}}")
    
    def initialize_database(self):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensors (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    location TEXT,
                    status TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id TEXT,
                    value REAL,
                    unit TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            self.log("INFO", "Database initialized successfully")
            return True
        except Exception as e:
            self.log("ERROR", f"Database initialization failed: {{e}}")
            return False
    
    def start(self):
        self.running = True
        self.log("INFO", "Database server starting")
        
        if not self.initialize_database():
            return
            
        # Simulate database operations
        while self.running:
            time.sleep(3)
            
            # Simulate various database operations
            operation = hash(time.time()) % 4
            if operation == 0:
                self.log("INFO", f"Query executed - SELECT sensors ({{hash(time.time()) % 100}}ms)")
            elif operation == 1:
                self.log("INFO", f"Data inserted - sensor_data table ({{hash(time.time()) % 50}}ms)")
            elif operation == 2:
                self.log("DEBUG", f"Connection pool status - Active: {{hash(time.time()) % 5}}/20")
            elif operation == 3 and hash(time.time()) % 10 == 0:
                self.log("INFO", "Backup operation completed successfully")

db_server = DatabaseServer()
try:
    db_server.start()
except KeyboardInterrupt:
    db_server.log("INFO", "Database server shutting down")
except Exception as e:
    db_server.log("ERROR", f"Database server error: {{e}}")
"""
    
    def _create_mongodb_script(self):
        """Create MongoDB database server script."""
        return f"""
import time
import threading
import os
import json
from datetime import datetime
from collections import defaultdict

class MongoDBSimulator:
    def __init__(self, host="{self.config.get('host', 'localhost')}", port={self.config.get('port', 27017)}):
        self.host = host
        self.port = port
        self.database_name = "{self.config.get('database', 'smart_home')}"
        self.running = False
        self.connections = 0
        self.collections = {{}}
        self.indexes = defaultdict(list)
        
        # Initialize collections
        for collection in {self.config.get('collections', [])}:
            self.collections[collection] = []
    
    def log(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{{timestamp}}] DATABASE {{level}}: {{message}}")
    
    def initialize_database(self):
        try:
            self.log("INFO", f"Initializing MongoDB database: {{self.database_name}}")
            
            # Create default collections
            default_collections = ['sensors', 'devices', 'readings', 'events', 'users']
            for collection in default_collections:
                if collection not in self.collections:
                    self.collections[collection] = []
                    self.log("INFO", f"Created collection: {{collection}}")
            
            # Create indexes
            self.create_default_indexes()
            
            self.log("INFO", "MongoDB database initialized successfully")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Failed to initialize database: {{e}}")
            return False
    
    def create_default_indexes(self):
        # Simulate creating indexes
        indexes = {{
            'sensors': ['{{"sensor_id": 1}}', '{{"type": 1}}', '{{"created_at": 1}}'],
            'devices': ['{{"device_id": 1}}', '{{"category": 1}}', '{{"status": 1}}'],
            'readings': ['{{"sensor_id": 1, "timestamp": 1}}', '{{"timestamp": 1}}'],
            'events': ['{{"thing_id": 1, "timestamp": 1}}', '{{"event_type": 1}}'],
            'users': ['{{"username": 1}}', '{{"email": 1}}']
        }}
        
        for collection, collection_indexes in indexes.items():
            self.indexes[collection].extend(collection_indexes)
            self.log("INFO", f"Created indexes for {{collection}}: {{len(collection_indexes)}} indexes")
    
    def simulate_operations(self):
        while self.running:
            try:
                # Simulate database operations
                operation_types = ['insert', 'find', 'update', 'delete']
                import random
                
                if random.random() < 0.3:  # 30% chance of operation
                    op_type = random.choice(operation_types)
                    collection = random.choice(list(self.collections.keys()))
                    
                    if op_type == 'insert':
                        doc_id = len(self.collections[collection]) + 1
                        self.collections[collection].append({{'_id': doc_id, 'timestamp': datetime.now().isoformat()}})
                        self.log("DEBUG", f"Inserted document into {{collection}}")
                    
                    elif op_type == 'find':
                        count = len(self.collections[collection])
                        self.log("DEBUG", f"Found {{count}} documents in {{collection}}")
                    
                    elif op_type == 'update' and self.collections[collection]:
                        self.log("DEBUG", f"Updated document in {{collection}}")
                    
                    elif op_type == 'delete' and self.collections[collection]:
                        self.collections[collection].pop()
                        self.log("DEBUG", f"Deleted document from {{collection}}")
                
                # Simulate connection activity
                if random.random() < 0.1:  # 10% chance of connection change
                    if self.connections > 0 and random.random() < 0.5:
                        self.connections -= 1
                        self.log("DEBUG", f"Connection closed. Active connections: {{self.connections}}")
                    elif self.connections < {self.config.get('max_connections', 100)}:
                        self.connections += 1
                        self.log("DEBUG", f"New connection. Active connections: {{self.connections}}")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.log("ERROR", f"Operation simulation error: {{e}}")
                time.sleep(5)
    
    def start(self):
        self.log("INFO", f"Starting MongoDB server on {{self.host}}:{{self.port}}")
        
        if not self.initialize_database():
            return False
        
        self.running = True
        
        # Start operation simulation in a separate thread
        self.ops_thread = threading.Thread(target=self.simulate_operations, daemon=True)
        self.ops_thread.start()
        
        self.log("INFO", f"MongoDB server started successfully")
        self.log("INFO", f"Database: {{self.database_name}}")
        self.log("INFO", f"Collections: {{', '.join(self.collections.keys())}}")
        self.log("INFO", f"Listening on {{self.host}}:{{self.port}}")
        
        # Keep the server running
        try:
            while self.running:
                self.log("INFO", f"MongoDB heartbeat - Active connections: {{self.connections}}, Collections: {{len(self.collections)}}")
                time.sleep(30)  # Heartbeat every 30 seconds
        except KeyboardInterrupt:
            self.log("INFO", "Received shutdown signal")
        finally:
            self.stop()
    
    def stop(self):
        self.log("INFO", "Stopping MongoDB server")
        self.running = False
        self.log("INFO", "MongoDB server stopped")

# Create and start MongoDB server
mongo_server = MongoDBSimulator()
try:
    mongo_server.start()
except KeyboardInterrupt:
    mongo_server.log("INFO", "MongoDB server shutting down")
except Exception as e:
    mongo_server.log("ERROR", f"MongoDB server error: {{e}}")
"""
    
    def _start_log_monitoring(self):
        """Start monitoring logs from the database process."""
        def monitor_logs():
            while self.process and self.process.poll() is None:
                try:
                    if self.process.stdout:
                        output = self.process.stdout.readline()
                    else:
                        break
                    if output:
                        line = output.strip()
                        if "] DATABASE " in line:
                            parts = line.split("] DATABASE ")
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


class MQTTBroker(SystemComponent):
    """MQTT Broker component."""
    
    def __init__(self, component_id: str = "mqtt_broker", name: str = "MQTT Broker"):
        super().__init__(component_id, name, ComponentType.MQTT_BROKER)
        self.port = 1883
        self.config = {
            'port': self.port,
            'websocket_port': 9001,
            'max_clients': 100,
            'retain_messages': True,
            'auth_required': False
        }
    
    def _start_process(self):
        """Start the MQTT broker process."""
        try:
            # Create MQTT broker simulation script
            broker_script = self._create_mqtt_script()
            
            self.process = subprocess.Popen([
                'python', '-c', broker_script
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self._start_log_monitoring()
            
            time.sleep(1)
            return self.process.poll() is None
            
        except Exception as e:
            self.emit_log("ERROR", f"Failed to start MQTT broker: {str(e)}")
            return False
    
    def _create_mqtt_script(self):
        """Create the MQTT broker script."""
        return f"""
import time
import threading
from datetime import datetime
import random

class MQTTBroker:
    def __init__(self, port={self.port}):
        self.port = port
        self.running = False
        self.clients = set()
        self.topics = {{'sensors/+/data': [], 'system/status': [], 'alerts/+': []}}
        
    def log(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{{timestamp}}] MQTT_BROKER {{level}}: {{message}}")
    
    def start(self):
        self.running = True
        self.log("INFO", f"MQTT Broker starting on port {{self.port}}")
        
        while self.running:
            time.sleep(4)
            
            # Simulate MQTT operations
            operation = hash(time.time()) % 5
            if operation == 0:
                client_id = f"client_{{random.randint(1000, 9999)}}"
                self.log("INFO", f"Client connected: {{client_id}}")
            elif operation == 1:
                topic = random.choice(["sensors/temp/data", "sensors/motion/data", "system/status"])
                self.log("INFO", f"Message published to {{topic}}")
            elif operation == 2:
                self.log("DEBUG", f"Active clients: {{len(self.clients)}}/100")
            elif operation == 3:
                topic = random.choice(list(self.topics.keys()))
                self.log("INFO", f"Subscription to {{topic}}")
            elif operation == 4 and hash(time.time()) % 8 == 0:
                self.log("WARNING", "High message volume detected")

broker = MQTTBroker()
try:
    broker.start()
except KeyboardInterrupt:
    broker.log("INFO", "MQTT Broker shutting down")
except Exception as e:
    broker.log("ERROR", f"MQTT Broker error: {{e}}")
"""
    
    def _start_log_monitoring(self):
        """Start monitoring logs from the MQTT broker."""
        def monitor_logs():
            while self.process and self.process.poll() is None:
                try:
                    if self.process.stdout:
                        output = self.process.stdout.readline()
                    else:
                        break
                    if output:
                        line = output.strip()
                        if "] MQTT_BROKER " in line:
                            parts = line.split("] MQTT_BROKER ")
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


class ComponentManager:
    """Manages all system components."""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.components = {}
        self.log_entries = []
        self.log_callbacks = []
        self.max_log_entries = 1000
        
    def register_component(self, component: SystemComponent):
        """Register a component with the manager."""
        self.components[component.component_id] = component
        component.add_log_callback(self._on_component_log)
        
        if self.logger:
            self.logger.info(f"Registered component: {component.name}")
    
    def _on_component_log(self, log_entry: LogEntry):
        """Handle log entries from components."""
        self.log_entries.append(log_entry)
        
        # Keep only the most recent entries
        if len(self.log_entries) > self.max_log_entries:
            self.log_entries = self.log_entries[-self.max_log_entries:]
        
        # Notify callbacks
        for callback in self.log_callbacks:
            try:
                callback(log_entry)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in log callback: {e}")
    
    def add_log_callback(self, callback: Callable[[LogEntry], None]):
        """Add a callback for all component logs."""
        self.log_callbacks.append(callback)
    
    def start_component(self, component_id: str) -> bool:
        """Start a component."""
        if component_id in self.components:
            return self.components[component_id].start()
        return False
    
    def stop_component(self, component_id: str) -> bool:
        """Stop a component."""
        if component_id in self.components:
            return self.components[component_id].stop()
        return False
    
    def restart_component(self, component_id: str) -> bool:
        """Restart a component."""
        if component_id in self.components:
            return self.components[component_id].restart()
        return False
    
    def get_component_status(self, component_id: str) -> Optional[Dict]:
        """Get status of a specific component."""
        if component_id in self.components:
            return self.components[component_id].get_status_info()
        return None
    
    def get_all_components_status(self) -> List[Dict]:
        """Get status of all components."""
        return [comp.get_status_info() for comp in self.components.values()]
    
    def get_component_logs(self, component_id: str, limit: int = 100) -> List[LogEntry]:
        """Get recent logs for a specific component."""
        component_logs = [
            entry for entry in self.log_entries 
            if entry.component_id == component_id
        ]
        return component_logs[-limit:] if limit else component_logs
    
    def get_all_logs(self, limit: int = 100) -> List[LogEntry]:
        """Get recent logs from all components."""
        return self.log_entries[-limit:] if limit else self.log_entries
    
    def start_all_components(self):
        """Start all registered components."""
        for component in self.components.values():
            if component.status == ComponentStatus.STOPPED:
                component.start()
    
    def stop_all_components(self):
        """Stop all running components."""
        for component in self.components.values():
            if component.status in [ComponentStatus.RUNNING, ComponentStatus.ERROR]:
                component.stop()