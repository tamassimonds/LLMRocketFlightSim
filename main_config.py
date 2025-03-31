import math
import datetime
from rocketpy import Environment, Flight, Rocket, SolidMotor

# =============================================================================
# MATERIAL PROPERTIES
# =============================================================================
materials = {
    "aluminum": {
        "density": 2700,         # kg/m³
        "yield_strength": 95e6,  # Pa
        "ultimate_strength": 150e6,  # Pa
    },
    "composite": {
        "density": 1600,         # kg/m³
        "yield_strength": 120e6, # Pa
        "ultimate_strength": 200e6,# Pa
    },
    # Add additional materials if desired.
}

# =============================================================================
# CONFIGURATION
# =============================================================================
config = {
    "goal_altitude": 10000,  # [m] desired altitude
    "motor": {
        "choice": "Pro75M1670",
        "available": {
            "Pro75M1670": {
                "thrust_source": "Cesaroni_M1670.eng",
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
            # More motor choices can be added here.
        },
    },
    "rocket_body": {
        "radius": 133 / 2000,       # [m]
        "length": 2.5,              # [m] (cylindrical section)
        "thickness": 0.005,         # [m] wall thickness
        "material": "aluminum",     # Material assigned to the body
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "vonKarman",
            "length": 0.55829,         # [m]
            "material": "composite",   # Nose cone material
            # Optionally, you can define a nose_thickness if needed:
            "thickness": 0.005,
        },
        "fins": {
            "number": 4,
            "root_chord": 0.320,       # [m]
            "tip_chord": 0.060,        # [m]
            "span": 0.110,             # [m]
            "cant_angle": 0.5,         # [degrees]
            "material": "aluminum",    # Fin material
            "thickness": 0.005,        # [m] fin thickness
        },
        "tail": {
            "length": 0.060,           # [m]
            "top_radius": 0.0635,      # [m]
            "bottom_radius": 0.0435,   # [m]
        },
    },
    "launch": {
        "rail_length": 5.2,  # [m]
        "inclination": 85,   # [degrees]
        "heading": 0,        # [degrees]
    },
}

# =============================================================================
# HELPER FUNCTIONS: MASS & INERTIA CALCULATIONS
# =============================================================================
def compute_rocket_body_mass(body_config):
    r = body_config["radius"]
    t = body_config["thickness"]
    L = body_config["length"]
    # Use material density from the materials dict if available
    if "material" in body_config:
        density = materials[body_config["material"]]["density"]
    else:
        density = 2700  # default aluminum density
    # Volume of a cylindrical shell: V = π * L * (r² - (r-t)²)
    volume = math.pi * L * (r**2 - (r - t)**2)
    return volume * density

def compute_nose_cone_mass(nose_config, body_radius):
    r = body_radius  # assume nose base has same radius as rocket body
    L = nose_config["length"]
    if "material" in nose_config:
        density = materials[nose_config["material"]]["density"]
    else:
        density = 1600  # default composite density
    # Cone volume: V = 1/3 * π * r² * L
    volume = (1/3) * math.pi * r**2 * L
    return volume * density

def compute_fins_mass(fins_config):
    num = fins_config["number"]
    root = fins_config["root_chord"]
    tip = fins_config["tip_chord"]
    span = fins_config["span"]
    if "material" in fins_config:
        density = materials[fins_config["material"]]["density"]
    else:
        density = 2700  # default aluminum density
    thickness = fins_config.get("thickness", 0.005)
    # Approximate each fin as a trapezoidal prism:
    # Area = (root + tip) / 2 * span, then volume = area * thickness
    area = (root + tip) / 2 * span
    volume = area * thickness
    return num * volume * density

def compute_total_mass(cfg):
    body_mass = compute_rocket_body_mass(cfg["rocket_body"])
    nose_mass = compute_nose_cone_mass(cfg["aerodynamics"]["nose_cone"], cfg["rocket_body"]["radius"])
    fins_mass = compute_fins_mass(cfg["aerodynamics"]["fins"])
    motor_choice = cfg["motor"]["choice"]
    motor_mass = cfg["motor"]["available"][motor_choice]["dry_mass"]
    return body_mass + nose_mass + fins_mass + motor_mass

def compute_inertia(total_mass, cfg):
    # Simplified inertia approximation as a uniform rod.
    L_body = cfg["rocket_body"]["length"]
    L_nose = cfg["aerodynamics"]["nose_cone"]["length"]
    L_tail = cfg["aerodynamics"]["tail"]["length"]
    L_total = L_body + L_nose + L_tail
    r = cfg["rocket_body"]["radius"]
    I_trans = (1/12) * total_mass * L_total**2  # Ixx and Iyy
    I_long = 0.5 * total_mass * r**2            # Izz
    return (I_trans, I_trans, I_long)

# =============================================================================
# COMPUTE PARAMETERS
# =============================================================================
total_mass = compute_total_mass(config)
inertia = compute_inertia(total_mass, config)

print("Computed total mass: {:.2f} kg".format(total_mass))
print("Computed inertia (Ixx, Iyy, Izz):", inertia)

# For positioning the components, we assume the rocket’s center of mass is at 0.
body_length = config["rocket_body"]["length"]
nose_length = config["aerodynamics"]["nose_cone"]["length"]
tail_length = config["aerodynamics"]["tail"]["length"]

nose_position = body_length / 2 + nose_length / 2
fins_position = -body_length / 2 + 0.2
tail_position = -body_length / 2 - tail_length / 2

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================
env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))  # UTC time
env.set_atmospheric_model(type="Forecast", file="GFS")
env.info()

# =============================================================================
# ROCKET SETUP
# =============================================================================
rocket = Rocket(
    radius=config["rocket_body"]["radius"],
    mass=total_mass,
    inertia=inertia,
    power_off_drag="powerOffDragCurve.csv",
    power_on_drag="powerOnDragCurve.csv",
    center_of_mass_without_motor=0,  # (Could be computed more precisely)
    coordinate_system_orientation="tail_to_nose",
)

# Optionally, you can configure rail buttons
rocket.set_rail_buttons(
    upper_button_position=0.0818,
    lower_button_position=-0.618,
    angular_position=45,
)

# Add the selected motor
motor_choice = config["motor"]["choice"]
motor_config = config["motor"]["available"][motor_choice]
motor = SolidMotor(**motor_config)
rocket.add_motor(motor, position=-1.255)  # This position could be made configurable

# Add nose cone using computed position
rocket.add_nose(
    length=config["aerodynamics"]["nose_cone"]["length"],
    kind=config["aerodynamics"]["nose_cone"]["kind"],
    position=nose_position,
)

# Add trapezoidal fins using the config and computed position
fin_conf = config["aerodynamics"]["fins"]
rocket.add_trapezoidal_fins(
    n=fin_conf["number"],
    root_chord=fin_conf["root_chord"],
    tip_chord=fin_conf["tip_chord"],
    span=fin_conf["span"],
    position=fins_position,
    cant_angle=fin_conf["cant_angle"],
    airfoil=("NACA0012-radians.txt", "radians"),
)

# Add tail
tail_conf = config["aerodynamics"]["tail"]
rocket.add_tail(
    top_radius=tail_conf["top_radius"],
    bottom_radius=tail_conf["bottom_radius"],
    length=tail_conf["length"],
    position=tail_position,
)

rocket.all_info()

# =============================================================================
# FLIGHT SETUP & EXECUTION
# =============================================================================
flight = Flight(
    rocket=rocket,
    environment=env,
    rail_length=config["launch"]["rail_length"],
    inclination=config["launch"]["inclination"],
    heading=config["launch"]["heading"],
)
flight.all_info()

# =============================================================================
# EXPORT TRAJECTORY (OPTIONAL)
# =============================================================================
flight.export_kml(
    file_name="trajectory.kml",
    extrude=True,
    altitude_mode="relative_to_ground",
)

# =============================================================================
# POST-FLIGHT STATISTICS & MATERIAL FAILURE CHECKS
# =============================================================================
# Flight statistics
try:
    max_apogee = flight.apogee  # Apogee altitude (m)
except Exception:
    max_apogee = None

# Assuming flight.time, flight.x, and flight.y are available as arrays
flight_time = flight.time[-1] if hasattr(flight, 'time') and len(flight.time) > 0 else None
horizontal_distance = math.sqrt(flight.x[-1]**2 + flight.y[-1]**2) if hasattr(flight, 'x') and hasattr(flight, 'y') else None
max_dynamic_pressure = flight.max_dynamic_pressure if hasattr(flight, 'max_dynamic_pressure') else None

# Print flight stats
print("\n--- Flight Summary ---")
print("Flight Time: {:.2f} s".format(flight_time) if flight_time is not None else "Flight Time: N/A")
print("Max Apogee: {:.2f} m".format(max_apogee) if max_apogee is not None else "Max Apogee: N/A")
print("Horizontal Distance from Launch: {:.2f} m".format(horizontal_distance) if horizontal_distance is not None else "Horizontal Distance: N/A")
print("Max Dynamic Pressure: {:.2f} Pa".format(max_dynamic_pressure) if max_dynamic_pressure is not None else "Max Dynamic Pressure: N/A")

# =============================================================================
# SIMPLE MATERIAL FAILURE SIMULATION
# =============================================================================
# We perform a very basic check for three components: fins, rocket body, and nose cone.
# The idea: Estimate aerodynamic force as (max dynamic pressure * projected area) and compare
# it against a structural threshold computed as (yield strength * effective cross-sectional area).

# -- FIN CHECK --
fin_material = fin_conf["material"]
# Projected aerodynamic area for one fin (trapezoidal approximation)
A_fin = (fin_conf["root_chord"] + fin_conf["tip_chord"]) / 2 * fin_conf["span"]
F_aero_fin = max_dynamic_pressure * A_fin  # (N) -- very simplified assumption
# Structural cross-sectional area (assume thickness x root chord)
A_struct_fin = fin_conf["thickness"] * fin_conf["root_chord"]
yield_strength_fin = materials[fin_material]["yield_strength"]
F_threshold_fin = yield_strength_fin * A_struct_fin  # Threshold force in N
fin_status = "Intact" if F_aero_fin <= F_threshold_fin else "Failed"

# -- ROCKET BODY CHECK --
body_conf = config["rocket_body"]
body_material = body_conf["material"]
# For the body, use the frontal projected area (circle) to approximate the aerodynamic force
A_body_frontal = math.pi * (body_conf["radius"]**2)
F_aero_body = max_dynamic_pressure * A_body_frontal
# Structural cross-sectional area of the cylindrical wall (thickness * circumference)
A_struct_body = body_conf["thickness"] * (2 * math.pi * body_conf["radius"])
yield_strength_body = materials[body_material]["yield_strength"]
F_threshold_body = yield_strength_body * A_struct_body
body_status = "Intact" if F_aero_body <= F_threshold_body else "Failed"

# -- NOSE CONE CHECK --
nose_conf = config["aerodynamics"]["nose_cone"]
nose_material = nose_conf["material"]
# For the nose, we approximate the projected area as the same as the body frontal area.
A_nose_frontal = math.pi * (config["rocket_body"]["radius"]**2)
F_aero_nose = max_dynamic_pressure * A_nose_frontal
# Assume nose structural area uses a nose thickness (if provided) times a characteristic length (e.g., base diameter)
nose_thickness = nose_conf.get("thickness", 0.005)
A_struct_nose = nose_thickness * (2 * config["rocket_body"]["radius"])
yield_strength_nose = materials[nose_material]["yield_strength"]
F_threshold_nose = yield_strength_nose * A_struct_nose
nose_status = "Intact" if F_aero_nose <= F_threshold_nose else "Failed"

material_status = {
    "fins": fin_status,
    "rocket_body": body_status,
    "nose_cone": nose_status,
}

print("\n--- Material Failure Summary ---")
print("Fins: {}".format(material_status["fins"]))
print("Rocket Body: {}".format(material_status["rocket_body"]))
print("Nose Cone: {}".format(material_status["nose_cone"]))

# A summary statement that reports if any component failed
failed_components = [comp for comp, status in material_status.items() if status == "Failed"]
if failed_components:
    print("\nWARNING: The following component(s) exceeded their material limits and are considered to have failed:")
    for comp in failed_components:
        print(" - {}".format(comp))
else:
    print("\nAll components remained within safe material limits.")
