import math
import os
import datetime
import shutil
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid popping up windows
import matplotlib.pyplot as plt
from rocketpy import Environment, Flight, Rocket, SolidMotor
from rocketpy.plots import rocket_plots, flight_plots

# =============================================================================
# MATERIAL PROPERTIES DICTIONARY
# =============================================================================
materials = {
    "aluminum": {
        "density": 2700,           # kg/m³
        "yield_strength": 95e6,    # Pa
        "ultimate_strength": 150e6, # Pa
        "cost": 5                  # $5 per kg
    },
    "composite": {
        "density": 1600,           # kg/m³
        "yield_strength": 120e6,
        "ultimate_strength": 200e6,
        "cost": 20                 # $20 per kg
    },
    "fiberglass": {
        "density": 1850,           # kg/m³
        "yield_strength": 200e6,   # Pa
        "ultimate_strength": 345e6,# Pa
        "cost": 15                 # $15 per kg
    },
    "carbon_fiber": {
        "density": 1550,           # kg/m³
        "yield_strength": 500e6,
        "ultimate_strength": 600e6,
        "cost": 50                 # $50 per kg
    },
    "balsa_wood": {
        "density": 160,            # kg/m³
        "yield_strength": 3e6,
        "ultimate_strength": 5e6,
        "cost": 2                 # $2 per kg
    },
    "plywood": {
        "density": 700,            # kg/m³
        "yield_strength": 30e6,
        "ultimate_strength": 40e6,
        "cost": 1.5               # $1.50 per kg
    },
    "ABS_plastic": {
        "density": 1050,           # kg/m³
        "yield_strength": 40e6,
        "ultimate_strength": 50e6,
        "cost": 4                 # $4 per kg
    },
}

# =============================================================================
# MOTOR CONFIGURATIONS (SEPARATE FROM CONFIG)
# =============================================================================
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

# =============================================================================
# CONFIGURATION
# =============================================================================
# =============================================================================
# CONFIGURATION (including payload support)
# =============================================================================
config = {
    "goal_altitude": 10000,  # [m] desired altitude
    "motor_choice": "CesaroniM1670",  # Which motor to use from the motors dict
    "rocket_body": {
        "radius": 166 / 2000,  # [m]
        "length": 5,         # [m] cylindrical section
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
    # -------------------------------
    # New: Payload configuration block.
    # Define the payload mass (in kg) and its position (in meters)
    # relative to the rocket's center (0 corresponds to the rocket body's geometric center)
    "payload": {
        "mass": 5.0,      # payload mass in kg
        "position": 0.1,  # payload position in meters (positive is forward)
    },
}


# =============================================================================
# HELPER FUNCTIONS: MASS & INERTIA CALCULATIONS
# =============================================================================
def compute_rocket_body_mass(body_config):
    r = body_config["radius"]
    t = body_config["thickness"]
    L = body_config["length"]
    density = materials[body_config["material"]]["density"]
    volume = math.pi * L * (r**2 - (r - t)**2)
    return volume * density

def compute_nose_cone_mass(nose_config, body_radius):
    r = body_radius
    L = nose_config["length"]
    density = materials[nose_config["material"]]["density"]
    volume = (1/3) * math.pi * r**2 * L
    return volume * density

def compute_fins_mass(fins_config):
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
    R_avg = (tail_config["top_radius"] + tail_config["bottom_radius"]) / 2
    t = default_thickness
    L = tail_config["length"]
    density = materials[tail_config["material"]]["density"]
    volume = math.pi * L * (R_avg**2 - (R_avg - t)**2)
    return volume * density

def compute_total_mass(cfg):
    body_mass = compute_rocket_body_mass(cfg["rocket_body"])
    nose_mass = compute_nose_cone_mass(cfg["aerodynamics"]["nose_cone"], cfg["rocket_body"]["radius"])
    fins_mass = compute_fins_mass(cfg["aerodynamics"]["fins"])
    tail_mass = compute_tail_mass(cfg["aerodynamics"]["tail"], cfg["rocket_body"]["thickness"])
    motor_choice = config["motor_choice"]
    motor_mass = motors[motor_choice]["dry_mass"]
    return body_mass + nose_mass + fins_mass + tail_mass + motor_mass

def compute_inertia(total_mass, cfg):
    L_body = cfg["rocket_body"]["length"]
    L_nose = cfg["aerodynamics"]["nose_cone"]["length"]
    L_tail = cfg["aerodynamics"]["tail"]["length"]
    L_total = L_body + L_nose + L_tail
    r = cfg["rocket_body"]["radius"]
    I_trans = (1/12) * total_mass * L_total**2
    I_long = 0.5 * total_mass * r**2
    return (I_trans, I_trans, I_long)
# =============================================================================
# COMPUTE PARAMETERS (including payload)
# =============================================================================
body_mass = compute_rocket_body_mass(config["rocket_body"])
nose_mass = compute_nose_cone_mass(config["aerodynamics"]["nose_cone"], config["rocket_body"]["radius"])
fins_mass = compute_fins_mass(config["aerodynamics"]["fins"])
tail_mass = compute_tail_mass(config["aerodynamics"]["tail"], config["rocket_body"]["thickness"])
motor_choice = config["motor_choice"]
motor_mass = motors[motor_choice]["dry_mass"]

# Compute positions for individual components (relative to the rocket body center at 0)
body_length = config["rocket_body"]["length"]
nose_length = config["aerodynamics"]["nose_cone"]["length"]
tail_length = config["aerodynamics"]["tail"]["length"]

nose_position = body_length / 2 + nose_length / 2   # forward of center
fins_position = -body_length / 2 + 0.2                # near the aft section
tail_position = -body_length / 2 - tail_length / 2    # at the extreme tail

# --- Incorporate payload into the mass calculation ---
payload_mass = config.get("payload", {}).get("mass", 0)
payload_position = config.get("payload", {}).get("position", 0)  # relative to rocket center

# Compute the structure mass (without the motor)
structure_mass = body_mass + nose_mass + fins_mass + tail_mass + payload_mass

# Compute the structure's center of mass (weighted average)
# We assume the rocket body's mass (without payload) is uniformly distributed and centered at 0.
structure_com = (body_mass * 0 +
                 nose_mass * nose_position +
                 fins_mass * fins_position +
                 tail_mass * tail_position +
                 payload_mass * payload_position) / structure_mass

# Total rocket mass includes the motor mass
total_mass = structure_mass + motor_mass

# For overall COM, include the motor's contribution.
# The motor is added at a given position (here we use -1.255 as in your motor addition).
motor_position = -1.255
overall_com = (structure_mass * structure_com + motor_mass * motor_position) / total_mass

# For simplicity, we continue to use your existing inertia calculation.
inertia = compute_inertia(total_mass, config)

print("Computed total mass: {:.2f} kg".format(total_mass))
print("Computed overall center-of-mass: {:.2f} m".format(overall_com))
print("Computed inertia (Ixx, Iyy, Izz):", inertia)

# =============================================================================
# ENVIRONMENT SETUP WITH WEATHER CACHING
# =============================================================================
env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))

cache_weather = True
cache_dir = "weather_cache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
date_str = f"{tomorrow.year}-{tomorrow.month:02d}-{tomorrow.day:02d}"
cache_filename = os.path.join(cache_dir, f"weather_{env.latitude}_{env.longitude}_{date_str}.json")

if cache_weather and os.path.exists(cache_filename):
    print(f"Loading cached weather data from {cache_filename}")
    env.set_atmospheric_model(type="Forecast", file=cache_filename)
else:
    print("Fetching new weather data.")
    env.set_atmospheric_model(type="Forecast", file="GFS")
    try:
        shutil.copy("GFS", cache_filename)
        print(f"Weather data cached to {cache_filename}")
    except Exception as e:
        print(f"Failed to cache weather data: {e}")

# =============================================================================
# ROCKET SETUP
# =============================================================================
rocket = Rocket(
    radius=config["rocket_body"]["radius"],
    mass=total_mass,
    inertia=inertia,
    power_off_drag="configs/powerOffDragCurve.csv",
    power_on_drag="configs/powerOnDragCurve.csv",
    center_of_mass_without_motor=structure_com,
    coordinate_system_orientation="tail_to_nose",
)

rocket.set_rail_buttons(
    upper_button_position=0.0818,
    lower_button_position=-0.618,
    angular_position=45,
)

# Calculate the position for the motor at the back of the rocket
# The tail position is at the extreme tail
motor_choice = config["motor_choice"]
motor_config = motors[motor_choice]
motor = SolidMotor(**motor_config)

# Calculate motor length (estimate based on burn time and size)
motor_length = motor.grain_initial_height * motor.grain_number + 0.1  # Add extra for nozzle

# Position the motor at the back, but account for the motor length
# tail_position is already at the extreme back, so we need to move forward by half the motor length
motor_position = tail_position   # Move forward (right) by half the motor length

print(f"Motor position (at back of rocket): {motor_position:.3f} m")
print(f"Tail position: {tail_position:.3f} m")
print(f"Motor length: {motor_length:.3f} m")

rocket.add_motor(motor, position=motor_position)  # Instead of the hardcoded -1.255

rocket.add_nose(
    length=config["aerodynamics"]["nose_cone"]["length"],
    kind=config["aerodynamics"]["nose_cone"]["kind"],
    position=nose_position,
)

fin_conf = config["aerodynamics"]["fins"]
rocket.add_trapezoidal_fins(
    n=fin_conf["number"],
    root_chord=fin_conf["root_chord"],
    tip_chord=fin_conf["tip_chord"],
    span=fin_conf["span"],
    position=fins_position,
    cant_angle=fin_conf["cant_angle"],
    airfoil=("configs/NACA0012-radians.txt", "radians"),
)

tail_conf = config["aerodynamics"]["tail"]
rocket.add_tail(
    top_radius=tail_conf["top_radius"],
    bottom_radius=tail_conf["bottom_radius"],
    length=tail_conf["length"],
    position=tail_position,
)

# -----------------------------------------------------------------------------
# Add Parachutes using configuration
# -----------------------------------------------------------------------------
parachute_conf = config["parachutes"]

main_chute = rocket.add_parachute(
    name=parachute_conf["main"]["name"],
    cd_s=parachute_conf["main"]["cd_s"],
    trigger=parachute_conf["main"]["trigger"],
    sampling_rate=parachute_conf["main"]["sampling_rate"],
    lag=parachute_conf["main"]["lag"],
    noise=parachute_conf["main"]["noise"],
)

drogue_chute = rocket.add_parachute(
    name=parachute_conf["drogue"]["name"],
    cd_s=parachute_conf["drogue"]["cd_s"],
    trigger=parachute_conf["drogue"]["trigger"],
    sampling_rate=parachute_conf["drogue"]["sampling_rate"],
    lag=parachute_conf["drogue"]["lag"],
    noise=parachute_conf["drogue"]["noise"],
)

# =============================================================================
# FLIGHT SETUP & EXECUTION
# =============================================================================
print("Starting flight simulation...")
flight = Flight(
    rocket=rocket,
    environment=env,
    rail_length=config["launch"]["rail_length"],
    inclination=config["launch"]["inclination"],
    heading=config["launch"]["heading"],
)
# We avoid calling flight.all_info() so that interactive plots are not shown.
flight.export_kml(
    file_name="trajectory.kml",
    extrude=True,
    altitude_mode="relative_to_ground",
)

# =============================================================================
# POST-FLIGHT ANALYSIS & MATERIAL FAILURE CHECKS
# =============================================================================
t_final = flight.time[-1]
x_final = flight.x(t_final)
y_final = flight.y(t_final)
horizontal_distance = math.sqrt(x_final**2 + y_final**2)
flight_time = t_final
max_apogee = flight.apogee

# --- Fin Failure Check ---
fin_area = (fin_conf["root_chord"] + fin_conf["tip_chord"]) / 2 * fin_conf["span"]
fin_material = materials[fin_conf["material"]]
fin_force = flight.max_dynamic_pressure * fin_area
failure_threshold_fin = fin_material["ultimate_strength"] * fin_area
fin_failed = fin_force > failure_threshold_fin

print("Fin Force: ", fin_force)
print("Fin Failure Threshold: ", failure_threshold_fin)

# --- Body Tube Failure Checks ---
radius_body = config["rocket_body"]["radius"]
length_body = config["rocket_body"]["length"]
diameter_body = 2 * radius_body
F_body = flight.max_dynamic_pressure * (length_body * diameter_body)
M_bend = F_body * (length_body / 2)
Z_body = math.pi * (radius_body**2) * config["rocket_body"]["thickness"]
sigma_bend = M_bend / Z_body
A_shear = 2 * math.pi * radius_body * config["rocket_body"]["thickness"]
tau_shear = F_body / A_shear

body_material = materials[config["rocket_body"]["material"]]
body_bending_failed = sigma_bend > body_material["yield_strength"]
body_shear_failed = tau_shear > (0.6 * body_material["yield_strength"])

print("\n--- Body Tube Failure Checks ---")
print("Body Drag Force: {:.2f} N".format(F_body))
print("Bending Moment: {:.2f} N·m".format(M_bend))
print("Bending Stress: {:.2f} Pa".format(sigma_bend))
print("Shear Stress: {:.2f} Pa".format(tau_shear))

print("\n========== Flight Summary ==========")
print("Flight Time: {:.2f} s".format(flight_time))
print("Max Apogee: {:.2f} m".format(max_apogee))
print("Horizontal Distance from Launch: {:.2f} m".format(horizontal_distance))
if fin_failed:
    print("Warning: Fins failed under aerodynamic loads!")
else:
    print("Fins survived the aerodynamic loads.")
if body_bending_failed:
    print("Warning: Body tube failed in bending!")
else:
    print("Body tube bending check passed.")
if body_shear_failed:
    print("Warning: Body tube failed in shear!")
else:
    print("Body tube shear check passed.")
print("====================================\n")

# =============================================================================
# BOM (Bill of Materials) CALCULATIONS
# =============================================================================
bom = {}
body_material_key = config["rocket_body"]["material"]
bom[body_material_key] = bom.get(body_material_key, 0) + body_mass
nose_material_key = config["aerodynamics"]["nose_cone"]["material"]
bom[nose_material_key] = bom.get(nose_material_key, 0) + nose_mass
fin_material_key = config["aerodynamics"]["fins"]["material"]
bom[fin_material_key] = bom.get(fin_material_key, 0) + fins_mass
tail_material_key = config["aerodynamics"]["tail"]["material"]
bom[tail_material_key] = bom.get(tail_material_key, 0) + tail_mass

bom_cost = {}
total_cost = 0
for material_key, mass in bom.items():
    cost_per_kg = materials[material_key]["cost"]
    cost = mass * cost_per_kg
    bom_cost[material_key] = cost
    total_cost += cost

print("========== BOM Summary ==========")
for material_key, mass in bom.items():
    cost_per_kg = materials[material_key]["cost"]
    cost = bom_cost[material_key]
    print(f"Material: {material_key}")
    print(f"  Total Mass: {mass:.2f} kg")
    print(f"  Cost per kg: ${cost_per_kg:.2f}")
    print(f"  Total Cost: ${cost:.2f}\n")
print(f"Overall Structural Material Cost: ${total_cost:.2f}")
print("==================================\n")

# =============================================================================
# PLOT SAVING USING ROCKETPY PLOTS CLASSES
# =============================================================================
output_dir = "outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create rocket plots instance and save selected rocket plots to files.
rplots = rocket_plots._RocketPlots(rocket)


rplots.static_margin(filename=os.path.join(output_dir, "rocket_static_margin.png"))
rplots.drag_curves(filename=os.path.join(output_dir, "rocket_drag_curves.png"))

rplots.draw(filename=os.path.join(output_dir, "rocket_draw.png"))

# Create flight plots instance and save selected flight plots to files.
fplots = flight_plots._FlightPlots(flight)
fplots.trajectory_3d(filename=os.path.join(output_dir, "flight_trajectory_3d.png"))
fplots.linear_kinematics_data(filename=os.path.join(output_dir, "flight_linear_kinematics_data.png"))
fplots.attitude_data(filename=os.path.join(output_dir, "flight_attitude_data.png"))
fplots.flight_path_angle_data(filename=os.path.join(output_dir, "flight_path_angle_data.png"))
fplots.angular_kinematics_data(filename=os.path.join(output_dir, "flight_angular_kinematics_data.png"))
fplots.rail_buttons_forces(filename=os.path.join(output_dir, "flight_rail_buttons_forces.png"))
fplots.aerodynamic_forces(filename=os.path.join(output_dir, "flight_aerodynamic_forces.png"))
fplots.energy_data(filename=os.path.join(output_dir, "flight_energy_data.png"))
fplots.fluid_mechanics_data(filename=os.path.join(output_dir, "flight_fluid_mechanics_data.png"))
fplots.stability_and_control_data(filename=os.path.join(output_dir, "flight_stability_and_control_data.png"))
fplots.pressure_rocket_altitude(filename=os.path.join(output_dir, "flight_pressure_rocket_altitude.png"))
