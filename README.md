# RocketPy Interface

A high-level abstraction layer for the RocketPy library, making it easier to build and simulate rocket flights.

## Overview

This project provides a simplified interface for building and simulating rockets using the RocketPy library. It abstracts away much of the complexity of the original library while preserving all the functionality.

Key features:
- Simple, fluent interface for rocket configuration
- Pre-built rocket configurations
- Easy environment setup
- Simplified motor configuration
- Component management (nose cones, fins, parachutes, etc.)
- Flight simulation and analysis

## Files

- `rocket_interface.py` - The main interface that abstracts RocketPy functionality
- `rocket_presets.py` - Pre-configured rocket designs for quick setup
- `example_rocket.py` - Example script showing how to use the interface
- `rocket_demo.ipynb` - Jupyter notebook with interactive examples and visualizations

## Installation

1. Ensure you have RocketPy and its dependencies installed:
   ```
   pip install rocketpy
   ```

2. Download the data files needed for the examples:
   ```
   mkdir -p configs
   cd configs
   curl -o NACA0012-radians.txt https://raw.githubusercontent.com/RocketPy-Team/RocketPy/master/data/airfoils/NACA0012-radians.txt
   curl -o Cesaroni_M1670.eng https://raw.githubusercontent.com/RocketPy-Team/RocketPy/master/data/motors/cesaroni/Cesaroni_M1670.eng
   curl -o powerOffDragCurve.csv https://raw.githubusercontent.com/RocketPy-Team/RocketPy/master/data/rockets/calisto/powerOffDragCurve.csv
   curl -o powerOnDragCurve.csv https://raw.githubusercontent.com/RocketPy-Team/RocketPy/master/data/rockets/calisto/powerOnDragCurve.csv
   ```

## Basic Usage

```python
from rocket_interface import RocketInterface, MotorType, WeatherType

# Create a rocket
rocket = RocketInterface(name="MyRocket")

# Set up environment
rocket.setup_environment(weather_type=WeatherType.STANDARD)

# Set up motor (using the default Cesaroni M1670)
rocket.setup_motor()

# Configure rocket parameters
rocket.setup_rocket(
    radius=0.127,  # 127mm
    mass=15.0,     # 15kg without motor
    inertia=(6.0, 6.0, 0.25),
    motor_position=0.2
)

# Add components
rocket.add_nose_cone(length=0.55, kind="vonKarman", position=1.68)
rocket.add_fins(n=4, root_chord=0.120, tip_chord=0.040, span=0.100, position=0.1)
rocket.add_rail_buttons(upper_position=1.2, lower_position=0.2)
rocket.add_parachute(name="Main", cd_s=10.0, trigger="apogee", lag=1.5)

# Simulate flight
rocket.simulate_flight(
    rail_length=5.0,
    inclination=85.0,  # 85 degrees from horizontal
    heading=0.0,       # North
    max_time=300       # 5 minutes
)

# Print flight info
rocket.print_flight_info()

# Plot trajectory
rocket.plot_trajectory()
```

## Using Presets

```python
from rocket_presets import RocketPresets

# Create a preset rocket
calisto = RocketPresets.create_calisto()

# Simulate flight
calisto.simulate_flight(rail_length=5.0, inclination=85.0, heading=0.0)

# Compare multiple rockets
results = RocketPresets.simulate_and_compare_all()
print(results)
```

## Advanced Usage

For more advanced usage, including customizing preset rockets and analyzing flight data, see the `rocket_demo.ipynb` Jupyter notebook.

## License

This project is released under the MIT License.

## Acknowledgments

This project is built on top of the excellent [RocketPy](https://github.com/RocketPy-Team/RocketPy) library developed by the RocketPy Team. # LLMRocketFlightSim
