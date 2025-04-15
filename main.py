import os
import math
import argparse
import json
import numpy as np
from rocket_package.src.models.simulation import RocketSimulation
from rocket_package.src.models.motors.motor_loader import _save_predefined_motors
from rocket_package.calculate_reward import calculate_bullseye_landing_reward, format_bullseye_landing_report
from rocket_package.calculate_reward import calculate_target_point_reward
from rocket_package.calculate_reward import calculate_reward

# Define target landing coordinates (far from the origin for challenge)
TARGET_X = 4000.0  # Target X coordinate in meters
TARGET_Y = 4000.0  # Target Y coordinate in meters

config = {
    "motor_choice": "Pro75M1670",
    "rocket_body": {
        "radius": 0.1,  # Body radius in meters
        "length": 0.3,    # Body length in meters
        "material": "plywood",
        "thickness": 0.005,  # Wall thickness in meters
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "ogive",
            "length": 0.2,  # Nose cone length in meters
            "material": "plywood",
        },
        "fins": {
            "number": 3,
            "root_chord": 0.15,  # Fin root chord in meters
            "tip_chord": 0.075,  # Fin tip chord in meters
            "span": 0.3,         # Fin span in meters
            "cant_angle": 0.5,   # Cant angle in degrees
            "material": "plywood",
            "thickness": 0.005   # Fin thickness in meters
        },
        "tail": {
            "length": 0.4,  # Tail length in meters
            "top_radius": 0.04,  # Top radius in meters
            "bottom_radius": 0.05,  # Bottom radius in meters
            "material": "plywood",
        },
    },
    "parachutes": {
        "main": {
            "name": "Main",
            "cd_s": 5,  # Main parachute CD_s
            "trigger": "apogee",
            "sampling_rate": 5,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
        "drogue": {
            "name": "Drogue",
            "cd_s": 3,  # Drogue parachute CD_s
            "trigger": "apogee",
            "sampling_rate": 5,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
    },
    "launch": {
        "rail_length": 2,  # Length of the launch rail in meters
        "inclination": 90,   # Rail inclination in degrees (vertical)
        "heading": 0,        # Launch heading in degrees (straight up)
    },
    "payload": {
        "mass": 10,  # Payload mass in kg
        "position": -0.5  # Payload position relative to rocket center in meters
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

# Access key flight results
flight_results = results["flight"]
landing_x = float(flight_results.get("x_final", 0))
landing_y = float(flight_results.get("y_final", 0))

# Access other important values
max_apogee = float(flight_results["max_apogee"])
flight_time = float(flight_results["flight_time"])
total_cost = float(results["materials"]["total_cost"])
structural_failure = bool(results["structural"]["overall_failure"])
impact_velocity = float(flight_results.get("impact_velocity", 10.0))  # Default if not available

# Calculate distance to target
distance_to_target = math.sqrt((landing_x - TARGET_X)**2 + (landing_y - TARGET_Y)**2)
horizontal_distance = math.sqrt(landing_x**2 + landing_y**2)
# Print flight details
print(f"\n----- FLIGHT DETAILS -----")
print(f"Max Apogee: {max_apogee:.2f} m")
print(f"Flight Time: {flight_time:.2f} s")
print(f"Landing Position: ({landing_x:.2f}m, {landing_y:.2f}m)")
print(f"Target Position: ({TARGET_X:.2f}m, {TARGET_Y:.2f}m)")
print(f"Distance to Target: {distance_to_target:.2f}m")
print(f"Total Cost: ${total_cost:.2f}")
print(f"Structural Integrity: {'FAILED' if structural_failure else 'PASSED'}")

# Calculate reward using dynamic bullseye landing reward function
reward_score, reward_breakdown = calculate_bullseye_landing_reward(
    landing_x=landing_x,
    landing_y=landing_y,
    target_x=TARGET_X,
    target_y=TARGET_Y,
    total_cost=total_cost,
    impact_velocity=impact_velocity,
    structural_failure=structural_failure
)

# Format and print the reward report
reward_report = format_bullseye_landing_report(reward_score, reward_breakdown)
print("\n" + reward_report)

# Save the reward details to a file
with open("outputs/dynamic_bullseye_reward.json", "w") as f:
    json.dump({k: float(v) if isinstance(v, np.number) else v 
              for k, v in reward_breakdown.items()}, f, indent=2)

# Save plots
# saved_files = simulation.save_plots()
# print(f"\nSaved {len(saved_files)} files to outputs")

# Print final score as percentage
reward_percentage = reward_score * 100
print(f"\nFinal Bullseye Score: {reward_percentage:.2f}%")

# Save the landing accuracy details for future analysis
landing_data = {
    "target": {"x": TARGET_X, "y": TARGET_Y},
    "landing": {"x": float(landing_x), "y": float(landing_y)},
    "error": float(reward_breakdown["landing_error"]),
    "sigma": float(reward_breakdown.get("landing_sigma", 50.0)),
    "bullseye_class": reward_breakdown.get("bullseye_class", "UNKNOWN"),
    "score": float(reward_percentage)
}

with open("outputs/landing_accuracy.json", "w") as f:
    json.dump(landing_data, f, indent=2)

reward_score, reward_breakdown = calculate_reward(
    apogee=max_apogee,
    target_apogee=3048,
    horizontal_distance=horizontal_distance,
    total_cost=total_cost,
    impact_velocity=impact_velocity,
    structural_failure=structural_failure
)
print(reward_score)
print(reward_breakdown)