#!/usr/bin/env python3
"""
Generate prompts for LLMs with rocket specifications and all available options.
"""

import os
import argparse
import json
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import tabulate
from src.models.materials import materials
from src.models.motors import EngFileLoader
from src.models.motors import motors as available_motor_configs

def generate_rocket_design_prompt(target_apogee, payload_mass=None, stability_margin=None, 
                                  horizontal_distance=None, price_bonus=None,
                                wind_speed=0, wind_direction="N"):
    """
    Generate a prompt for an LLM to design a rocket.
    
    Args:
        target_apogee (float): Target apogee in meters
        payload_mass (float): Mass of the payload in kg
        stability_margin (float): Target stability margin
        body_diameter (float): Body diameter in mm
        fins_number (int): Number of fins
        material_options (list): List of material options
        wind_speed (float): Wind speed in m/s
        wind_direction (str): Wind direction
        
    Returns:
        str: Prompt for LLM
    """
    # Get the project root directory
    project_root = Path(__file__).resolve().parent.parent.parent
    
    # Load motors from motors.py using their .eng files
    motor_loader = EngFileLoader(base_dir=project_root)
    motors_table = motor_loader.get_motors_table()
    
    # Available materials
    if material_options is None:
        material_options = list(materials.keys())
    
    # Build the prompt
    prompt = f"""# Rocket Design Task

## Design Requirements

- **Target Apogee**: {target_apogee} meters
- **Wind Conditions**: {wind_speed} m/s from {wind_direction} direction
"""

    if payload_mass is not None:
        prompt += f"- **Payload Mass**: {payload_mass} kg\n"
    
    if stability_margin is not None:
        prompt += f"- **Target Stability Margin**: {stability_margin} calibers\n"
        prompt += f"You are given extra points for being below the stability margin if you are within 10% of the target apogee\n"
    
    if price_bonus is not None:
        prompt += f"You are given extra points for how cheap the rocket is to build\n"
    

    prompt += f"""
## Available Materials

The following materials are available for the rocket components:
{', '.join(material_options)}

## Available Motors

{motors_table}

## Design Task

Based on the requirements and available components, design a rocket that will reach the target apogee. Your design should include:

1. Motor selection (choose from the available motors list)
2. Body dimensions and material
3. Nose cone dimensions and material
4. Fin design and material
5. Parachute specifications
6. Launch rail configuration

## Response Format

Please provide your design as a Python dictionary that can be directly used in our simulation software. Use the following format:

```python
config = {{
    "motor_choice": "MOTOR_NAME",  # Choose from available motors
    "rocket_body": {{
        "radius": RADIUS_IN_METERS,  # Body radius in meters
        "length": LENGTH_IN_METERS,  # Body length in meters
        "material": "MATERIAL",  # Choose from available materials
        "thickness": THICKNESS_IN_METERS,  # Wall thickness in meters
    }},
    "aerodynamics": {{
        "nose_cone": {{
            "kind": "SHAPE",  # e.g., vonKarman, conical, elliptical
            "length": LENGTH_IN_METERS,
            "material": "MATERIAL",
        }},
        "fins": {{
            "number": NUMBER_OF_FINS,
            "root_chord": LENGTH_IN_METERS,
            "tip_chord": LENGTH_IN_METERS,
            "span": LENGTH_IN_METERS,
            "cant_angle": ANGLE_IN_DEGREES,
            "material": "MATERIAL",
            "thickness": THICKNESS_IN_METERS,
        }},
        "tail": {{
            "length": LENGTH_IN_METERS,
            "top_radius": RADIUS_IN_METERS,
            "bottom_radius": RADIUS_IN_METERS,
            "material": "MATERIAL",
        }},
    }},
    "parachutes": {{
        "main": {{
            "cd_s": AREA,
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        }},
        "drogue": {{
            "cd_s": AREA,
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        }},
    }},
    "launch": {{
        "rail_length": LENGTH_IN_METERS,
        "inclination": ANGLE_IN_DEGREES,
        "heading": ANGLE_IN_DEGREES,
    }},
    "payload": {{
        "mass": MASS_IN_KG,
        "position": POSITION_IN_METERS,  # relative to rocket center
    }},
}}
```

Before answering you should provide your full reasoning for the design choices you made thinking like a rocket scientist.
"""
    
    return prompt

def main():
    """Main function to generate the prompt from command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate rocket design prompts for LLMs")
    parser.add_argument("--apogee", type=float, required=True, help="Target apogee in meters")
    parser.add_argument("--payload", type=float, help="Payload mass in kg")
    parser.add_argument("--stability", type=float, help="Target stability margin in calibers")
    parser.add_argument("--diameter", type=float, help="Body diameter in mm")
    parser.add_argument("--fins", type=int, help="Number of fins")
    parser.add_argument("--materials", type=str, help="Comma-separated list of materials")
    parser.add_argument("--wind-speed", type=float, default=0, help="Wind speed in m/s")
    parser.add_argument("--wind-direction", type=str, default="N", help="Wind direction (N, S, E, W, etc.)")
    parser.add_argument("--output", type=str, help="Output file for the prompt")
    
    args = parser.parse_args()
    
    # Parse materials if provided
    materials = None
    if args.materials:
        materials = [m.strip() for m in args.materials.split(",")]
    
    # Generate the prompt
    prompt = generate_rocket_design_prompt(
        target_apogee=args.apogee,
        payload_mass=args.payload,
        stability_margin=args.stability,
        body_diameter=args.diameter,
        fins_number=args.fins,
        material_options=materials,
        wind_speed=args.wind_speed,
        wind_direction=args.wind_direction
    )
    
    # Output the prompt
    if args.output:
        with open(args.output, 'w') as f:
            f.write(prompt)
        print(f"Prompt saved to {args.output}")
    else:
        print(prompt)

if __name__ == "__main__":
    main()