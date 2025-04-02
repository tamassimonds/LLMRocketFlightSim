from pathlib import Path

motors = {
    "Pro75M1670": {
        "thrust_source": str(Path(__file__).resolve().parent.parent.parent.parent / "configs" / "Cesaroni_M1670.eng"),
        "dry_mass": 1.815,
        "dry_inertia": (0.125, 0.125, 0.002),
        "nozzle_radius": 33 / 1000,
        "grain_number": 5,
        "grain_density": 1815,
        "grain_outer_radius": 33 / 1000,
        "grain_initial_inner_radius": 15 / 1000,
        "grain_initial_height": 120 / 1000,
        "grain_separation": 5 / 1000,
        "grains_center_of_mass_position": 0.397,
        "center_of_dry_mass_position": 0.317,
        "nozzle_position": 0,
        "burn_time": 3.9,
        "throat_radius": 11 / 1000,
        "coordinate_system_orientation": "nozzle_to_combustion_chamber",
        "cost": 520.00,  # Cost in USD
    },
    "AeroTechK700W": {
        "thrust_source": str(Path(__file__).resolve().parent.parent.parent.parent / "configs" / "AeroTech_K700W.eng"),
        "dry_mass": 0.732,
        "dry_inertia": (0.015, 0.015, 0.002),
        "nozzle_radius": 27 / 1000,
        "grain_number": 1,
        "grain_density": 1750,
        "grain_outer_radius": 25 / 1000,
        "grain_initial_inner_radius": 10 / 1000,
        "grain_initial_height": 450 / 1000,
        "grain_separation": 0,
        "grains_center_of_mass_position": 0.28,
        "center_of_dry_mass_position": 0.25,
        "nozzle_position": 0,
        "burn_time": 3.5,
        "throat_radius": 12 / 1000,
        "coordinate_system_orientation": "nozzle_to_combustion_chamber",
        "cost": 180.00,  # Cost in USD
    },
    "CesaroniM1670": {
        "thrust_source": str(Path(__file__).resolve().parent.parent.parent.parent / "configs" / "Cesaroni_6026M1670-P.eng"),
        "dry_mass": 3.101,
        "dry_inertia": (0.025, 0.025, 0.002),
        "nozzle_radius": 37.5 / 1000,
        "grain_number": 1,
        "grain_density": 1750,
        "grain_outer_radius": 35 / 1000,
        "grain_initial_inner_radius": 15 / 1000,
        "grain_initial_height": 650 / 1000,
        "grain_separation": 0,
        "grains_center_of_mass_position": 0.35,
        "center_of_dry_mass_position": 0.32,
        "nozzle_position": -0.1,
        "burn_time": 3.6,
        "throat_radius": 15 / 1000,
        "coordinate_system_orientation": "nozzle_to_combustion_chamber",
        "cost": 550.00,  # Cost in USD
    },
    "AeroTechH128W": {
        "thrust_source": str(Path(__file__).resolve().parent.parent.parent.parent / "configs" / "AeroTech_H128W.eng"),
        "dry_mass": 0.108,
        "dry_inertia": (0.005, 0.005, 0.001),
        "nozzle_radius": 14.5 / 1000,
        "grain_number": 1,
        "grain_density": 1750,
        "grain_outer_radius": 14 / 1000,
        "grain_initial_inner_radius": 6 / 1000,
        "grain_initial_height": 120 / 1000,
        "grain_separation": 0,
        "grains_center_of_mass_position": 0.12,
        "center_of_dry_mass_position": 0.10,
        "nozzle_position": 0,
        "burn_time": 1.29,
        "throat_radius": 5 / 1000,
        "coordinate_system_orientation": "nozzle_to_combustion_chamber",
        "cost": 65.00,  # Cost in USD
    },
    "CesaroniO3700": {
        "thrust_source": str(Path(__file__).resolve().parent.parent.parent.parent / "configs" / "Cesaroni_29920O3700-P.eng"),
        "dry_mass": (31.351 - 17.157),  # Total weight - Propellant weight in kg
        "dry_inertia": (0.8, 0.8, 0.05),  # Estimated based on size/mass
        "nozzle_radius": 161/2000,  # Diameter/2 in meters
        "grain_number": 4,  # Estimated based on size
        "grain_density": 1815,  # Standard Cesaroni grain density
        "grain_outer_radius": 155/2000,  # Slightly less than case diameter
        "grain_initial_inner_radius": 60/2000,  # Estimated for thrust level
        "grain_initial_height": 220/1000,  # Total length divided by grains
        "grain_separation": 10/1000,  # Standard separation
        "grains_center_of_mass_position": 0.55,  # Estimated based on length
        "center_of_dry_mass_position": 0.48,  # Estimated based on length
        "nozzle_position": 0,
        "burn_time": 8.2,  # From specifications
        "throat_radius": 40/1000,  # Estimated for thrust level
        "coordinate_system_orientation": "nozzle_to_combustion_chamber",
        "cost": 1250.00,  # Cost in USD
    },
    "CesaroniO5800": {
        "thrust_source": str(Path(__file__).resolve().parent.parent.parent.parent / "configs" / "Cesaroni_30600O5800-P.eng"),
        "dry_mass": (26.368 - 13.950),  # Total weight - Propellant weight in kg
        "dry_inertia": (0.6, 0.6, 0.04),  # Estimated based on size/mass
        "nozzle_radius": 161/2000,  # Diameter/2 in meters
        "grain_number": 3,  # Estimated based on size and burn time
        "grain_density": 1815,  # Standard Cesaroni grain density
        "grain_outer_radius": 155/2000,  # Slightly less than case diameter
        "grain_initial_inner_radius": 65/2000,  # Estimated for higher thrust level
        "grain_initial_height": 230/1000,  # Total length divided by grains
        "grain_separation": 10/1000,  # Standard separation
        "grains_center_of_mass_position": 0.45,  # Estimated based on length
        "center_of_dry_mass_position": 0.38,  # Estimated based on length
        "nozzle_position": 0,
        "burn_time": 5.2,  # From specifications
        "throat_radius": 45/1000,  # Estimated for higher thrust level
        "coordinate_system_orientation": "nozzle_to_combustion_chamber",
        "cost": 1100.00,  # Cost in USD
    },
    "CesaroniK160": {
        "thrust_source": str(Path(__file__).resolve().parent.parent.parent.parent / "configs" / "Cesaroni_1526K160-6.eng"),
        "dry_mass": (1.472 - 0.772),  # Total weight - Propellant weight in kg
        "dry_inertia": (0.012, 0.012, 0.001),  # Estimated based on size/mass
        "nozzle_radius": 54/2000,  # Diameter/2 in meters
        "grain_number": 4,  # Estimated based on size and long burn time
        "grain_density": 1815,  # Standard Cesaroni grain density
        "grain_outer_radius": 52/2000,  # Slightly less than case diameter
        "grain_initial_inner_radius": 20/2000,  # Estimated for thrust level
        "grain_initial_height": 90/1000,  # Total length divided by grains
        "grain_separation": 5/1000,  # Standard separation for smaller motor
        "grains_center_of_mass_position": 0.25,  # Estimated based on length
        "center_of_dry_mass_position": 0.20,  # Estimated based on length
        "nozzle_position": 0,
        "burn_time": 9.7,  # From specifications
        "throat_radius": 12/1000,  # Estimated for thrust level
        "coordinate_system_orientation": "nozzle_to_combustion_chamber",
        "cost": 130.00,  # Cost in USD
    },
}