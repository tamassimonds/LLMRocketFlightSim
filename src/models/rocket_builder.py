"""
Rocket builder class for creating rocket models from configurations.
"""
from rocketpy import Rocket, SolidMotor
from src.utils.rocket_physics import (
    compute_rocket_body_mass,
    compute_nose_cone_mass,
    compute_fins_mass,
    compute_tail_mass,
    compute_inertia,
    calculate_component_positions,
    calculate_center_of_mass,
    calculate_motor_position
)
from src.models.motors.motor_loader import motors

class RocketBuilder:
    """Builder class for creating RocketPy rocket models from configurations."""
    
    def __init__(self, config, motor_configs=None):
        """
        Initialize the rocket builder.
        
        Args:
            config (dict): Rocket configuration.
            motor_configs (dict, optional): Motor configurations. Defaults to predefined motors.
        """
        self.config = config
        self.motor_configs = motor_configs if motor_configs is not None else motors
        self.component_masses = {}
        self.component_positions = None
        self.motor = None
        self.rocket = None
        self.mass_data = None
    
    def build(self):
        """
        Build a rocket model from configuration.
        
        Returns:
            Rocket: RocketPy Rocket object.
        """
        self._calculate_masses()
        self.component_positions = calculate_component_positions(self.config)
        self._setup_motor()
        self._build_rocket()
        self._add_components()
        
        return self.rocket, self.component_masses, self.mass_data
    
    def _calculate_masses(self):
        """Calculate masses of all rocket components."""
        body_mass = compute_rocket_body_mass(self.config["rocket_body"])
        nose_mass = compute_nose_cone_mass(
            self.config["aerodynamics"]["nose_cone"], 
            self.config["rocket_body"]["radius"]
        )
        fins_mass = compute_fins_mass(self.config["aerodynamics"]["fins"])
        tail_mass = compute_tail_mass(
            self.config["aerodynamics"]["tail"], 
            self.config["rocket_body"]["thickness"]
        )
        
        self.component_masses = {
            "body": body_mass,
            "nose": nose_mass,
            "fins": fins_mass,
            "tail": tail_mass
        }
    
    def _setup_motor(self):
        """Set up the rocket motor."""
        motor_choice = self.config["motor_choice"]
        
        if motor_choice not in self.motor_configs:
            raise ValueError(f"Motor '{motor_choice}' not found in motor configurations.")
        
        motor_config = self.motor_configs[motor_choice]
        self.motor = SolidMotor(**motor_config)
        
        # Calculate motor position at the back of the rocket
        motor_position, motor_length = calculate_motor_position(
            self.config, 
            self.motor, 
            self.component_positions
        )
        
        # Calculate center of mass
        self.mass_data = calculate_center_of_mass(
            self.config,
            self.component_masses,
            self.component_positions,
            self.motor_configs[motor_choice]["dry_mass"],
            motor_position
        )
    
    def _build_rocket(self):
        """Build the basic rocket model."""
        self.rocket = Rocket(
            radius=self.config["rocket_body"]["radius"],
            mass=self.mass_data["total_mass"],
            inertia=compute_inertia(self.mass_data["total_mass"], self.config),
            power_off_drag="configs/powerOffDragCurve.csv",
            power_on_drag="configs/powerOnDragCurve.csv",
            center_of_mass_without_motor=self.mass_data["structure_com"],
            coordinate_system_orientation="tail_to_nose",
        )
        
        # Add rail buttons
        self.rocket.set_rail_buttons(
            upper_button_position=0.0818,
            lower_button_position=-0.618,
            angular_position=45,
        )
        
        # Add motor at calculated position
        motor_position, _ = calculate_motor_position(
            self.config, 
            self.motor, 
            self.component_positions
        )
        self.rocket.add_motor(self.motor, position=motor_position)
    
    def _add_components(self):
        """Add all components to the rocket."""
        # Add nose cone
        nose_conf = self.config["aerodynamics"]["nose_cone"]
        self.rocket.add_nose(
            length=nose_conf["length"],
            kind=nose_conf["kind"],
            position=self.component_positions["nose"],
        )
        
        # Add fins
        fin_conf = self.config["aerodynamics"]["fins"]
        self.rocket.add_trapezoidal_fins(
            n=fin_conf["number"],
            root_chord=fin_conf["root_chord"],
            tip_chord=fin_conf["tip_chord"],
            span=fin_conf["span"],
            position=self.component_positions["fins"],
            cant_angle=fin_conf["cant_angle"],
            airfoil=("configs/NACA0012-radians.txt", "radians"),
        )
        
        # Add tail
        tail_conf = self.config["aerodynamics"]["tail"]
        self.rocket.add_tail(
            top_radius=tail_conf["top_radius"],
            bottom_radius=tail_conf["bottom_radius"],
            length=tail_conf["length"],
            position=self.component_positions["tail"],
        )
        
        # Add parachutes
        parachute_conf = self.config["parachutes"]
        
        self.rocket.add_parachute(
            name=parachute_conf["main"]["name"],
            cd_s=parachute_conf["main"]["cd_s"],
            trigger=parachute_conf["main"]["trigger"],
            sampling_rate=parachute_conf["main"]["sampling_rate"],
            lag=parachute_conf["main"]["lag"],
            noise=parachute_conf["main"]["noise"],
        )
        
        self.rocket.add_parachute(
            name=parachute_conf["drogue"]["name"],
            cd_s=parachute_conf["drogue"]["cd_s"],
            trigger=parachute_conf["drogue"]["trigger"],
            sampling_rate=parachute_conf["drogue"]["sampling_rate"],
            lag=parachute_conf["drogue"]["lag"],
            noise=parachute_conf["drogue"]["noise"],
        ) 