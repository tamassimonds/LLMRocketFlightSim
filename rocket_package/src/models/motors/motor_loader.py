"""
Motor configuration loader and management.
"""
import os
import json
from pathlib import Path
from rocket_package.src.models.motors.motors import motors
import numpy as np

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

    for motor_name, motor_config in motors.items():
        thrust_file = motor_config["thrust_source"]
        os.makedirs(os.path.dirname(thrust_file), exist_ok=True)
        
        # Check if the thrust file exists
        if not os.path.exists(thrust_file):
            # Create a default thrust curve
            create_default_thrust_curve(
                filename=thrust_file,
                motor_name=motor_name,
                burn_time=motor_config["burn_time"],
                thrust_avg=None,  # We'll estimate based on the motor configuration
                thrust_initial=None,
                thrust_max=None
            )

def create_default_thrust_curve(filename, motor_name, burn_time, thrust_avg=None, thrust_initial=None, thrust_max=None):
    """
    Create a default thrust curve file for a motor.
    
    Args:
        filename (str): Path to the thrust curve file.
        motor_name (str): Name of the motor.
        burn_time (float): Burn time in seconds.
        thrust_avg (float, optional): Average thrust in N.
        thrust_initial (float, optional): Initial thrust in N.
        thrust_max (float, optional): Maximum thrust in N.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # If no thrust values are provided, estimate them based on motor properties
    if thrust_avg is None:
        # Estimate thrust based on motor grain
        motor_config = motors[motor_name]
        grain_radius = motor_config["grain_outer_radius"]
        grain_inner_radius = motor_config["grain_initial_inner_radius"]
        grain_height = motor_config["grain_initial_height"]
        grain_number = motor_config["grain_number"]
        
        # Estimate propellant volume
        propellant_volume = np.pi * grain_number * grain_height * (grain_radius**2 - grain_inner_radius**2)
        
        # Estimate propellant mass
        propellant_mass = propellant_volume * motor_config["grain_density"]
        
        # Estimate total impulse (rough estimate)
        total_impulse = propellant_mass * 200  # Assuming 200 Ns/kg specific impulse
        
        # Estimate average thrust
        thrust_avg = total_impulse / burn_time
    
    # If initial and max thrust are not provided, estimate them
    if thrust_initial is None:
        thrust_initial = thrust_avg * 0.8  # 80% of average thrust
    
    if thrust_max is None:
        thrust_max = thrust_avg * 1.2  # 120% of average thrust
    
    # Generate time points
    t_points = np.linspace(0, burn_time, 100)
    
    # Generate a thrust curve
    # We'll use a simple model: ramp up, plateau, ramp down
    thrust = np.zeros_like(t_points)
    ramp_up_time = burn_time * 0.1
    plateau_time = burn_time * 0.8
    
    for i, t in enumerate(t_points):
        if t < ramp_up_time:
            # Ramp up from initial to max thrust
            thrust[i] = thrust_initial + (thrust_max - thrust_initial) * (t / ramp_up_time)
        elif t < ramp_up_time + plateau_time:
            # Plateau at max thrust
            thrust[i] = thrust_max
        else:
            # Ramp down to zero
            ramp_down_progress = (t - ramp_up_time - plateau_time) / (burn_time - ramp_up_time - plateau_time)
            thrust[i] = thrust_max * (1 - ramp_down_progress)
    
    # Write the thrust curve to file
    with open(filename, 'w') as f:
        f.write(f"; {motor_name} thrust curve\n")
        f.write(f"; Auto-generated thrust curve for testing\n")
        f.write(f"; Burn time: {burn_time} s\n")
        f.write(f"; Average thrust: {thrust_avg:.1f} N\n")
        f.write(f"; Initial thrust: {thrust_initial:.1f} N\n")
        f.write(f"; Maximum thrust: {thrust_max:.1f} N\n")
        f.write(f"; Total impulse: {thrust_avg * burn_time:.1f} Ns\n\n")
        
        for t, f in zip(t_points, thrust):
            f.write(f"{t:.6f} {f:.6f}\n")
    
    print(f"Created default thrust curve for {motor_name} at {filename}")
    
    return filename

# Uncomment to save predefined motors when importing this module
# _save_predefined_motors() 