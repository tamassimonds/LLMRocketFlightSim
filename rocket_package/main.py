
import os
import argparse
import json
from rocket_package.src.models.simulation import RocketSimulation
from rocket_package.src.models.motors.motor_loader import _save_predefined_motors

config = {
    "motor_choice": "Pro75M1670",
    "rocket_body": {
        "radius": 0.076,        # meters (> 0.075 m motor radius)
        "length": 1.3,          # meters
        "material": "fiberglass",
        "thickness": 0.0028,    # 2.8 mm wall thickness
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "ogive",
            "length": 0.3,       # nose cone length in meters
            "material": "fiberglass",
        },
        "fins": {
            "number": 3,
            "root_chord": 0.14,  # meters
            "tip_chord": 0.06,   # meters
            "span": 0.1,         # meters
            "cant_angle": 0,     # degrees
            "material": "plywood",
            "thickness": 0.0028, # 2.8 mm fin thickness
        },
        "tail": {
            "length": 0.07,      # meters
            "top_radius": 0.076,
            "bottom_radius": 0.065,
            "material": "fiberglass",
        },
    },
    "parachutes": {
        "main": {
            "name": "Main",
            "cd_s": 0.70,         # ensures ~5 m/s landing speed
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
        "drogue": {
            "name": "Drogue",
            "cd_s": 0.05,
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
    },
    "launch": {
        "rail_length": 2.3,  # meters
        "inclination": 90,   # degrees (vertical)
        "heading": 0,        # degrees
    },
    "payload": {
        "mass": 0.2,         # kg
        "position": 0.65,    # meters from rocket center
    }
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