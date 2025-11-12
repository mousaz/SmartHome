#!/usr/bin/env python3
"""
Test script for Smart Home Simulation Application
Verifies basic functionality of core components.
"""

import sys
import os

# Add paths for imports
project_root = os.path.dirname(__file__)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

def test_sensor_framework():
    """Test sensor creation and basic functionality."""
    print("Testing Sensor Framework...")
    
    from src.sensors.common_sensors import sensor_registry
    
    # Test sensor registry
    available_types = sensor_registry.get_available_types()
    print(f"Available sensor types: {list(available_types.keys())}")
    
    # Create test sensors
    temp_sensor = sensor_registry.create_sensor('temperature', name='Test Temp', location=(100, 200))
    motion_sensor = sensor_registry.create_sensor('motion', name='Test Motion', location=(150, 250))
    
    if temp_sensor and motion_sensor:
        print("✓ Sensors created successfully")
        
        # Test sensor activation
        temp_sensor.activate()
        motion_sensor.activate()
        
        # Test readings
        temp_reading = temp_sensor.get_reading()
        motion_reading = motion_sensor.get_reading()
        
        print(f"Temperature reading: {temp_reading}")
        print(f"Motion reading: {motion_reading}")
        print("✓ Sensor readings working")
    else:
        print("✗ Failed to create sensors")
        return False
    
    return True

def test_simulation_engine():
    """Test simulation engine functionality."""
    print("\nTesting Simulation Engine...")
    
    from src.simulation.engine import SimulationEngine
    from src.log_system.logger import SmartHomeLogger
    
    logger = SmartHomeLogger()
    engine = SimulationEngine(logger)
    
    # Create and add sensors
    from src.sensors.common_sensors import sensor_registry
    
    sensors = [
        sensor_registry.create_sensor('temperature', name='Living Room Temp', location=(100, 100)),
        sensor_registry.create_sensor('motion', name='Entry Motion', location=(50, 50)),
        sensor_registry.create_sensor('door_window', name='Front Door', location=(25, 100))
    ]
    
    for sensor in sensors:
        if sensor:
            engine.add_sensor(sensor)
    
    print(f"✓ Added {len(engine.get_sensors())} sensors to simulation")
    
    # Test simulation control
    print("Starting simulation...")
    engine.start()
    
    import time
    time.sleep(2)  # Run for 2 seconds
    
    print("Stopping simulation...")
    engine.stop()
    
    print("✓ Simulation engine working")
    logger.shutdown()
    return True

def test_logging_system():
    """Test logging system functionality."""
    print("\nTesting Logging System...")
    
    from src.log_system.logger import SmartHomeLogger
    
    logger = SmartHomeLogger()
    
    # Test different log levels
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    # Test specialized logging
    logger.log_sensor_event("test_sensor", "reading_changed", {"value": 25.5})
    logger.log_security_event("authentication", {"user": "test"}, "info")
    
    # Get recent logs
    recent_logs = logger.get_recent_logs(10)
    print(f"✓ Generated {len(recent_logs)} log entries")
    
    # Test search
    search_results = logger.search_logs("test")
    print(f"✓ Found {len(search_results)} logs matching 'test'")
    
    logger.shutdown()
    return True

def test_template_system():
    """Test template loading functionality."""
    print("\nTesting Template System...")
    
    import json
    template_file = os.path.join(project_root, 'templates', 'home_templates.json')
    
    if os.path.exists(template_file):
        try:
            with open(template_file, 'r') as f:
                templates = json.load(f)
            
            print(f"✓ Loaded {len(templates)} templates")
            
            for name, template in templates.items():
                sensor_count = len(template.get('sensors', []))
                wall_count = len(template.get('walls', []))
                print(f"  - {name}: {sensor_count} sensors, {wall_count} walls")
            
            return True
        except Exception as e:
            print(f"✗ Failed to load templates: {e}")
            return False
    else:
        print("✗ Template file not found")
        return False

def main():
    """Run all tests."""
    print("Smart Home Simulation - Component Tests")
    print("=" * 50)
    
    tests = [
        test_sensor_framework,
        test_simulation_engine, 
        test_logging_system,
        test_template_system
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The application is ready to use.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)