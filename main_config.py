import math
import os
import datetime
import matplotlib.pyplot as plt
from rocketpy import Environment, Flight, Rocket, SolidMotor

# =============================================================================
# MATERIAL PROPERTIES DICTIONARY
# =============================================================================
materials = {
    "aluminum": {
        "density": 2700,           # kg/m³
        "yield_strength": 95e6,    # Pa
        "ultimate_strength": 150e6 # Pa
    },
    "composite": {
        "density": 1600,           # kg/m³
        "yield_strength": 120e6,   
        "ultimate_strength": 200e6
    },
    "paper": {
        "density": 1000,           # kg/m³
        "yield_strength": 10e6,   
        "ultimate_strength": 20e6
    },
    # add more materials as needed
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
            # You could add more motor configurations here...
        },
    },
    "rocket_body": {
        "radius": 133 / 2000,       # [m]
        "length": 2.5,              # [m] (cylindrical section)
        "material": "aluminum",     # material key
        "thickness": 0.05,         # [m] wall thickness
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "vonKarman",
            "length": 0.55829,         # [m]
            "material": "composite",   # material key
        },
        "fins": {
            "number": 4,
            "root_chord": 0.320,       # [m]
            "tip_chord": 0.060,        # [m]
            "span": 0.110,             # [m]
            "cant_angle": 0.5,         # [degrees]
            "material": "paper",       # material key
            "thickness": 0.005,        # [m] fin thickness
        },
        "tail": {
            "length": 0.060,          # [m]
            "top_radius": 0.0635,       # [m]
            "bottom_radius": 0.0435,    # [m]
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
    # Use material density from materials dict:
    density = materials[body_config["material"]]["density"]
    # Volume of a cylindrical shell: V = π * L * (r² - (r-t)²)
    volume = math.pi * L * (r**2 - (r - t)**2)
    return volume * density

def compute_nose_cone_mass(nose_config, body_radius):
    r = body_radius  # assume nose base has same radius as rocket body
    L = nose_config["length"]
    density = materials[nose_config["material"]]["density"]
    # Cone volume: V = 1/3 * π * r² * L
    volume = (1/3) * math.pi * r**2 * L
    return volume * density

def compute_fins_mass(fins_config):
    num = fins_config["number"]
    root = fins_config["root_chord"]
    tip = fins_config["tip_chord"]
    span = fins_config["span"]
    thickness = fins_config.get("thickness", 0.005)
    density = materials[fins_config["material"]]["density"]
    # Approximate each fin as a trapezoidal prism:
    # Area = (root + tip)/2 * span, then volume = area * thickness
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
    L_body = cfg["rocket_body"]["length"]
    L_nose = cfg["aerodynamics"]["nose_cone"]["length"]
    L_tail = cfg["aerodynamics"]["tail"]["length"]
    L_total = L_body + L_nose + L_tail
    r = cfg["rocket_body"]["radius"]
    I_trans = (1/12) * total_mass * L_total**2
    I_long = 0.5 * total_mass * r**2
    return (I_trans, I_trans, I_long)

# =============================================================================
# COMPUTE PARAMETERS
# =============================================================================
total_mass = compute_total_mass(config)
inertia = compute_inertia(total_mass, config)

print("Computed total mass: {:.2f} kg".format(total_mass))
print("Computed inertia (Ixx, Iyy, Izz):", inertia)

# Compute component positions based on rocket body length
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
env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))  # UTC hour
env.set_atmospheric_model(type="Forecast", file="GFS")
# env.info()

# =============================================================================
# ROCKET SETUP
# =============================================================================
rocket = Rocket(
    radius=config["rocket_body"]["radius"],
    mass=total_mass,
    inertia=inertia,
    power_off_drag="powerOffDragCurve.csv",
    power_on_drag="powerOnDragCurve.csv",
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose",
)

rocket.set_rail_buttons(
    upper_button_position=0.0818,
    lower_button_position=-0.618,
    angular_position=45,
)

motor_choice = config["motor"]["choice"]
motor_config = config["motor"]["available"][motor_choice]
motor = SolidMotor(**motor_config)
rocket.add_motor(motor, position=-1.255)

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
    airfoil=("NACA0012-radians.txt", "radians"),
)

tail_conf = config["aerodynamics"]["tail"]
rocket.add_tail(
    top_radius=tail_conf["top_radius"],
    bottom_radius=tail_conf["bottom_radius"],
    length=tail_conf["length"],
    position=tail_position,
)

# rocket.all_info()

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
# flight.all_info()

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
max_apogee = flight.apogee  # scalar property

# --- Fin Failure Check (as before) ---
fin_area = (fin_conf["root_chord"] + fin_conf["tip_chord"]) / 2 * fin_conf["span"]
fin_material = materials[fin_conf["material"]]
fin_force = flight.max_dynamic_pressure * fin_area
failure_threshold_fin = fin_material["ultimate_strength"] * fin_area
fin_failed = fin_force > failure_threshold_fin

print("Fin Force: ", fin_force)
print("Fin Failure Threshold: ", failure_threshold_fin)

# --- Body Tube Failure Checks ---
# For the body tube, assume the drag force is applied over the side area:
radius_body = config["rocket_body"]["radius"]
length_body = config["rocket_body"]["length"]
diameter_body = 2 * radius_body

# Approximate drag force on the body tube:
F_body = flight.max_dynamic_pressure * (length_body * diameter_body)
# Approximate bending moment (assume force acts at mid-length)
M_bend = F_body * (length_body / 2)
# Section modulus for a thin-walled circular tube: Z = π * r² * t
Z_body = math.pi * (radius_body**2) * config["rocket_body"]["thickness"]
sigma_bend = M_bend / Z_body

# Approximate shear stress:
A_shear = 2 * math.pi * radius_body * config["rocket_body"]["thickness"]
tau_shear = F_body / A_shear

body_material = materials[config["rocket_body"]["material"]]
body_bending_failed = sigma_bend > body_material["yield_strength"]
# For shear, assume failure if tau exceeds ~60% of yield strength
body_shear_failed = tau_shear > (0.6 * body_material["yield_strength"])

print("\n--- Body Tube Failure Checks ---")
print("Body Drag Force: {:.2f} N".format(F_body))
print("Bending Moment: {:.2f} N·m".format(M_bend))
print("Bending Stress: {:.2f} Pa".format(sigma_bend))
print("Shear Stress: {:.2f} Pa".format(tau_shear))

# =============================================================================
# PRINT SUMMARY OF FLIGHT & MATERIAL STATUS
# =============================================================================
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
# SAVE ALL MATPLOTLIB FIGURES TO PNG FILES IN 'outputs' FOLDER
# =============================================================================
output_dir = "outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

fig_nums = plt.get_fignums()
for num in fig_nums:
    plt.figure(num)
    filename = os.path.join(output_dir, f"figure_{num}.png")
    plt.savefig(filename)
    print(f"Figure {num} saved as {filename}")
plt.close('all')
