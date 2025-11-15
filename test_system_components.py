#!/usr/bin/env python3
"""
Test script for system components integration.
"""

import sys
import os
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from system.components import ComponentManager, APIServer, DatabaseServer, MQTTBroker

def test_component_manager():
    """Test the component manager functionality."""
    print("Testing Component Manager...")
    
    # Create component manager
    manager = ComponentManager()
    
    # Create and register components
    api_server = APIServer()
    database = DatabaseServer()
    mqtt_broker = MQTTBroker()
    
    manager.register_component(api_server)
    manager.register_component(database)
    manager.register_component(mqtt_broker)
    
    print(f"Registered {len(manager.components)} components:")
    for comp_id, comp in manager.components.items():
        print(f"  - {comp_id}: {comp.name} ({comp.status.value})")
    
    # Test starting components
    print("\nStarting API Server...")
    success = manager.start_component("api_server")
    print(f"Start result: {success}")
    
    # Wait a moment
    time.sleep(2)
    
    # Check status
    status = manager.get_component_status("api_server")
    if status:
        print(f"API Server status: {status['status']} (PID: {status.get('pid', 'N/A')})")
    
    # Test logs
    logs = manager.get_component_logs("api_server", limit=5)
    print(f"Recent logs ({len(logs)} entries):")
    for log in logs[-3:]:
        print(f"  {log.timestamp} [{log.level}] {log.message}")
    
    # Stop components
    print("\nStopping all components...")
    manager.stop_all_components()
    
    # Final status
    print("\nFinal status:")
    for comp_id, comp in manager.components.items():
        status = comp.get_status_info()
        print(f"  - {comp_id}: {status['status']}")

def test_individual_component():
    """Test individual component functionality."""
    print("\n" + "="*50)
    print("Testing Individual Component...")
    
    # Test API Server
    api_server = APIServer()
    print(f"Created API Server: {api_server.name}")
    print(f"Initial status: {api_server.status.value}")
    
    # Start the component
    print("Starting API Server...")
    result = api_server.start()
    print(f"Start result: {result}")
    
    # Wait a moment
    time.sleep(1)
    
    # Check status
    print(f"Status after start: {api_server.status.value}")
    if api_server.process:
        print(f"Process PID: {api_server.process.pid}")
    
    # Stop the component
    print("Stopping API Server...")
    result = api_server.stop()
    print(f"Stop result: {result}")
    print(f"Final status: {api_server.status.value}")

if __name__ == "__main__":
    print("System Components Integration Test")
    print("=" * 50)
    
    try:
        test_component_manager()
        test_individual_component()
        print("\n" + "="*50)
        print("All tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTest finished.")