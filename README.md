# LLM Rocket Flight Simulator

A Python package for rocket flight simulation, design optimization, and benchmarking using Large Language Models (LLMs).

## Overview

This project combines rocket flight simulation with LLM-powered design optimization to create an intelligent rocket design system. It allows you to:

1. **Simulate rocket flights** with realistic physics using RocketPy
2. **Optimize rocket designs** using LLMs to target specific performance goals
3. **Benchmark LLM performance** in rocket design tasks
4. **Evaluate landing precision** with dynamic reward functions

The project contains tooling to benchmark models on metrics used in paper aswell as the simulation tools you need to create your own benchmarks

## Features

- **Realistic Flight Simulation**: Physics-based simulation using RocketPy
- **LLM Integration**: Seamless integration with various LLM models (GPT-4, Claude, etc.)
- **Iterative Design Optimization**: LLMs improve designs based on simulation results
- **Dynamic Reward Functions**: Sophisticated scoring for landing precision
- **Batch Processing**: Run multiple simulations in parallel
- **Comprehensive Output**: Detailed reports, plots, and data for analysis
- **Wind Effects**: Account for wind conditions in flight simulation


# Benchmarking

### Apogee Targeting Benchmark

Run a benchmark to optimize rocket designs for reaching a specific apogee:

```bash
python benchmark.py --prompt prompt.txt --model claude-3-7-sonnet-20250219 --apogee 3048 --iterations 5 --wind-speed 5 --wind-direction E --output-dir benchmarks
```

### Target Landing Benchmark

Run a benchmark to optimize rocket designs for precise landing at specific coordinates:

```bash
python benchmark.py --prompt prompt-target.txt --model o1-mini --target-x 4000 --target-y 4000 --iterations 1 --batch-size 5 --wind-speed 5 --wind-direction E --output-dir target-benchmarks
```

### Command Line Arguments

- `--prompt`: Path to prompt file or raw prompt text
- `--model`: LLM model to use (e.g., "gpt-4", "claude-3-opus", "o1-mini")
- `--apogee`: Target apogee in meters (for apogee targeting mode)
- `--target-x`: X-coordinate for bullseye landing target
- `--target-y`: Y-coordinate for bullseye landing target
- `--iterations`: Maximum number of improvement iterations
- `--batch-size`: Number of simulations to run per iteration
- `--wind-speed`: Wind speed in m/s
- `--wind-direction`: Wind direction (N, S, E, W)
- `--output-dir`: Base directory for outputs
- `--save-plots`: Save simulation plots

## Reward Functions

The system includes several reward functions for evaluating rocket performance:

1. **Apogee Targeting**: Evaluates how close the rocket gets to the target apogee
2. **Bullseye Landing**: Evaluates landing precision at specific coordinates
3. **Complex Bullseye**: Combines landing precision with other factors like cost and structural integrity


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

### Basic Simulation

```python
from rocket_package.rocket_interface import simulate_from_config

# Define your rocket configuration
config = {
    "motor_choice": "Pro75M1670",
    "rocket_body": {
        "radius": 0.1,
        "length": 3.0,
        "material": "carbon_fiber",
        "thickness": 0.002,
    },
    # ... other configuration details ...
}

# Run simulation
result = simulate_from_config(
    config=config,
    target_apogee=3000,
    wind_speed=5,
    wind_direction="E",
    save_outputs=True
)

# Print summary
print_result_summary(result)
```

## Project Structure

```
LLMRocketFlightSim/
├── rocket_package/       # Core rocket simulation package
│   ├── src/              # Source code
│   │   ├── models/       # Rocket and simulation models
│   │   └── utils/        # Utility functions
│   ├── rocket_interface.py  # Main interface
│   └── calculate_reward.py  # Reward calculation
├── utils/                # Utility functions
│   └── inference.py      # LLM inference
├── main.py               # Main simulation script
├── benchmark.py          # Benchmarking script
├── prompt.txt            # Prompt for apogee targeting
└── prompt-target.txt     # Prompt for bullseye landing
```

## Dependencies

- rocketpy
- numpy
- matplotlib
- pandas
- tabulate
- asyncio

## License

MIT License