"""
Material properties for rocket components.
"""

# Materials dictionary with mechanical properties
materials = {
    "aluminum": {
        "density": 2700,           # kg/m³
        "yield_strength": 95e6,    # Pa
        "ultimate_strength": 150e6, # Pa
        "cost": 5                  # $5 per kg
    },
    "composite": {
        "density": 1600,           # kg/m³
        "yield_strength": 120e6,
        "ultimate_strength": 200e6,
        "cost": 20                 # $20 per kg
    },
    "fiberglass": {
        "density": 1850,           # kg/m³
        "yield_strength": 200e6,   # Pa
        "ultimate_strength": 345e6,# Pa
        "cost": 15                 # $15 per kg
    },
    "carbon_fiber": {
        "density": 1550,           # kg/m³
        "yield_strength": 500e6,
        "ultimate_strength": 600e6,
        "cost": 50                 # $50 per kg
    },
    "balsa_wood": {
        "density": 160,            # kg/m³
        "yield_strength": 3e6,
        "ultimate_strength": 5e6,
        "cost": 2                 # $2 per kg
    },
    "plywood": {
        "density": 700,            # kg/m³
        "yield_strength": 30e6,
        "ultimate_strength": 40e6,
        "cost": 1.5               # $1.50 per kg
    },
    "ABS_plastic": {
        "density": 1050,           # kg/m³
        "yield_strength": 40e6,
        "ultimate_strength": 50e6,
        "cost": 4                 # $4 per kg
    },
} 