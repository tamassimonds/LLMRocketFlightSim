"""
Rocket flight simulation classes.
"""
import os
import matplotlib.pyplot as plt
from rocketpy import Flight
from src.models.rocket_builder import RocketBuilder
from src.utils.environment_utils import (
    setup_environment_from_data, 
    setup_environment_with_cache,
    create_constant_wind_environment
)
from src.analysis.rocket_analysis import analyze_rocket

class RocketSimulation:
    """Manage rocket flight simulations."""
    
    def __init__(self, config, environment=None, output_dir="outputs"):
        """
        Initialize rocket simulation.
        
        Args:
            config (dict): Rocket configuration.
            environment (Environment, optional): RocketPy Environment object.
            output_dir (str, optional): Directory for saving outputs.
        """
        self.config = config
        self.environment = environment
        self.rocket = None
        self.flight = None
        self.component_masses = None
        self.mass_data = None
        self.results = None
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def setup_environment(self, env_type="data", **kwargs):
        """
        Set up the simulation environment.
        
        Args:
            env_type (str): Type of environment to set up.
                           "data" - Use provided data.
                           "cache" - Use cached or fetch new data.
                           "constant_wind" - Create environment with constant wind.
            **kwargs: Additional parameters for environment setup.
        
        Returns:
            Environment: RocketPy Environment object.
        """
        if env_type == "data":
            data_env = kwargs.get("data_env", None)
            if data_env is None:
                # Get wind details from config if available
                wind_u = self.config.get("env", {}).get("wind_u", 0)
                wind_v = self.config.get("env", {}).get("wind_v", 0)
                
                # Create a default data environment
                data_env = create_constant_wind_environment(wind_u, wind_v)
            
            self.environment = setup_environment_from_data(data_env)
        
        elif env_type == "cache":
            cache_file = kwargs.get("cache_file", "environment.json")
            lat = kwargs.get("lat", 32.990254)
            lon = kwargs.get("lon", -106.974998)
            elev = kwargs.get("elev", 1400)
            self.environment = setup_environment_with_cache(lat, lon, elev, cache_file)
        
        elif env_type == "constant_wind":
            wind_u = kwargs.get("wind_u", 5)
            wind_v = kwargs.get("wind_v", 5)
            heights = kwargs.get("heights", None)
            
            data_env = create_constant_wind_environment(wind_u, wind_v, heights)
            self.environment = setup_environment_from_data(data_env)
        
        else:
            raise ValueError(f"Unknown environment type: {env_type}")
        
        return self.environment
    
    def build_rocket(self, motor_configs=None):
        """
        Build the rocket model.
        
        Args:
            motor_configs (dict, optional): Motor configurations.
            
        Returns:
            Rocket: RocketPy Rocket object.
        """
        builder = RocketBuilder(self.config, motor_configs)
        self.rocket, self.component_masses, self.mass_data = builder.build()
        return self.rocket
    
    def run_simulation(self):
        """
        Run the flight simulation.
        
        Returns:
            Flight: RocketPy Flight object.
        """
        if self.rocket is None:
            self.build_rocket()
        
        if self.environment is None:
            self.setup_environment()
        
        launch_conf = self.config["launch"]
        
        print("Starting flight simulation...")
        self.flight = Flight(
            rocket=self.rocket,
            environment=self.environment,
            rail_length=launch_conf["rail_length"],
            inclination=launch_conf["inclination"],
            heading=launch_conf["heading"],
        )
        
        return self.flight
    
    def analyze_results(self):
        """
        Analyze the simulation results.
        
        Returns:
            dict: Analysis results.
        """
        if self.flight is None:
            raise ValueError("No flight to analyze. Run a simulation first.")
        
        self.results = analyze_rocket(self.flight, self.config, self.component_masses)
        return self.results
    
    def save_plots(self, include_kml=True):
        """
        Save plots from the simulation.
        
        Args:
            include_kml (bool): Whether to export KML trajectory.
            
        Returns:
            list: Paths to saved files.
        """
        from rocketpy.plots import rocket_plots, flight_plots
        
        if self.rocket is None or self.flight is None:
            raise ValueError("No rocket or flight to plot. Run a simulation first.")
        
        # Save KML file if requested
        if include_kml:
            self.flight.export_kml(
                file_name=os.path.join(self.output_dir, "trajectory.kml"),
                extrude=True,
                altitude_mode="relative_to_ground",
            )
        
        # Create rocket plots instance and save selected rocket plots to files
        rplots = rocket_plots._RocketPlots(self.rocket)
        rplots.static_margin(filename=os.path.join(self.output_dir, "rocket_static_margin.png"))
        rplots.drag_curves(filename=os.path.join(self.output_dir, "rocket_drag_curves.png"))
        rplots.draw(filename=os.path.join(self.output_dir, "rocket_draw.png"))
        
        # Create flight plots instance and save selected flight plots to files
        fplots = flight_plots._FlightPlots(self.flight)
        fplots.trajectory_3d(filename=os.path.join(self.output_dir, "flight_trajectory_3d.png"))
        fplots.linear_kinematics_data(filename=os.path.join(self.output_dir, "flight_linear_kinematics_data.png"))
        fplots.attitude_data(filename=os.path.join(self.output_dir, "flight_attitude_data.png"))
        fplots.flight_path_angle_data(filename=os.path.join(self.output_dir, "flight_path_angle_data.png"))
        fplots.angular_kinematics_data(filename=os.path.join(self.output_dir, "flight_angular_kinematics_data.png"))
        fplots.rail_buttons_forces(filename=os.path.join(self.output_dir, "flight_rail_buttons_forces.png"))
        fplots.aerodynamic_forces(filename=os.path.join(self.output_dir, "flight_aerodynamic_forces.png"))
        fplots.energy_data(filename=os.path.join(self.output_dir, "flight_energy_data.png"))
        fplots.fluid_mechanics_data(filename=os.path.join(self.output_dir, "flight_fluid_mechanics_data.png"))
        fplots.stability_and_control_data(filename=os.path.join(self.output_dir, "flight_stability_and_control_data.png"))
        fplots.pressure_rocket_altitude(filename=os.path.join(self.output_dir, "flight_pressure_rocket_altitude.png"))
        
        return [f for f in os.listdir(self.output_dir) if f.endswith(".png") or f.endswith(".kml")]
    
    def print_summary(self):
        """Print a summary of the simulation results."""
        if not hasattr(self, 'results') or self.results is None:
            print("No results to display. Run analyze_results() first.")
            return
        
        flight_results = self.results["flight"]
        structural_results = self.results["structural"]
        material_results = self.results["materials"]
        
        print("\n=== FLIGHT RESULTS ===")
        print(f"Max Apogee: {flight_results['max_apogee']:.2f} m")
        print(f"Flight Time: {flight_results['flight_time']:.2f} s")
        print(f"Max Speed: {flight_results['max_speed']:.2f} m/s")
        print(f"Max Acceleration: {flight_results['max_acceleration']:.2f} m/s²")
        print(f"Horizontal Distance: {flight_results['horizontal_distance']:.2f} m")
        
        print("\n=== STRUCTURAL ANALYSIS ===")
        print(f"Overall Structural Failure: {structural_results['overall_failure']}")
        
        fin_results = structural_results["fins"]
        print("\nFin Analysis:")
        print(f"  Fin Force: {fin_results['fin_force']:.2f} N")
        print(f"  Failure Threshold: {fin_results['failure_threshold']:.2f} N")
        print(f"  Safety Factor: {fin_results['safety_factor']:.2f}")
        print(f"  Failed: {fin_results['failed']}")
        
        body_results = structural_results["body"]
        print("\nBody Tube Analysis:")
        print(f"  Body Drag Force: {body_results['body_drag_force']:.2f} N")
        print(f"  Bending Moment: {body_results['bending_moment']:.2f} N·m")
        print(f"  Bending Stress: {body_results['bending_stress']:.2f} Pa")
        print(f"  Shear Stress: {body_results['shear_stress']:.2f} Pa")
        print(f"  Bending Safety Factor: {body_results['bending_safety_factor']:.2f}")
        print(f"  Shear Safety Factor: {body_results['shear_safety_factor']:.2f}")
        print(f"  Bending Failure: {body_results['bending_failed']}")
        print(f"  Shear Failure: {body_results['shear_failed']}")
        
        print("\n=== BILL OF MATERIALS ===")
        print(f"Total Cost: ${material_results['total_cost']:.2f}")
        
        # Print motor cost if available
        if "motor" in material_results['costs']:
            motor_cost = material_results['costs']["motor"]
            print(f"  Motor ({self.config['motor_choice']}): ${motor_cost:.2f}")
        
        # Print material costs
        for material, mass in material_results['materials'].items():
            cost = material_results['costs'][material]
            print(f"  {material}: {mass:.2f} kg - ${cost:.2f}")
        
        print("\n===========================") 