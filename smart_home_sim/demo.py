#!/usr/bin/env python3
"""
Demo script showing basic usage of the Smart Home Simulation Application.
This script demonstrates how to programmatically create and run a simulation.
"""

import sys
import os
import time

# Add paths for imports
project_root = os.path.dirname(__file__)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

def create_demo_simulation():
    """Create a demonstration simulation setup."""
    print("Creating Smart Home Simulation Demo...")
    
    # Initialize components
    from src.log_system.logger import SmartHomeLogger
    from src.simulation.engine import SimulationEngine
    from src.sensors.common_sensors import sensor_registry
    
    logger = SmartHomeLogger()
    engine = SimulationEngine(logger)
    
    print("✓ Initialized simulation engine and logger")
    
    # Create a variety of sensors for demo
    demo_sensors = [
        # Living room sensors
        {
            'type': 'temperature',
            'name': 'Living Room Temperature',
            'location': (150, 150),
            'config': {'base_temp': 22.0, 'accuracy': 0.3}
        },
        {
            'type': 'motion',
            'name': 'Living Room Motion',
            'location': (180, 180),
            'config': {'trigger_probability': 0.15, 'sensitivity': 0.8}
        },
        {
            'type': 'light',
            'name': 'Living Room Light Sensor',
            'location': (120, 120),
            'config': {'day_night_simulation': True}
        },
        
        # Entry sensors
        {
            'type': 'door_window',
            'name': 'Front Door',
            'location': (100, 50),
            'config': {'sensor_type': 'door', 'state_change_probability': 0.08}
        },
        {
            'type': 'motion',
            'name': 'Entry Motion',
            'location': (100, 80),
            'config': {'trigger_probability': 0.12}
        },
        
        # Kitchen sensors
        {
            'type': 'temperature',
            'name': 'Kitchen Temperature', 
            'location': (300, 200),
            'config': {'base_temp': 24.0, 'accuracy': 0.4}
        },
        {
            'type': 'smoke',
            'name': 'Kitchen Smoke Detector',
            'location': (320, 180),
            'config': {'alarm_probability': 0.002}
        },
        {
            'type': 'humidity',
            'name': 'Kitchen Humidity',
            'location': (280, 220),
            'config': {'base_humidity': 55.0}
        },
        
        # Bedroom sensors
        {
            'type': 'temperature',
            'name': 'Bedroom Temperature',
            'location': (450, 120),
            'config': {'base_temp': 20.5}
        },
        {
            'type': 'door_window',
            'name': 'Bedroom Window',
            'location': (480, 50),
            'config': {'sensor_type': 'window', 'state_change_probability': 0.05}
        }
    ]
    
    # Create and add sensors to simulation
    created_sensors = []
    for sensor_def in demo_sensors:
        sensor = sensor_registry.create_sensor(
            sensor_def['type'],
            name=sensor_def['name'],
            location=sensor_def['location'],
            config=sensor_def['config']
        )
        
        if sensor:
            engine.add_sensor(sensor)
            created_sensors.append(sensor)
            print(f"  + Added {sensor.name} ({sensor.get_sensor_type()})")
    
    print(f"✓ Created {len(created_sensors)} sensors")
    
    return engine, logger, created_sensors

def run_demo_simulation(engine, logger, duration=30):
    """Run the demo simulation for specified duration."""
    print(f"\nRunning simulation for {duration} seconds...")
    print("Monitoring sensor events (press Ctrl+C to stop early)")
    print("-" * 60)
    
    # Set up event monitoring
    event_count = 0
    
    def event_monitor(event):
        nonlocal event_count
        event_count += 1
        
        if event.event_type == 'sensor_data':
            sensor = engine.get_sensor(event.sensor_id)
            if sensor:
                print(f"[{event.timestamp.strftime('%H:%M:%S')}] {sensor.name}: {event.data}")
        elif event.event_type in ['sensor_activated', 'sensor_deactivated']:
            sensor = engine.get_sensor(event.sensor_id)
            if sensor:
                print(f"[{event.timestamp.strftime('%H:%M:%S')}] {sensor.name} {event.event_type}")
    
    engine.add_event_callback(event_monitor)
    
    try:
        # Start simulation
        engine.start()
        start_time = time.time()
        
        # Run for specified duration
        while time.time() - start_time < duration:
            time.sleep(1)
            
            # Print periodic status
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0 and elapsed > 0:
                fps = engine.get_fps()
                sensor_count = len(engine.get_sensors())
                sim_time = engine.get_simulation_time()
                print(f"[Status] Elapsed: {elapsed}s, Events: {event_count}, "
                      f"Sensors: {sensor_count}, FPS: {fps:.1f}, Sim Time: {sim_time}")
        
        # Stop simulation
        engine.stop()
        
    except KeyboardInterrupt:
        print("\n⚠️ Simulation interrupted by user")
        engine.stop()
    
    print("-" * 60)
    print(f"✓ Demo completed. Total events processed: {event_count}")

def show_demo_statistics(engine, logger):
    """Show statistics from the demo run."""
    print(f"\nDemo Statistics:")
    print("=" * 40)
    
    # Sensor statistics
    sensors = engine.get_sensors()
    print(f"Total Sensors: {len(sensors)}")
    
    sensor_types = {}
    active_sensors = 0
    
    for sensor in sensors.values():
        sensor_type = sensor.get_sensor_type()
        sensor_types[sensor_type] = sensor_types.get(sensor_type, 0) + 1
        
        if sensor.status.value == 'active':
            active_sensors += 1
    
    print(f"Active Sensors: {active_sensors}")
    print(f"Sensor Types:")
    for sensor_type, count in sensor_types.items():
        print(f"  - {sensor_type.title()}: {count}")
    
    # Logging statistics
    log_stats = logger.get_statistics()
    print(f"\nLog Statistics:")
    print(f"Total Log Records: {log_stats['total_records']}")
    
    if log_stats['level_counts']:
        print("Log Levels:")
        for level, count in log_stats['level_counts'].items():
            print(f"  - {level}: {count}")
    
    if log_stats['category_counts']:
        print("Log Categories:")
        for category, count in log_stats['category_counts'].items():
            print(f"  - {category}: {count}")

def main():
    """Main demo function."""
    print("Smart Home Simulation - Interactive Demo")
    print("=" * 50)
    
    try:
        # Create demo simulation
        engine, logger, sensors = create_demo_simulation()
        
        # Ask user for simulation duration
        print(f"\nDemo is ready with {len(sensors)} sensors configured.")
        try:
            duration_input = input("Enter simulation duration in seconds (default 30): ").strip()
            duration = int(duration_input) if duration_input else 30
        except ValueError:
            duration = 30
        
        # Run simulation
        run_demo_simulation(engine, logger, duration)
        
        # Show statistics
        show_demo_statistics(engine, logger)
        
        # Cleanup
        logger.shutdown()
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"\nTo run the full GUI application, use: python main.py")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)