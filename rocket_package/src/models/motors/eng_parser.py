"""
Parse RockSim .eng files for rocket motor specifications based on motors.py definitions.
"""

import numpy as np
from pathlib import Path
import tabulate
from.src.models.motors.motors import motors as motor_configs

def parse_eng_file(file_path):
    """
    Parse a RockSim .eng file and extract key motor specifications.
    
    Args:
        file_path (str): Path to the .eng file
        
    Returns:
        dict: Motor specifications
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Skip comment lines (starting with ';')
        header_index = -1
        header = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.startswith(';'):
                header = line.split()
                header_index = i
                break
        
        if header_index == -1 or not header:
            raise ValueError(f"No valid header found in {file_path}")
        
        # Parse header information
        if len(header) >= 7:
            designation = header[0]
            diameter_mm = float(header[1])
            length_mm = float(header[2])
            propellant_weight_kg = float(header[4])
            total_weight_kg = float(header[5])
            manufacturer = header[6]
        else:
            raise ValueError(f"Invalid header format in {file_path}")
        
        # Parse thrust curve
        thrust_data = []
        for line in lines[header_index + 1:]:
            line = line.strip()
            if line and not line.startswith(';'):
                try:
                    time, thrust = map(float, line.split())
                    thrust_data.append((time, thrust))
                except ValueError:
                    continue
        
        if not thrust_data:
            raise ValueError(f"No thrust data found in {file_path}")
        
        # Calculate motor specifications
        thrust_data = np.array(thrust_data)
        times = thrust_data[:, 0]
        thrusts = thrust_data[:, 1]
        
        burn_time = times[-1]  # Last time point with non-zero thrust
        max_thrust = np.max(thrusts)
        
        # Calculate average thrust
        avg_thrust = np.mean(thrusts[thrusts > 0])
        
        # Calculate total impulse - integrate thrust over time
        total_impulse = 0
        for i in range(1, len(times)):
            dt = times[i] - times[i-1]
            avg_thrust_interval = (thrusts[i] + thrusts[i-1]) / 2
            total_impulse += avg_thrust_interval * dt
        
        # Calculate specific impulse (Isp)
        if propellant_weight_kg > 0:
            # Convert to Ns/kg, then divide by g (9.81) to get Isp in seconds
            isp = total_impulse / (propellant_weight_kg * 9.81)
        else:
            isp = 0
        
        dry_mass = total_weight_kg - propellant_weight_kg
        
        motor_specs = {
            "name": Path(file_path).stem,
            "designation": designation,
            "manufacturer": manufacturer,
            "diameter_mm": diameter_mm,
            "length_mm": length_mm,
            "propellant_weight_kg": propellant_weight_kg,
            "total_weight_kg": total_weight_kg,
            "dry_mass_kg": dry_mass,
            "max_thrust_N": max_thrust,
            "avg_thrust_N": avg_thrust,
            "burn_time_s": burn_time,
            "total_impulse_Ns": total_impulse,
            "isp_s": isp
        }
        
        return motor_specs
    except Exception as e:
        print(f"Error parsing {file_path}: {str(e)}")
        return None

class EngFileLoader:
    """Load motor data from the motors defined in motors.py and their associated .eng files."""
    
    def __init__(self, base_dir=""):
        """
        Initialize the motor loader.
        
        Args:
            base_dir (str): Base directory for resolving relative paths
        """
        self.base_dir = Path(base_dir)
        self.motors = self._load_motors_from_config()
    
    def _load_motors_from_config(self):
        """
        Load motors defined in motors.py and their associated .eng files.
        
        Returns:
            list: List of motor specifications combining config and .eng data
        """
        motors = []
        
        for motor_name, config in motor_configs.items():
            # Get the thrust source from config
            thrust_source = config.get("thrust_source", "")
            if not thrust_source:
                print(f"Warning: No thrust source defined for {motor_name}")
                continue
            
            # Resolve the file path
            eng_file_path = self.base_dir / thrust_source
            
            # Parse the .eng file
            eng_data = parse_eng_file(eng_file_path)
            if not eng_data:
                print(f"Warning: Could not parse .eng file for {motor_name}")
                continue
            
            # Combine data from config and .eng file
            motor_data = {
                "name": motor_name,
                "eng_file": Path(thrust_source).stem,
                "manufacturer": eng_data["manufacturer"],
                "diameter_mm": eng_data["diameter_mm"],
                "length_mm": eng_data["length_mm"],
                "propellant_weight_kg": eng_data["propellant_weight_kg"],
                "total_weight_kg": eng_data["total_weight_kg"],
                "dry_mass_kg": config.get("dry_mass", eng_data["dry_mass_kg"]),
                "max_thrust_N": eng_data["max_thrust_N"],
                "avg_thrust_N": eng_data["avg_thrust_N"],
                "burn_time_s": config.get("burn_time", eng_data["burn_time_s"]),
                "total_impulse_Ns": eng_data["total_impulse_Ns"],
                "isp_s": eng_data["isp_s"],
                "nozzle_radius": config.get("nozzle_radius", 0) * 1000,  # Convert to mm
                "throat_radius": config.get("throat_radius", 0) * 1000,  # Convert to mm
                "grain_number": config.get("grain_number", 1),
            }
            
            motors.append(motor_data)
        
        return motors
    
    def get_motors_table(self):
        """
        Generate a formatted table of all motors.
        
        Returns:
            str: Markdown table of motors
        """
        if not self.motors:
            return "No motors found."
        
        # Define table headers
        headers = ["Name", "Manufacturer", "Diameter (mm)", "Length (mm)", 
                  "Dry Mass (kg)", "Max Thrust (N)", "Avg Thrust (N)", 
                  "Burn Time (s)", "Total Impulse (Ns)", "Isp (s)"]
        
        # Prepare table rows
        rows = []
        for motor in self.motors:
            row = [
                motor["name"],
                motor["manufacturer"],
                f"{motor['diameter_mm']:.1f}",
                f"{motor['length_mm']:.1f}",
                f"{motor['dry_mass_kg']:.3f}",
                f"{motor['max_thrust_N']:.1f}",
                f"{motor['avg_thrust_N']:.1f}",
                f"{motor['burn_time_s']:.2f}",
                f"{motor['total_impulse_Ns']:.1f}",
                f"{motor['isp_s']:.1f}"
            ]
            rows.append(row)
        
        # Generate markdown table
        return tabulate.tabulate(rows, headers=headers, tablefmt="pipe")
        
    def get_motor_data(self, motor_name):
        """
        Get detailed data for a specific motor.
        
        Args:
            motor_name (str): Name of the motor
            
        Returns:
            dict: Motor data or None if not found
        """
        for motor in self.motors:
            if motor["name"] == motor_name:
                return motor
        return None 