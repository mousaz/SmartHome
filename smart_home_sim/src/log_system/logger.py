"""
Smart Home Logger system with live viewing capabilities.
"""

import logging
import logging.handlers
import os
import threading
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional
from queue import Queue, Empty
import json


class SmartHomeLogRecord:
    """Enhanced log record for smart home events."""
    
    def __init__(self, level: str, message: str, category: str = "general", 
                 timestamp: Optional[datetime] = None, extra_data: Dict[str, Any] = None):
        self.timestamp = timestamp or datetime.now()
        self.level = level
        self.message = message
        self.category = category  # general, sensor, rule, security, simulation
        self.extra_data = extra_data or {}
        self.record_id = f"{self.timestamp.timestamp()}_{id(self)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log record to dictionary."""
        return {
            'record_id': self.record_id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message,
            'category': self.category,
            'extra_data': self.extra_data
        }
    
    def format_message(self) -> str:
        """Format message for display."""
        time_str = self.timestamp.strftime("%H:%M:%S.%f")[:-3]
        return f"[{time_str}] {self.level:8} [{self.category:10}] {self.message}"


class LogHandler:
    """Handler for processing log records."""
    
    def __init__(self, callback: Callable[[SmartHomeLogRecord], None]):
        self.callback = callback
        self.active = True
    
    def handle(self, record: SmartHomeLogRecord):
        """Handle a log record."""
        if self.active:
            try:
                self.callback(record)
            except Exception as e:
                print(f"Error in log handler: {e}")
    
    def set_active(self, active: bool):
        """Set handler active state."""
        self.active = active


class SmartHomeLogger:
    """Main logger class for smart home simulation."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()
        
        # Log storage
        self.log_records: List[SmartHomeLogRecord] = []
        self.max_records = 10000  # Keep last 10k records in memory
        
        # Handlers
        self.handlers: List[LogHandler] = []
        
        # Threading
        self.log_queue = Queue()
        self.log_thread = None
        self.shutdown_event = threading.Event()
        
        # File logging
        self.file_logger = self.setup_file_logger()
        
        # Start log processing thread
        self.start_log_thread()
        
        self.info("Smart Home Logger initialized")
    
    def ensure_log_directory(self):
        """Ensure log directory exists."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def setup_file_logger(self) -> logging.Logger:
        """Setup file-based logging."""
        logger = logging.getLogger("smarthome")
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(category)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Daily rotating file handler
        log_file = os.path.join(self.log_dir, "smarthome.log")
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file, when='midnight', interval=1, backupCount=7
        )
        file_handler.setFormatter(detailed_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_log_file = os.path.join(self.log_dir, "errors.log")
        error_handler = logging.handlers.TimedRotatingFileHandler(
            error_log_file, when='midnight', interval=1, backupCount=30
        )
        error_handler.setFormatter(detailed_formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)
        
        return logger
    
    def start_log_thread(self):
        """Start the log processing thread."""
        self.log_thread = threading.Thread(target=self._log_processor, daemon=True)
        self.log_thread.start()
    
    def _log_processor(self):
        """Process log records in separate thread."""
        while not self.shutdown_event.is_set():
            try:
                # Get log record from queue (with timeout)
                record = self.log_queue.get(timeout=1.0)
                
                # Add to memory storage
                self.log_records.append(record)
                
                # Trim old records if needed
                if len(self.log_records) > self.max_records:
                    self.log_records = self.log_records[-self.max_records:]
                
                # Log to file
                extra = {'category': record.category}
                if record.extra_data:
                    extra.update(record.extra_data)
                
                log_level = getattr(logging, record.level.upper(), logging.INFO)
                self.file_logger.log(log_level, record.message, extra=extra)
                
                # Call handlers
                for handler in self.handlers:
                    handler.handle(record)
                
                self.log_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                print(f"Error in log processor: {e}")
    
    def shutdown(self):
        """Shutdown the logger."""
        self.shutdown_event.set()
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=2.0)
    
    def add_handler(self, handler: LogHandler):
        """Add a log handler."""
        self.handlers.append(handler)
    
    def remove_handler(self, handler: LogHandler):
        """Remove a log handler."""
        if handler in self.handlers:
            self.handlers.remove(handler)
    
    def log(self, level: str, message: str, category: str = "general", 
            extra_data: Dict[str, Any] = None):
        """Log a message."""
        record = SmartHomeLogRecord(level, message, category, extra_data=extra_data)
        
        try:
            self.log_queue.put(record, timeout=1.0)
        except Exception as e:
            print(f"Failed to queue log record: {e}")
    
    def debug(self, message: str, category: str = "general", extra_data: Dict[str, Any] = None):
        """Log debug message."""
        self.log("DEBUG", message, category, extra_data)
    
    def info(self, message: str, category: str = "general", extra_data: Dict[str, Any] = None):
        """Log info message."""
        self.log("INFO", message, category, extra_data)
    
    def warning(self, message: str, category: str = "general", extra_data: Dict[str, Any] = None):
        """Log warning message."""
        self.log("WARNING", message, category, extra_data)
    
    def error(self, message: str, category: str = "general", extra_data: Dict[str, Any] = None):
        """Log error message."""
        self.log("ERROR", message, category, extra_data)
    
    def critical(self, message: str, category: str = "general", extra_data: Dict[str, Any] = None):
        """Log critical message."""
        self.log("CRITICAL", message, category, extra_data)
    
    # Specialized logging methods
    def log_sensor_event(self, sensor_id: str, event_type: str, data: Dict[str, Any]):
        """Log sensor-related event."""
        message = f"Sensor {sensor_id}: {event_type}"
        self.info(message, category="sensor", extra_data={
            'sensor_id': sensor_id,
            'event_type': event_type,
            'sensor_data': data
        })
    
    def log_rule_execution(self, rule_id: str, rule_name: str, triggered: bool, 
                          condition_result: Any = None, action_result: Any = None):
        """Log rule execution."""
        status = "triggered" if triggered else "evaluated"
        message = f"Rule '{rule_name}' {status}"
        
        self.info(message, category="rule", extra_data={
            'rule_id': rule_id,
            'rule_name': rule_name,
            'triggered': triggered,
            'condition_result': condition_result,
            'action_result': action_result
        })
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "info"):
        """Log security-related event."""
        message = f"Security event: {event_type}"
        
        level_map = {
            'info': 'INFO',
            'warning': 'WARNING',
            'error': 'ERROR',
            'critical': 'CRITICAL'
        }
        
        level = level_map.get(severity, 'INFO')
        self.log(level, message, category="security", extra_data={
            'event_type': event_type,
            'severity': severity,
            'details': details
        })
    
    def log_simulation_event(self, event_type: str, details: Dict[str, Any]):
        """Log simulation-related event."""
        message = f"Simulation: {event_type}"
        self.info(message, category="simulation", extra_data={
            'event_type': event_type,
            'details': details
        })
    
    # Query methods
    def get_recent_logs(self, count: int = 100, level_filter: str = None, 
                       category_filter: str = None) -> List[SmartHomeLogRecord]:
        """Get recent log records with optional filtering."""
        records = self.log_records[-count:] if count > 0 else self.log_records
        
        # Apply filters
        if level_filter:
            records = [r for r in records if r.level == level_filter.upper()]
        
        if category_filter:
            records = [r for r in records if r.category == category_filter]
        
        return records
    
    def get_logs_by_timerange(self, start_time: datetime, end_time: datetime) -> List[SmartHomeLogRecord]:
        """Get logs within a time range."""
        return [r for r in self.log_records 
                if start_time <= r.timestamp <= end_time]
    
    def get_logs_by_category(self, category: str) -> List[SmartHomeLogRecord]:
        """Get all logs for a specific category."""
        return [r for r in self.log_records if r.category == category]
    
    def search_logs(self, query: str, case_sensitive: bool = False) -> List[SmartHomeLogRecord]:
        """Search logs by message content."""
        if not case_sensitive:
            query = query.lower()
        
        results = []
        for record in self.log_records:
            message = record.message if case_sensitive else record.message.lower()
            if query in message:
                results.append(record)
        
        return results
    
    def export_logs(self, filename: str, format_type: str = "json", 
                   start_time: datetime = None, end_time: datetime = None):
        """Export logs to file."""
        # Get records to export
        if start_time or end_time:
            start_time = start_time or datetime.min
            end_time = end_time or datetime.max
            records = self.get_logs_by_timerange(start_time, end_time)
        else:
            records = self.log_records
        
        try:
            if format_type.lower() == "json":
                data = [record.to_dict() for record in records]
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format_type.lower() == "csv":
                import csv
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Level', 'Category', 'Message'])
                    for record in records:
                        writer.writerow([
                            record.timestamp.isoformat(),
                            record.level,
                            record.category,
                            record.message
                        ])
            
            elif format_type.lower() == "txt":
                with open(filename, 'w') as f:
                    for record in records:
                        f.write(record.format_message() + "\n")
            
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            self.info(f"Exported {len(records)} log records to {filename}")
            
        except Exception as e:
            self.error(f"Failed to export logs: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        total_records = len(self.log_records)
        
        # Count by level
        level_counts = {}
        category_counts = {}
        
        for record in self.log_records:
            level_counts[record.level] = level_counts.get(record.level, 0) + 1
            category_counts[record.category] = category_counts.get(record.category, 0) + 1
        
        # Calculate time range
        if self.log_records:
            first_log = min(self.log_records, key=lambda r: r.timestamp)
            last_log = max(self.log_records, key=lambda r: r.timestamp)
            time_range = (last_log.timestamp - first_log.timestamp).total_seconds()
        else:
            time_range = 0
        
        return {
            'total_records': total_records,
            'level_counts': level_counts,
            'category_counts': category_counts,
            'time_range_seconds': time_range,
            'max_records': self.max_records
        }