"""
Functions for analyzing rocket flight performance and structural integrity.
"""
import math
import numpy as np
from rocket_package.src.models.materials import materials
from rocket_package.src.models.motors.motors import motors

def analyze_flight(flight):
    """
    Analyze flight results.
    
    Args:
        flight: RocketPy Flight object.
        
    Returns:
        dict: Analysis results.
    """
    t_final = flight.time[-1]
    x_final = flight.x(t_final)
    y_final = flight.y(t_final)
    horizontal_distance = math.sqrt(x_final**2 + y_final**2)
    flight_time = t_final
    max_apogee = flight.apogee
    max_speed = flight.max_speed
    max_acceleration = flight.max_acceleration
    impact_velocity = flight.impact_velocity

    
    analysis = {
        "flight_time": flight_time,
        "max_apogee": max_apogee,
        "horizontal_distance": horizontal_distance,
        "max_speed": max_speed,
        "max_acceleration": max_acceleration,
        "max_dynamic_pressure": flight.max_dynamic_pressure,
        "x_final": x_final,
        "y_final": y_final,
        "t_final": t_final,
        "impact_velocity": impact_velocity
    }
    
    return analysis

def check_fin_failure(flight, fin_config, material_key):
    """
    Check if fins would fail under aerodynamic loads.
    
    Args:
        flight: RocketPy Flight object.
        fin_config (dict): Fin configuration.
        material_key (str): Material key for the fins.
        
    Returns:
        dict: Fin failure analysis.
    """
    fin_area = (fin_config["root_chord"] + fin_config["tip_chord"]) / 2 * fin_config["span"]
    fin_material = materials[material_key]
    fin_force = flight.max_dynamic_pressure * fin_area
    failure_threshold_fin = fin_material["ultimate_strength"] * fin_area * fin_config["thickness"]
    fin_failed = fin_force > failure_threshold_fin
    safety_factor = failure_threshold_fin / fin_force if fin_force > 0 else float('inf')
    
    fin_analysis = {
        "fin_force": fin_force,
        "failure_threshold": failure_threshold_fin,
        "failed": fin_failed,
        "safety_factor": safety_factor
    }
    
    return fin_analysis

def check_body_tube_failure(flight, body_config):
    """
    Check if body tube would fail under aerodynamic loads.
    
    Args:
        flight: RocketPy Flight object.
        body_config (dict): Body configuration.
        
    Returns:
        dict: Body tube failure analysis.
    """
    radius_body = body_config["radius"]
    length_body = body_config["length"]
    diameter_body = 2 * radius_body
    F_body = flight.max_dynamic_pressure * (length_body * diameter_body)
    M_bend = F_body * (length_body / 2)
    Z_body = math.pi * (radius_body**2) * body_config["thickness"]
    sigma_bend = M_bend / Z_body
    A_shear = 2 * math.pi * radius_body * body_config["thickness"]
    tau_shear = F_body / A_shear

    body_material = materials[body_config["material"]]
    body_bending_failed = sigma_bend > body_material["yield_strength"]
    body_shear_failed = tau_shear > (0.6 * body_material["yield_strength"])
    
    bending_safety_factor = body_material["yield_strength"] / sigma_bend if sigma_bend > 0 else float('inf')
    shear_safety_factor = (0.6 * body_material["yield_strength"]) / tau_shear if tau_shear > 0 else float('inf')
    
    body_analysis = {
        "body_drag_force": F_body,
        "bending_moment": M_bend,
        "bending_stress": sigma_bend,
        "shear_stress": tau_shear,
        "bending_failed": body_bending_failed,
        "shear_failed": body_shear_failed,
        "bending_safety_factor": bending_safety_factor,
        "shear_safety_factor": shear_safety_factor
    }
    
    return body_analysis

def calculate_bill_of_materials(config, component_masses):
    """
    Calculate bill of materials and costs.
    
    Args:
        config (dict): Rocket configuration.
        component_masses (dict): Component masses.
        
    Returns:
        dict: Bill of materials analysis.
    """
    bom = {}
    body_material_key = config["rocket_body"]["material"]
    bom[body_material_key] = bom.get(body_material_key, 0) + component_masses["body"]
    
    nose_material_key = config["aerodynamics"]["nose_cone"]["material"]
    bom[nose_material_key] = bom.get(nose_material_key, 0) + component_masses["nose"]
    
    fin_material_key = config["aerodynamics"]["fins"]["material"]
    bom[fin_material_key] = bom.get(fin_material_key, 0) + component_masses["fins"]
    
    tail_material_key = config["aerodynamics"]["tail"]["material"]
    bom[tail_material_key] = bom.get(tail_material_key, 0) + component_masses["tail"]

    bom_cost = {}
    total_cost = 0
    
    # Calculate material costs
    for material_key, mass in bom.items():
        cost_per_kg = materials[material_key]["cost"]
        cost = mass * cost_per_kg
        bom_cost[material_key] = cost
        total_cost += cost
    
    # Add motor cost
    motor_choice = config.get("motor_choice")
    if motor_choice and motor_choice in motors:
        motor_cost = motors[motor_choice].get("cost", 0)
        bom_cost["motor"] = motor_cost
        total_cost += motor_cost

    bom_analysis = {
        "materials": bom,
        "costs": bom_cost,
        "total_cost": total_cost
    }
    
    return bom_analysis

def analyze_rocket(flight, config, component_masses):
    """
    Perform comprehensive rocket analysis.
    
    Args:
        flight: RocketPy Flight object.
        config (dict): Rocket configuration.
        component_masses (dict): Component masses.
        
    Returns:
        dict: Complete analysis results.
    """
    flight_analysis = analyze_flight(flight)
    
    fin_analysis = check_fin_failure(
        flight, 
        config["aerodynamics"]["fins"], 
        config["aerodynamics"]["fins"]["material"]
    )
    
    body_analysis = check_body_tube_failure(flight, config["rocket_body"])
    
    bom_analysis = calculate_bill_of_materials(config, component_masses)
    
    structural_failure = fin_analysis["failed"] or body_analysis["bending_failed"] or body_analysis["shear_failed"]
    
    # Combine all analyses into a single result
    result = {
        "flight": flight_analysis,
        "structural": {
            "fins": fin_analysis,
            "body": body_analysis,
            "overall_failure": structural_failure
        },
        "materials": bom_analysis
    }
    
    return result 