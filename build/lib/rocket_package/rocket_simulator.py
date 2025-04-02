#!/usr/bin/env python3
"""
Rocket Simulator - A simple demonstration of using the rocket_design package.

This script shows how to:
1. Define a rocket configuration
2. Run a simulation
3. Analyze the results
"""

import os
import sys
import json
import argparse
from rocket_design import (
    simulate_from_config, 
    process_llm_response, 
    print_result_summary,
    list_motor_files,
    get_motor_file_path
)

def simulate_from_file(config_file, target_apogee, output_dir="outputs", wind_speed=0, wind_direction="N"):
    """
    Run a simulation from a JSON config file.
    
    Args:
        config_file (str): Path to the JSON config file
        target_apogee (float): Target apogee in meters
        output_dir (str): Directory for outputs
        wind_speed (float): Wind speed in m/s
        wind_direction (str): Wind direction
        
    Returns:
        dict: Simulation results
    """
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print(f"Running simulation for config: {config_file}")
    print(f"Target apogee: {target_apogee}m")
    print(f"Wind: {wind_speed} m/s from {wind_direction}\n")
    
    result = simulate_from_config(
        config=config,
        target_apogee=target_apogee,
        output_dir=output_dir,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        save_outputs=True
    )
    
    return result

def main():
    """Main entry point for the rocket simulator."""
    parser = argparse.ArgumentParser(description="Rocket flight simulator")
    parser.add_argument('--config', type=str, help='Path to a JSON configuration file')
    parser.add_argument('--llm-response', type=str, help='Path to a text file containing an LLM response')
    parser.add_argument('--apogee', type=float, default=1000, help='Target apogee in meters')
    parser.add_argument('--wind-speed', type=float, default=0, help='Wind speed in m/s')
    parser.add_argument('--wind-direction', type=str, default="N", help='Wind direction (N, S, E, W, etc.)')
    parser.add_argument('--output-dir', type=str, default="outputs", help='Directory for outputs')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Print available motor files
    print("\nAvailable motor files:")
    for motor_file in list_motor_files():
        print(f"  - {motor_file}")
    print()
    
    # Run simulation based on arguments
    if args.config:
        result = simulate_from_file(
            config_file=args.config,
            target_apogee=args.apogee,
            output_dir=args.output_dir,
            wind_speed=args.wind_speed,
            wind_direction=args.wind_direction
        )
        print_result_summary(result, args.apogee)
        
    elif args.llm_response:
        with open(args.llm_response, 'r') as f:
            llm_response = f.read()
        
        result = process_llm_response(
            llm_response=llm_response,
            target_apogee=args.apogee,
            output_dir=args.output_dir,
            wind_speed=args.wind_speed,
            wind_direction=args.wind_direction,
            save_outputs=True
        )
        print_result_summary(result, args.apogee)
        
    else:
        # Define a sample configuration
        sample_config = {
            "motor": {
                "designation": "AeroTechK700W",
                "thrust_source": str(get_motor_file_path("AeroTech_K700W.eng")),
            },
            "body": {
                "radius": 0.075,
                "length": 2.5,
                "material": "aluminum",
                "thickness": 0.002,
                "total_mass": 8.0,
                "dry_mass": 6.5,
            },
            "nose_cone": {
                "shape": "von karman",
                "length": 0.4,
                "material": "plastic",
                "diameter": 0.15,
            },
            "fins": {
                "count": 4,
                "root_chord": 0.2,
                "tip_chord": 0.1,
                "span": 0.15,
                "sweep": 0.05,
                "cant_angle": 0,
                "material": "aluminum",
                "thickness": 0.003,
            },
            "parachutes": {
                "Main": {
                    "cd_s": 1.5,
                    "deploy_at_apogee": False,
                    "deployment_altitude": 300,
                    "sampling_rate": 100,
                    "noise": (0, 5.0, 0.5),
                },
                "Drogue": {
                    "cd_s": 0.5,
                    "deploy_at_apogee": True,
                    "deployment_altitude": 0,
                    "sampling_rate": 100,
                    "noise": (0, 5.0, 0.5),
                },
            },
            "launch": {
                "rail_length": 3.0,
                "rail_inclination": 85,
                "rail_azimuth": 0,
            },
            "environment": {
                "latitude": 28.5,
                "longitude": -80.5,
                "elevation": 0,
                "date": (2023, 3, 15, 12),
            },
            "payload": {
                "mass": 0.5,
                "position": 0.5,
            },
        }
        
        # Save the sample configuration
        sample_config_path = os.path.join(args.output_dir, "sample_config.json")
        with open(sample_config_path, 'w') as f:
            json.dump(sample_config, f, indent=2, default=str)
        
        print(f"Saved sample configuration to {sample_config_path}")
        print(f"You can run the simulation with: python {sys.argv[0]} --config {sample_config_path}")
        print(f"Or process an LLM response with: python {sys.argv[0]} --llm-response path/to/response.txt")

if __name__ == "__main__":
    main() 