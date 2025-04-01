"""
Motor configuration loader and management.
"""
import os
import json
from pathlib import Path
from src.models.motors.motors import motors

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