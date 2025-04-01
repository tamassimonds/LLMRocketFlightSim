from rocket_interface import process_llm_response

from math import exp



LLM_response = """
### Reasoning for Rocket Design Choices

#### **1. Motor Selection**
- **Target Apogee**: 3000 meters is a moderately high altitude, requiring a motor with sufficient total impulse (Isp) and thrust to overcome gravity and drag.
- **Wind Conditions**: 20 m/s wind from the East suggests the need for a stable rocket with sufficient thrust to counteract wind drift.
- **Motor Analysis**:
  - **Pro75M1670 (CTI)**: Total impulse of 6023.6 Ns, Isp of 198s, and max thrust of 2200 N. This motor provides a good balance between thrust and burn time (3.9s), making it suitable for reaching 3000m.
  - **CesaroniM1670 (CTI)**: Similar specs to Pro75M1670 but slightly heavier (3.101 kg vs. 1.815 kg dry mass). The Pro75M1670 is lighter and thus more efficient for our target.
  - **AeroTechK700W (AT)**: Lower total impulse (2249 Ns) and thrust, insufficient for 3000m.
  - **CesaroniO3700/O5800**: Overkill for 3000m, designed for much higher altitudes.
  - **AeroTechH128W/CesaroniK160**: Too low total impulse for the target.
- **Choice**: **Pro75M1670** (best balance of thrust, impulse, and weight).

#### **2. Rocket Body**
- **Material**: **Carbon fiber** (lightweight, high strength-to-weight ratio, ideal for high-performance rockets).
- **Radius**: 75 mm (0.075 m) to match the motor diameter.
- **Length**: ~3.0 m (to ensure stability and accommodate motor + payload).
- **Thickness**: 0.002 m (2 mm, sufficient for structural integrity while keeping weight low).

#### **3. Nose Cone**
- **Shape**: **Von Karman** (optimal for reducing drag at supersonic/subsonic speeds).
- **Length**: ~0.6 m (20% of total rocket length for smooth airflow transition).
- **Material**: **Carbon fiber** (matches body for consistency and strength).

#### **4. Fins**
- **Number**: 4 (standard for stability).
- **Shape**: Tapered (root chord > tip chord) for aerodynamic efficiency.
  - Root chord: 0.2 m
  - Tip chord: 0.1 m
  - Span: 0.15 m
- **Cant Angle**: 0° (no cant for straight flight).
- **Material**: **Composite** (lightweight and stiff).
- **Thickness**: 0.003 m (3 mm, robust enough for wind loads).

#### **5. Tail**
- **Length**: 0.1 m (short transition between body and motor).
- **Top Radius**: 0.075 m (matches body).
- **Bottom Radius**: 0.074 m (slightly smaller to avoid error).
- **Material**: **Carbon fiber** (consistent with body).

#### **6. Parachutes**
- **Drogue**: Small parachute for stabilization during descent.
  - CdS: 0.2 m² (slows descent to ~20 m/s).
- **Main**: Larger parachute for safe landing.
  - CdS: 1.0 m² (slows descent to ~5 m/s).
- **Trigger**: Both deploy at apogee (simplified for this design).

#### **7. Launch Rail**
- **Rail Length**: 5.0 m (ensures stable launch in 20 m/s wind).
- **Inclination**: 85° (nearly vertical to minimize wind drift).
- **Heading**: 90° (East, into the wind to counteract drift).

#### **8. Payload**
- **Mass**: 1.0 kg (typical for altimeters/sensors).
- **Position**: 0.5 m from nose cone base (centered for balance).

### Final Design (Python Dictionary)
```python
config = {
    "motor_choice": "Pro75M1670",
    "rocket_body": {
        "radius": 0.075,
        "length": 3,
        "material": "carbon_fiber",
        "thickness": 0.002,
    },
    "aerodynamics": {
        "nose_cone": {
            "kind": "von karman",
            "length": 0.6,
            "material": "carbon_fiber",
        },
        "fins": {
            "number": 1,
            "root_chord": 0.2,
            "tip_chord": 0.1,
            "span": 0.15,
            "cant_angle": 0,
            "material": "composite",
            "thickness": 0.003,
        },
        "tail": {
            "length": 0.1,
            "top_radius": 0.075,
            "bottom_radius": 0.074,
            "material": "carbon_fiber",
        },
    },
    "parachutes": {
        "main": {
            "name": "Main",
            "cd_s": 1.0,
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
        "drogue": {
            "name": "Drogue",
            "cd_s": 0.2,
            "trigger": "apogee",
            "sampling_rate": 105,
            "lag": 1.5,
            "noise": (0, 8.3, 0.5),
        },
    },
    "launch": {
        "rail_length": 5.0,
        "inclination": 85,
        "heading": 90,
    },
    "payload": {
        "mass": 1.0,
        "position": 0.5,
    },
}
```

### Key Trade-offs
- **Motor**: Pro75M1670 was chosen over CesaroniM1670 due to lower dry mass.
- **Materials**: Carbon fiber/composite for strength/weight, though more expensive than aluminum.
- **Fins**: Tapered design balances drag and stability.
- **Parachutes**: Conservative sizing ensures safe recovery in wind.

This design should reliably reach 3000m while handling 20 m/s winds. Adjustments may be needed after simulation (e.g., fin size or parachute CdS).
"""


response = process_llm_response(LLM_response, 3000, wind_speed=20, wind_direction="E", save_outputs=False)

reward = 0
target_apogee = 1000

if response['simple_results']:
    reward += 0.05 #compiled so here's some reward

distance_reward = exp(-abs(response['simple_results']["apogee"] - target_apogee) / (target_apogee*0.1))
# cost_reward = exp(-abs(response['simple_results']["total_cost"]) / (1000))

reward += distance_reward
