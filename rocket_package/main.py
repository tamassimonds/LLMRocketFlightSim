
import os
import argparse
import json
from rocket_package.src.models.simulation import RocketSimulation
from rocket_package.src.models.motors.motor_loader import _save_predefined_motors

config = {
    "goal_altitude": 10000,  # [m] desired altitude
    "motor_choice": "CesaroniM1670",  # Which motor to use from the motors dict
    "rocket_body": {
        "radius": 0.075,  # [m]
        "length": 2.5,         # [m] cylindrical section
        "material": "carbon_fiber",  # material key
        "thickness": 0.005,  # [m] wall thickness
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "vonKarman",
            "length": 0.6,  # [m]
            "material": "carbon_fiber",  # material key
        },
        "fins": {
            "number":4,  # Four fins for stability
            "root_chord": 0.15,  # Root chord length of 0.15 meters
            "tip_chord": 0.05,  # Tip chord length of 0.05 meters
            "span": 0.25,  # Span of 0.25 meters for good stability
            "cant_angle": 1,  # Slight cant angle for improved stability
            "material": "fiberglass",  # Lightweight and durable material
            "thickness": 0.005,  # 5mm thickness for optimal strength without excess weight
        },
        "tail": {
            "length": 0.3,     # [m]
            "top_radius": 0.075,  # [m]
            "bottom_radius": 0.0435,  # [m]
            "material": "fiberglass",  # assume same as rocket body
        },
    },
    "parachutes": {
        "main": {
            "name": "Main",
            "cd_s": 10.0,
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
        "drogue": {
            "name": "Drogue",
            "cd_s": 1.0,
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
    },
    "launch": {
        "rail_length": 8,  # [m]
        "inclination": 45,   # [degrees]
        "heading": 0,        # [degrees]
    },
    "payload": {
        "mass": 5.0,      # payload mass in kg
        "position": 0.1,  # payload position in meters (positive is forward)
    },
    "env": {
        "wind_u": 20, # m/s
        "wind_v": 0,  # m/s
    },
}


# Initialize simulation
simulation = RocketSimulation(config, output_dir="outputs")

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

# After running the simulation
simulation = RocketSimulation(config)
simulation.setup_environment()
simulation.build_rocket()
simulation.run_simulation()

# Get all results
results = simulation.analyze_results()

# Access specific values
max_apogee = results["flight"]["max_apogee"]
max_speed = results["flight"]["max_speed"]
flight_time = results["flight"]["flight_time"]
horizontal_distance = results["flight"]["horizontal_distance"]

# Access structural analysis
structural_failure = results["structural"]["overall_failure"]
fin_safety_factor = results["structural"]["fins"]["safety_factor"]
body_safety_factor = results["structural"]["body"]["bending_safety_factor"]

# Access costs
total_cost = results["materials"]["total_cost"]
material_costs = results["materials"]["costs"]  # Dictionary of costs by material
material_masses = results["materials"]["materials"]  # Dictionary of masses by material

# Example: print specific results
print(f"Max Apogee: {max_apogee:.2f} m")
print(f"Total Cost: ${total_cost:.2f}")
print(f"Structural Failure: {structural_failure}")


# Save plots
saved_files = simulation.save_plots()
print(f"\nSaved {len(saved_files)} files to outputs")