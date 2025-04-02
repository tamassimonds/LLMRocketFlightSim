"""
Utility functions for rocket physics calculations.
"""
import math
from rocket_package.src.models.materials import materials

def compute_rocket_body_mass(body_config):
    """
    Compute the mass of a cylindrical rocket body.
    
    Args:
        body_config (dict): Rocket body configuration.
        
    Returns:
        float: Mass of the rocket body in kg.
    """
    r = body_config["radius"]
    t = body_config["thickness"]
    L = body_config["length"]
    density = materials[body_config["material"]]["density"]
    volume = math.pi * L * (r**2 - (r - t)**2)
    return volume * density

def compute_nose_cone_mass(nose_config, body_radius):
    """
    Compute the mass of a nose cone.
    
    Args:
        nose_config (dict): Nose cone configuration.
        body_radius (float): Radius of the rocket body.
        
    Returns:
        float: Mass of the nose cone in kg.
    """
    r = body_radius
    L = nose_config["length"]
    density = materials[nose_config["material"]]["density"]
    volume = (1/3) * math.pi * r**2 * L
    return volume * density

def compute_fins_mass(fins_config):
    """
    Compute the mass of rocket fins.
    
    Args:
        fins_config (dict): Fins configuration.
        
    Returns:
        float: Mass of all fins in kg.
    """
    num = fins_config["number"]
    root = fins_config["root_chord"]
    tip = fins_config["tip_chord"]
    span = fins_config["span"]
    thickness = fins_config.get("thickness", 0.005)
    density = materials[fins_config["material"]]["density"]
    area = (root + tip) / 2 * span
    volume = area * thickness
    return num * volume * density

def compute_tail_mass(tail_config, default_thickness):
    """
    Compute the mass of a rocket tail.
    
    Args:
        tail_config (dict): Tail configuration.
        default_thickness (float): Default thickness if not specified.
        
    Returns:
        float: Mass of the tail in kg.
    """
    R_avg = (tail_config["top_radius"] + tail_config["bottom_radius"]) / 2
    t = default_thickness
    L = tail_config["length"]
    density = materials[tail_config["material"]]["density"]
    volume = math.pi * L * (R_avg**2 - (R_avg - t)**2)
    return volume * density

def compute_inertia(total_mass, cfg):
    """
    Compute the inertia tensor of the rocket.
    
    Args:
        total_mass (float): Total mass of the rocket in kg.
        cfg (dict): Rocket configuration.
        
    Returns:
        tuple: Inertia tensor (Ixx, Iyy, Izz).
    """
    L_body = cfg["rocket_body"]["length"]
    L_nose = cfg["aerodynamics"]["nose_cone"]["length"]
    L_tail = cfg["aerodynamics"]["tail"]["length"]
    L_total = L_body + L_nose + L_tail
    r = cfg["rocket_body"]["radius"]
    I_trans = (1/12) * total_mass * L_total**2
    I_long = 0.5 * total_mass * r**2
    return (I_trans, I_trans, I_long)

def calculate_component_positions(config):
    """
    Calculate positions of rocket components.
    
    Args:
        config (dict): Rocket configuration.
        
    Returns:
        dict: Component positions.
    """
    body_length = config["rocket_body"]["length"]
    nose_length = config["aerodynamics"]["nose_cone"]["length"]
    tail_length = config["aerodynamics"]["tail"]["length"]

    positions = {
        "nose": body_length / 2 + nose_length / 2,      # forward of center
        "fins": -body_length / 2 + 0.2,                # near the aft section
        "tail": -body_length / 2 - tail_length / 2,    # at the extreme tail
    }
    
    return positions

def calculate_center_of_mass(config, component_masses, component_positions, motor_mass, motor_position):
    """
    Calculate the center of mass of the entire rocket.
    
    Args:
        config (dict): Rocket configuration.
        component_masses (dict): Masses of rocket components.
        component_positions (dict): Positions of rocket components.
        motor_mass (float): Mass of the motor.
        motor_position (float): Position of the motor.
        
    Returns:
        float: Center of mass position.
    """
    # Extract masses
    body_mass = component_masses["body"]
    nose_mass = component_masses["nose"]
    fins_mass = component_masses["fins"]
    tail_mass = component_masses["tail"]
    payload_mass = config.get("payload", {}).get("mass", 0)
    payload_position = config.get("payload", {}).get("position", 0)
    
    # Calculate structure mass (without motor)
    structure_mass = body_mass + nose_mass + fins_mass + tail_mass + payload_mass
    
    # Calculate structure center of mass
    # Assume rocket body mass is uniformly distributed and centered at 0
    structure_com = (body_mass * 0 +
                    nose_mass * component_positions["nose"] +
                    fins_mass * component_positions["fins"] +
                    tail_mass * component_positions["tail"] +
                    payload_mass * payload_position) / structure_mass
    
    # Calculate overall center of mass including motor
    total_mass = structure_mass + motor_mass
    overall_com = (structure_mass * structure_com + motor_mass * motor_position) / total_mass
    
    return {
        "structure_mass": structure_mass,
        "structure_com": structure_com,
        "total_mass": total_mass,
        "overall_com": overall_com
    }

def calculate_motor_position(config, motor, component_positions):
    """
    Calculate the appropriate motor position at the back of the rocket.
    
    Args:
        config (dict): Rocket configuration.
        motor: SolidMotor object.
        component_positions (dict): Positions of rocket components.
        
    Returns:
        float: Calculated motor position.
    """
    # Get tail position (back of the rocket)
    tail_position = component_positions["tail"]
    
    # Calculate motor length
    motor_length = motor.grain_initial_height * motor.grain_number + 0.1  # Add extra for nozzle
    
    # Position the motor at the back - exactly at the tail
    motor_position = tail_position  # For RocketPy coordinate system
    
    return motor_position, motor_length 