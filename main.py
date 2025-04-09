import os
import argparse
import json
from rocket_package.src.models.simulation import RocketSimulation
from rocket_package.src.models.motors.motor_loader import _save_predefined_motors
from rocket_package.calculate_reward import calculate_reward
config = {
    "motor_choice": "CesaroniO5800",
    "rocket_body": {
        "radius": 0.16,  # Body radius in meters (must be greater than motor radius of 0.15m)
        "length": 0.95,    # Body length in meters (slightly reduced for mass optimization)
        "material": "carbon_fiber",
        "thickness": 0.0015,  # Wall thickness in meters (further reduced to save mass)
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "ogive",
            "length": 0.23,  # Nose cone length in meters (optimized for aerodynamics)
            "material": "balsa_wood",
        },
        "fins": {
            "number": 4,
            "root_chord": 0.11,      # Fin root chord in meters (slightly reduced)
            "tip_chord": 0.055,      # Fin tip chord in meters (slightly reduced)
            "span": 0.24,             # Fin span in meters (slightly reduced)
            "cant_angle": 0.5,        # Cant angle in degrees
            "material": "fiberglass",
            "thickness": 0.0015       # Fin thickness in meters (further reduced to save mass)
        },
        "tail": {
            "length": 0.18,           # Tail length in meters (slightly reduced)
            "top_radius": 0.034,      # Top radius in meters
            "bottom_radius": 0.044,   # Bottom radius in meters
            "material": "carbon_fiber",
        },
    },
    "parachutes": {
        "main": {
            "name": "Main",
            "cd_s": 0.21,             # Main parachute CD_s (slightly reduced)
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.25,               # Slightly reduced lag for quicker deployment
            "noise": (0, 8.0, 0.5),
        },
        "drogue": {
            "name": "Drogue",
            "cd_s": 0.17,              # Drogue parachute CD_s (slightly reduced)
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.25,               # Slightly reduced lag for quicker deployment
            "noise": (0, 8.0, 0.5),
        },
    },
    "launch": {
        "rail_length": 0.95,           # Length of the launch rail in meters (slightly reduced)
        "inclination": 90,             # Rail inclination in degrees (vertical launch)
        "heading": 0,                  # Launch heading in degrees (straight up)
    },
    "payload": {
        "mass": 1.57,                   # Payload mass in kg (includes ballast)
        "position": 0.48               # Payload position relative to rocket center in meters (slightly adjusted for balance)
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

print(results)

# # Save plots
# saved_files = simulation.save_plots()
# print(f"\nSaved {len(saved_files)} files to outputs")

# Calculate the reward score using the specific values from the results
reward_score, reward_breakdown = calculate_reward(
    apogee=max_apogee,
    target_apogee=3048,
    horizontal_distance=horizontal_distance,
    total_cost=total_cost,
    impact_velocity=results["flight"].get("impact_velocity", 0),
    structural_failure=structural_failure
)

# Format reward score as percentage 
reward_percentage = reward_score * 100

# Print the reward score
print(f"\nPerformance Score: {reward_percentage:.2f}%")

