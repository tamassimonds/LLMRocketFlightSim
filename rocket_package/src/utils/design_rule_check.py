"""
Design Rule Check (DRC) utility for rocket configurations.

This module provides functions to validate rocket configurations before simulation.
It checks for basic physical constraints and design rules to catch obvious errors.
"""

from typing import Dict, Any, List, Tuple
from rocket_package.src.models.motors.motors import motors

def check_rocket_configuration(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Perform a design rule check on a rocket configuration.
    
    Args:
        config (dict): Rocket configuration
        
    Returns:
        tuple: (passed, issues)
            - passed (bool): True if all checks passed, False otherwise
            - issues (list): List of issue descriptions if any were found
    """
    issues = []
    
    # Check motor choice
    motor_choice = config.get("motor_choice")
    if not motor_choice:
        issues.append("No motor specified (missing 'motor_choice' field)")
    elif motor_choice not in motors:
        issues.append(f"Unknown motor: '{motor_choice}'. Available motors: {', '.join(motors.keys())}")
    
    # Get motor data if available
    motor_config = motors.get(motor_choice, {})
    motor_radius = motor_config.get("nozzle_radius", 0) * 1000  # Convert to mm for comparison
    
    # Check rocket body
    if "rocket_body" not in config:
        issues.append("Missing 'rocket_body' section")
    else:
        body = config["rocket_body"]
        
        # Check body dimensions
        if "radius" not in body:
            issues.append("Missing rocket body radius")
        elif body["radius"] <= 0:
            issues.append(f"Invalid rocket body radius: {body['radius']}")
        elif motor_radius > 0 and body["radius"] * 1000 < motor_radius:
            issues.append(f"Rocket body radius ({body['radius'] * 1000:.1f} mm) is smaller than motor radius ({motor_radius:.1f} mm)")
        
        if "length" not in body:
            issues.append("Missing rocket body length")
        elif body["length"] <= 0:
            issues.append(f"Invalid rocket body length: {body['length']}")
        
        if "thickness" not in body:
            issues.append("Missing rocket body thickness")
        elif body["thickness"] <= 0:
            issues.append(f"Invalid rocket body thickness: {body['thickness']}")
        elif body.get("radius", 0) > 0 and body["thickness"] >= body["radius"]:
            issues.append(f"Body thickness ({body['thickness']}) must be less than radius ({body['radius']})")
        
        if "material" not in body:
            issues.append("Missing rocket body material")
    
    # Check aerodynamics section
    if "aerodynamics" not in config:
        issues.append("Missing 'aerodynamics' section")
    else:
        aero = config["aerodynamics"]
        
        # Check nose cone
        if "nose_cone" not in aero:
            issues.append("Missing 'nose_cone' section")
        else:
            nose = aero["nose_cone"]
            if "length" not in nose:
                issues.append("Missing nose cone length")
            elif nose["length"] <= 0:
                issues.append(f"Invalid nose cone length: {nose['length']}")
                
            if "kind" not in nose:
                issues.append("Missing nose cone kind")
            elif nose["kind"] not in ["conical", "ogive", "von karman", "vonKarman", "von Karman", "parabolic", "elliptical"]:
                issues.append(f"Invalid nose cone kind: {nose['kind']}. Valid types are: conical, ogive, von karman, von Karman, parabolic, elliptical")
                
            if "material" not in nose:
                issues.append("Missing nose cone material")
        
        # Check fins
        if "fins" not in aero:
            issues.append("Missing 'fins' section")
        else:
            fins = aero["fins"]
            if "number" not in fins:
                issues.append("Missing number of fins")
            elif not isinstance(fins["number"], int) or fins["number"] <= 0:
                issues.append(f"Invalid number of fins: {fins['number']}. Must be a positive integer.")
            
            if "root_chord" not in fins:
                issues.append("Missing fin root chord")
            elif fins["root_chord"] <= 0:
                issues.append(f"Invalid fin root chord: {fins['root_chord']}")
                
            if "tip_chord" not in fins:
                issues.append("Missing fin tip chord")
            elif fins["tip_chord"] < 0:
                issues.append(f"Invalid fin tip chord: {fins['tip_chord']}")
                
            if "span" not in fins:
                issues.append("Missing fin span")
            elif fins["span"] <= 0:
                issues.append(f"Invalid fin span: {fins['span']}")
                
            if "material" not in fins:
                issues.append("Missing fin material")
                
            if "thickness" not in fins:
                issues.append("Missing fin thickness")
            elif fins["thickness"] <= 0:
                issues.append(f"Invalid fin thickness: {fins['thickness']}")
    
        # Check tail
        if "tail" not in aero:
            issues.append("Missing 'tail' section")
        else:
            tail = aero["tail"]
            if "length" not in tail:
                issues.append("Missing tail length")
            elif tail["length"] <= 0:
                issues.append(f"Invalid tail length: {tail['length']}")
                
            if "top_radius" not in tail:
                issues.append("Missing tail top radius")
            elif tail["top_radius"] <= 0:
                issues.append(f"Invalid tail top radius: {tail['top_radius']}")
                
            if "bottom_radius" not in tail:
                issues.append("Missing tail bottom radius")
            elif tail["bottom_radius"] <= 0:
                issues.append(f"Invalid tail bottom radius: {tail['bottom_radius']}")
                
            if "material" not in tail:
                issues.append("Missing tail material")
    
    # Check parachutes
    if "parachutes" not in config:
        issues.append("Missing 'parachutes' section")
    else:
        parachutes = config["parachutes"]
        
        # Check main parachute
        if "main" not in parachutes:
            issues.append("Missing main parachute configuration")
        else:
            main = parachutes["main"]
            if "cd_s" not in main:
                issues.append("Missing main parachute drag coefficient")
            elif main["cd_s"] <= 0:
                issues.append(f"Invalid main parachute drag coefficient: {main['cd_s']}")
        
        # Check drogue parachute
        if "drogue" not in parachutes:
            issues.append("Missing drogue parachute configuration")
        else:
            drogue = parachutes["drogue"]
            if "cd_s" not in drogue:
                issues.append("Missing drogue parachute drag coefficient")
            elif drogue["cd_s"] <= 0:
                issues.append(f"Invalid drogue parachute drag coefficient: {drogue['cd_s']}")
    
    # Check launch configuration
    if "launch" not in config:
        issues.append("Missing 'launch' section")
    else:
        launch = config["launch"]
        if "rail_length" not in launch:
            issues.append("Missing launch rail length")
        elif launch["rail_length"] <= 0:
            issues.append(f"Invalid launch rail length: {launch['rail_length']}")
            
        if "inclination" not in launch:
            issues.append("Missing launch inclination")
        elif launch["inclination"] < 0 or launch["inclination"] > 90:
            issues.append(f"Invalid launch inclination: {launch['inclination']}. Must be between 0 and 90 degrees.")
    
    # Overall design consistency checks
    if "rocket_body" in config and "aerodynamics" in config:
        body = config["rocket_body"]
        aero = config["aerodynamics"]
        
        # Check if nose + body + tail length seems reasonable
        if ("length" in body and 
            "nose_cone" in aero and "length" in aero["nose_cone"] and
            "tail" in aero and "length" in aero["tail"]):
            
            total_length = body["length"] + aero["nose_cone"]["length"] + aero["tail"]["length"]
            
            # Sanity check on total length (arbitrary values, adjust as needed)
            if total_length < 0.2:  # 20 cm is very small for a rocket
                issues.append(f"Total rocket length ({total_length:.2f} m) seems unrealistically small")
            elif total_length > 10:  # 10 m is very large for most amateur rockets
                issues.append(f"Total rocket length ({total_length:.2f} m) seems unrealistically large")
    
    # Return results
    passed = len(issues) == 0
    return (passed, issues)

def generate_drc_report(config: Dict[str, Any]) -> str:
    """
    Generate a human-readable DRC report for a rocket configuration.
    
    Args:
        config (dict): Rocket configuration
        
    Returns:
        str: Formatted DRC report
    """
    passed, issues = check_rocket_configuration(config)
    
    report = []
    report.append("=== DESIGN RULE CHECK REPORT ===")
    
    if passed:
        report.append("✅ All design rule checks passed!")
    else:
        report.append(f"❌ Design rule check failed with {len(issues)} issue(s):")
        for i, issue in enumerate(issues, 1):
            report.append(f"  {i}. {issue}")
    
    report.append("===============================")
    
    return "\n".join(report) 