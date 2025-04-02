"""
Default configurations for rocket simulations.
"""

# Standard high-altitude configuration
standard_config = {
    "goal_altitude": 10000,  # [m] desired altitude
    "motor_choice": "CesaroniM1670",  # Which motor to use from the motors dict
    "rocket_body": {
        "radius": 166 / 2000,  # [m]
        "length": 3,         # [m] cylindrical section
        "material": "fiberglass",  # material key
        "thickness": 0.005,  # [m] wall thickness
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "vonKarman",
            "length": 0.55829,  # [m]
            "material": "fiberglass",  # material key
        },
        "fins": {
            "number": 4,
            "root_chord": 0.520,  # [m]
            "tip_chord": 0.060,   # [m]
            "span": 0.210,        # [m]
            "cant_angle": 0.5,    # [degrees]
            "material": "fiberglass",  # material key
            "thickness": 0.005,   # [m] fin thickness
        },
        "tail": {
            "length": 0.060,     # [m]
            "top_radius": 0.0635,  # [m]
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
        "inclination": 90,   # [degrees]
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

# Optimized 3km configuration
o3_config = {
    "goal_altitude": 3000,  # target altitude: 3 km
    "motor_choice": "AeroTechK700W",  # lightweight motor for the flight profile
    "rocket_body": {
        # Using a scaling factor of 0.56 for structural elements
        "radius": (166 / 2000) * 0.56,  # ~0.0465 m
        "length": 3 * 0.56,             # 1.68 m
        "material": "fiberglass",
        "thickness": 0.005 * 0.56,      # ~0.0028 m wall thickness
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "vonKarman",
            "length": 0.55829 * 0.56,  # ~0.3126 m
            "material": "fiberglass",
        },
        "fins": {
            "number": 4,
            "root_chord": 0.520 * 0.56,  # ~0.2912 m
            "tip_chord": 0.060 * 0.56,   # ~0.0336 m
            "span": 0.210 * 0.56,        # ~0.1176 m
            "cant_angle": 0.0,           # 0° to minimize lateral forces
            "material": "fiberglass",
            "thickness": 0.005 * 0.56,   # ~0.0028 m
        },
        "tail": {
            "length": 0.060 * 0.56,         # ~0.0336 m
            "top_radius": 0.0635 * 0.56,      # ~0.0356 m
            "bottom_radius": 0.0435 * 0.56,   # ~0.0244 m
            "material": "fiberglass",
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
        "rail_length": 40,  # increased rail length to maintain a vertical trajectory longer
        "inclination": 90,
        "heading": 0,
    },
    "payload": {
        "mass": 5.0,
        "position": 0.5,  # shifting payload further forward for better stability
    },
    "env": {
        "wind_u": 0,  # m/s
        "wind_v": 0,  # m/s
    },
} 