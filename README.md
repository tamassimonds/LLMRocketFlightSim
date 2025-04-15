# Rocket Package

A Python package for rocket flight simulation and design analysis, built on RocketPy.

## Overview

Rocket Package provides tools for rocket design, flight simulation, and performance evaluation. It's designed to work with LLM (Large Language Model) responses to evaluate and score rocket designs automatically.

## Installation

### From GitHub

```bash
pip install git+https://github.com/tamassimonds/LLMRocketFlightSim.git
```

### Local Development

```bash
git clone https://github.com/tamassimonds/LLMRocketFlightSim.git
cd LLMRocketFlightSim
pip install -e .
```

## Usage

### Basic Usage

```python
from rocket_package.rocket_interface import process_llm_response

# Your LLM response containing a rocket design
llm_response = """
### Reasoning for Rocket Design Choices

#### **1. Motor Selection**
- **Target Apogee**: 3000 meters is a moderately high altitude, requiring a motor with sufficient total impulse.
- **Choice**: **Pro75M1670** (best balance of thrust, impulse, and weight).

... (truncated for brevity) ...

### Final Design (Python Dictionary)
```python
config = {
    "motor_choice": "Pro75M1670",
    "rocket_body": {
        "radius": 0.075,
        "length": 3,
        "material": "carbon_fiber",
        "thickness": 0.002,
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "von karman",
            "length": 0.6,
            "material": "carbon_fiber",
        },
        "fins": {
            "number": 4,
            "root_chord": 0.2,
            "tip_chord": 0.1,
            "span": 0.15,
            "cant_angle": 0,
            "material": "composite",
            "thickness": 0.003,
        },
        "tail": {
            "length": 0.1,
            "top_radius": 0.075,
            "bottom_radius": 0.074,
            "material": "carbon_fiber",
        },
    },
    "parachutes": {
        "main": {
            "name": "Main",
            "cd_s": 1.0,
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
        "drogue": {
            "name": "Drogue",
            "cd_s": 0.2,
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
    },
    "launch": {
        "rail_length": 5.0,
        "inclination": 85,
        "heading": 90,
    },
}
```
"""

# Process the LLM response with a target apogee of 3000 meters
response = process_llm_response(
    llm_response, 
    target_apogee=3000, 
    wind_speed=20,  # m/s
    wind_direction="E",  # East
    save_outputs=True  # Save simulation outputs to files
)

# Calculate reward based on how close the rocket got to the target apogee
from math import exp

target_apogee = 3000
reward = 0

if response['simple_results']:
    # Basic reward for valid design that could be simulated
    reward += 0.05 
    
    # Calculate distance-based reward (exponential decay based on error)
    distance_reward = exp(-abs(response['simple_results']["apogee"] - target_apogee) / (target_apogee*0.1))
    reward += distance_reward

print(f"Reward score: {reward}")
print(f"Apogee: {response['simple_results']['apogee']} m")
```

### Design Rule Checks

The package includes design rule checks to validate rocket configurations:

- Motor compatibility with body dimensions
- Material validation
- Component dimension constraints
- Aerodynamic stability checks
- Physical feasibility validation

Key constraints include:
- Top and bottom radius of the tail cannot be the same
- Body radius must be larger than the motor radius
- Body thickness must be less than body radius
- Total rocket length has realistic bounds

### Output Files

When `save_outputs=True`, the following files are generated in the `outputs` directory:

- Flight trajectory plots
- 3D rocket visualization
- Detailed simulation results
- KML files for Google Earth visualization

## Package Structure

```
rocket_package/
├── configs/             # Engine files and configuration data
├── src/                 # Source code
│   ├── analysis/        # Analysis tools
│   ├── models/          # Rocket and simulation models
│   │   └── motors/      # Motor definitions
│   └── utils/           # Utility functions
├── rocket_interface.py  # Main interface for LLM integration
├── rocket_designer.py   # Design optimization tools
├── rocket_simulator.py  # Core simulation functionality
├── calculate_reward.py  # Reward calculation utilities
└── default_configs.py   # Default rocket configurations
```

## Available Motors

The package includes several pre-configured motors:

- Pro75M1670
- AeroTechK700W
- CesaroniM1670
- AeroTechH128W
- CesaroniO3700
- CesaroniO5800
- CesaroniK160

## Dependencies

- rocketpy
- numpy
- matplotlib
- pandas
- tabulate

## License

MIT License

python3 benchmark.py --prompt prompt.txt --model claude-3-7-sonnet-20250219  --apogee 3048 --iterations 5 --wind-speed 5 --wind-direction E --output-dir benchmarks
python3 benchmark.py --prompt prompt-target.txt --model o1-mini --target-x 4000 --target-y 4000 --iterations 1 --batch-size 5 --wind-speed 5 --wind-direction E --output-dir target-benchmarks 