"""
Motor configuration loader and management.
"""
import os
import json
from pathlib import Path

class MotorLoader:
    """Load and manage motor configurations."""
    
    def __init__(self, motors_dir=None):
        """
        Initialize the motor loader.
        
        Args:
            motors_dir (str, optional): Directory containing motor JSON configurations.
                                       Defaults to "motors".
        """
        if motors_dir is None:
            # Default to 'motors' directory in the same directory as this file
            self.motors_dir = Path(__file__).parent
        else:
            self.motors_dir = Path(motors_dir)
        
        # Load all motor configurations
        self.motors = self._load_all_motors()
    
    def _load_all_motors(self):
        """Load all motor configurations from JSON files."""
        motors = {}
        json_files = list(self.motors_dir.glob("*.json"))
        
        # If no JSON files yet, return an empty dict
        if not json_files:
            return motors
            
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    motor_config = json.load(f)
                    motor_name = file_path.stem  # Get filename without extension
                    motors[motor_name] = motor_config
            except Exception as e:
                print(f"Error loading motor configuration from {file_path}: {e}")
        
        return motors
    
    def get_motor_config(self, motor_name):
        """
        Get configuration for a specific motor.
        
        Args:
            motor_name (str): Name of the motor.
            
        Returns:
            dict: Motor configuration.
            
        Raises:
            KeyError: If motor_name is not found.
        """
        if motor_name not in self.motors:
            raise KeyError(f"Motor '{motor_name}' not found.")
        return self.motors[motor_name]
    
    def save_motor_config(self, motor_name, config):
        """
        Save a motor configuration to a JSON file.
        
        Args:
            motor_name (str): Name of the motor.
            config (dict): Motor configuration.
        """
        # Ensure motors directory exists
        os.makedirs(self.motors_dir, exist_ok=True)
        
        file_path = self.motors_dir / f"{motor_name}.json"
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Update the in-memory dictionary
        self.motors[motor_name] = config
        
        print(f"Motor configuration saved to {file_path}")
    
    def list_available_motors(self):
        """
        List names of all available motors.
        
        Returns:
            list: List of motor names.
        """
        return list(self.motors.keys())


# Export predefined motor configurations
motors = {
    "Pro75M1670": {
        "thrust_source": "configs/Cesaroni_M1670.eng",
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
    },
    "AeroTechK700W": {
        "thrust_source": "configs/AeroTech_K700W.eng",
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
    },
    "CesaroniM1670": {
        "thrust_source": "configs/Cesaroni_6026M1670-P.eng",
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
    },
}

# Save predefined motors to JSON files when this module is imported
def _save_predefined_motors():
    loader = MotorLoader()
    for motor_name, config in motors.items():
        # Handle tuple serialization issue by converting tuples to lists
        config_copy = config.copy()
        for key, value in config_copy.items():
            if isinstance(value, tuple):
                config_copy[key] = list(value)
        loader.save_motor_config(motor_name, config_copy)
    
    print(f"Saved {len(motors)} predefined motor configurations.")

# Uncomment to save predefined motors when importing this module
# _save_predefined_motors() 