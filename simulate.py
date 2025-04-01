#!/usr/bin/env python3
"""
Example script demonstrating how to use the rocket simulation framework.
"""
import os
import argparse
import json
from src.models.simulation import RocketSimulation
from src.models.motors.motor_loader import _save_predefined_motors

# Default configurations
from default_configs import standard_config as default_config

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Rocket simulation example")
    parser.add_argument("-c", "--config", type=str, help="Path to configuration file")
    parser.add_argument("-o", "--output", type=str, default="outputs", help="Output directory")
    parser.add_argument("-w", "--wind-u", type=float, default=None, help="Wind speed (East-West) in m/s")
    parser.add_argument("-v", "--wind-v", type=float, default=None, help="Wind speed (North-South) in m/s")
    parser.add_argument("-m", "--motor", type=str, default=None, help="Motor choice")
    parser.add_argument("--save-motors", action="store_true", help="Save predefined motors to JSON files")
    
    return parser.parse_args()

def load_config(config_path=None):
    """Load configuration from file or use default."""
    if config_path is None:
        print("Using default configuration")
        return default_config
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        print(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Using default configuration")
        return default_config

def main():
    """Run the example simulation."""
    args = parse_args()
    
    # Save predefined motors if requested
    if args.save_motors:
        _save_predefined_motors()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override motor choice if specified
    if args.motor is not None:
        config["motor_choice"] = args.motor
        print(f"Using motor: {args.motor}")
    
    # Override wind if specified
    if args.wind_u is not None or args.wind_v is not None:
        if "env" not in config:
            config["env"] = {}
        
        if args.wind_u is not None:
            config["env"]["wind_u"] = args.wind_u
            print(f"Setting East-West wind to {args.wind_u} m/s")
        
        if args.wind_v is not None:
            config["env"]["wind_v"] = args.wind_v
            print(f"Setting North-South wind to {args.wind_v} m/s")
    
    # Initialize simulation
    simulation = RocketSimulation(config, output_dir=args.output)
    
    # Set up environment with config-defined wind
    simulation.setup_environment()
    
    # Build rocket
    rocket = simulation.build_rocket()
    
    # Run simulation
    flight = simulation.run_simulation()
    
    # Analyze results
    results = simulation.analyze_results()
    
    # Print summary
    simulation.print_summary()
    
    # Save plots
    saved_files = simulation.save_plots()
    print(f"\nSaved {len(saved_files)} files to {args.output}")

if __name__ == "__main__":
    main() 