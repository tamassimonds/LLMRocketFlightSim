#!/usr/bin/env python3
"""
Reward Calculation - Calculate rewards based on rocket simulation results.

This module provides functions to:
1. Calculate reward scores based on rocket simulation results.
2. Format the reward information in a human-readable way
3. Provide detailed breakdowns of the reward calculation
"""

from typing import Dict, Any, Tuple
import math


def calculate_reward(
    apogee: float,
    target_apogee: float,
    horizontal_distance: float = 0,
    total_cost: float = 0,
    impact_velocity: float = 0,
    structural_failure: bool = False
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate a performance reward based on simulation results.
    
    The reward is calculated based on:
    1. Accuracy in reaching target apogee
    2. Cost-effectiveness of the design
    3. Structural integrity
    4. Horizontal distance
    5. Impact velocity
    
    Args:
        apogee (float): Actual apogee reached in meters
        target_apogee (float): Target apogee in meters
        horizontal_distance (float): Horizontal distance traveled in meters
        total_cost (float): Total cost of the rocket
        impact_velocity (float): Impact velocity in m/s
        structural_failure (bool): Whether structural failure occurred
        
    Returns:
        tuple: (total_reward, reward_breakdown)
            - total_reward (float): Overall performance score (0-100)
            - reward_breakdown (dict): Detailed breakdown of the reward calculation
    """
    reward = 0.0
    reward_breakdown = {}
    
    # Distance (apogee) reward - linear based on percentage difference
    # Prevent division by zero
    if target_apogee < 1:
        percent_difference = abs(apogee - target_apogee)
    else:
        percent_difference = abs(apogee - target_apogee) / target_apogee
    
    distance_reward = 1.0 - percent_difference
    distance_reward = max(0, distance_reward)
    
    reward += distance_reward
    reward_breakdown["distance_reward"] = distance_reward
    reward_breakdown["apogee_actual"] = apogee
    reward_breakdown["apogee_target"] = target_apogee
    reward_breakdown["percent_difference"] = percent_difference
    
    # Structural failure reward
    structural_failure_reward = 0 if structural_failure else 1
    
    # Horizontal distance reward (linear version)
    max_horz_distance = target_apogee * 0.3  # Scale factor
    horz_distance_reward = max(0, 1 - horizontal_distance / max_horz_distance)
    
    # Cost reward (linear version)
    max_cost = 1000
    cost_reward = max(0, 1 - total_cost / max_cost)
    
    # Impact velocity reward (linear version)
    max_impact_velocity = 50
    impact_reward = max(0, 1 - impact_velocity / max_impact_velocity)
    
    # Add additional rewards with weights
    reward += (horz_distance_reward * 0.2 + 
               cost_reward * 0.3 + 
               impact_reward * 0.3 + 
               structural_failure_reward * 0.2)
    
    # Scale reward to 0-100 range
    max_reward = 2
    
    total_reward = reward / max_reward
    
    # Update reward breakdown
    reward_breakdown.update({
        "horz_distance": horizontal_distance,
        "horz_distance_reward": horz_distance_reward,
        "cost_total": total_cost,
        "cost_reward": cost_reward,
        "impact_velocity": impact_velocity,
        "impact_reward": impact_reward,
        "structural_failure": structural_failure,
        "structural_failure_reward": structural_failure_reward,
        "total_reward": total_reward,
        "message": "Simulation successful" if not structural_failure else "Structural failure detected"
    })
    
    return total_reward, reward_breakdown


def format_reward_report(reward: float, breakdown: Dict[str, Any]) -> str:
    """
    Format the reward calculation as a human-readable report.
    
    Args:
        reward (float): Total reward value
        breakdown (dict): Reward breakdown dictionary
        
    Returns:
        str: Formatted report
    """
    if "error" in breakdown:
        return f"REWARD CALCULATION FAILED: {breakdown['error']}"
    
    report = []
    report.append("="*60)
    report.append(" REWARD CALCULATION ".center(60, "="))
    report.append("="*60)
    
    # Basic stats
    report.append(f"Target Apogee: {breakdown['apogee_target']:.2f} m")
    report.append(f"Actual Apogee: {breakdown['apogee_actual']:.2f} m")
    report.append(f"Error: {breakdown['percent_difference']*100:.2f}%")
    report.append(f"Total Cost: ${breakdown['cost_total']:.2f}")
    
    # Reward breakdown
    report.append("\nReward Components:")
    report.append(f"  Apogee Accuracy: {breakdown['distance_reward']*100:.2f} points")
    report.append(f"  Horizontal Distance: {breakdown['horz_distance_reward']*100:.2f} points")
    report.append(f"  Cost Efficiency: {breakdown['cost_reward']*100:.2f} points")
    report.append(f"  Impact Velocity: {breakdown['impact_reward']*100:.2f} points")
    report.append(f"  Structural Integrity: {breakdown['structural_failure_reward']*100:.2f} points")
    
    # Structural failure note if applicable
    if breakdown["structural_failure"]:
        report.append("\nStructural Failure detected!")
    
    # Final score
    report.append(f"\nTOTAL REWARD SCORE: {reward:.2f} / 100")
    
    if reward >= 90:
        report.append("OUTSTANDING PERFORMANCE!")
    elif reward >= 75:
        report.append("EXCELLENT PERFORMANCE!")
    elif reward >= 60:
        report.append("GOOD PERFORMANCE")
    elif reward >= 40:
        report.append("ACCEPTABLE PERFORMANCE")
    else:
        report.append("NEEDS IMPROVEMENT")
    
    report.append("="*60)
    
    return "\n".join(report)


def calculate_landing_accuracy_reward(
    apogee: float,
    target_apogee: float,
    landing_distance: float,
    target_landing_distance: float = 0,
    total_cost: float = 0,
    impact_velocity: float = 0,
    structural_failure: bool = False
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate a performance reward based on simulation results with focus on landing accuracy.
    
    The reward is calculated based on:
    1. Landing accuracy - how close to the target landing spot
    2. Accuracy in reaching target apogee
    3. Cost-effectiveness of the design
    4. Structural integrity 
    5. Impact velocity
    
    Args:
        apogee (float): Actual apogee reached in meters
        target_apogee (float): Target apogee in meters
        landing_distance (float): Distance from launch site to landing site in meters
        target_landing_distance (float): Target distance for landing in meters
        total_cost (float): Total cost of the rocket
        impact_velocity (float): Impact velocity in m/s
        structural_failure (bool): Whether structural failure occurred
        
    Returns:
        tuple: (total_reward, reward_breakdown)
            - total_reward (float): Overall performance score (0-1.0)
            - reward_breakdown (dict): Detailed breakdown of the reward calculation
    """
    reward = 0.0
    reward_breakdown = {}
    
    # Distance (apogee) reward - linear based on percentage difference
    if target_apogee < 1:
        percent_difference = abs(apogee - target_apogee)
    else:
        percent_difference = abs(apogee - target_apogee) / target_apogee
    
    apogee_reward = 1.0 - min(1.0, percent_difference)
    
    reward_breakdown["apogee_reward"] = apogee_reward
    reward_breakdown["apogee_actual"] = apogee
    reward_breakdown["apogee_target"] = target_apogee
    reward_breakdown["apogee_error"] = percent_difference * 100
    
    # Landing accuracy reward
    landing_difference = abs(landing_distance - target_landing_distance)
    # More precision required for landing - using exponential decay 
    max_landing_error = 100  # meters
    landing_reward = math.exp(-landing_difference / max_landing_error)
    
    reward_breakdown["landing_reward"] = landing_reward
    reward_breakdown["landing_distance"] = landing_distance
    reward_breakdown["target_landing_distance"] = target_landing_distance
    reward_breakdown["landing_error"] = landing_difference
    
    # Structural failure reward
    structural_failure_reward = 0 if structural_failure else 1
    
    # Cost reward (linear version)
    max_cost = 1000
    cost_reward = max(0, 1 - total_cost / max_cost)
    
    # Impact velocity reward (linear version)
    max_impact_velocity = 50
    impact_reward = max(0, 1 - impact_velocity / max_impact_velocity)
    
    # Add rewards with new weights prioritizing landing accuracy
    reward = (landing_reward * 0.4 +      # Landing accuracy is most important
              apogee_reward * 0.2 +       # Reaching target apogee is still important
              cost_reward * 0.1 +         # Cost is less important
              impact_reward * 0.1 +       # Soft landing is less important
              structural_failure_reward * 0.2)  # Structural integrity is still important
    
    # Cap reward at 1.0
    total_reward = min(1.0, reward)
    
    # Update reward breakdown
    reward_breakdown.update({
        "cost_total": total_cost,
        "cost_reward": cost_reward,
        "impact_velocity": impact_velocity,
        "impact_reward": impact_reward,
        "structural_failure": structural_failure,
        "structural_failure_reward": structural_failure_reward,
        "total_reward": total_reward,
        "message": "Simulation successful" if not structural_failure else "Structural failure detected"
    })
    
    return total_reward, reward_breakdown


def format_landing_accuracy_report(reward: float, breakdown: Dict[str, Any]) -> str:
    """
    Format the landing accuracy reward calculation as a human-readable report.
    
    Args:
        reward (float): Total reward value
        breakdown (dict): Reward breakdown dictionary
        
    Returns:
        str: Formatted report
    """
    if "error" in breakdown:
        return f"REWARD CALCULATION FAILED: {breakdown['error']}"
    
    report = []
    report.append("="*60)
    report.append(" LANDING ACCURACY REWARD ".center(60, "="))
    report.append("="*60)
    
    # Basic stats
    report.append(f"Target Apogee: {breakdown['apogee_target']:.2f} m")
    report.append(f"Actual Apogee: {breakdown['apogee_actual']:.2f} m")
    report.append(f"Apogee Error: {breakdown['apogee_error']:.2f}%")
    
    report.append(f"\nTarget Landing Distance: {breakdown['target_landing_distance']:.2f} m")
    report.append(f"Actual Landing Distance: {breakdown['landing_distance']:.2f} m")
    report.append(f"Landing Error: {breakdown['landing_error']:.2f} m")
    
    report.append(f"\nTotal Cost: ${breakdown['cost_total']:.2f}")
    
    # Reward breakdown
    report.append("\nReward Components:")
    report.append(f"  Landing Accuracy (40%): {breakdown['landing_reward']*100:.2f} points")
    report.append(f"  Apogee Accuracy (20%): {breakdown['apogee_reward']*100:.2f} points")
    report.append(f"  Cost Efficiency (10%): {breakdown['cost_reward']*100:.2f} points")
    report.append(f"  Impact Velocity (10%): {breakdown['impact_reward']*100:.2f} points")
    report.append(f"  Structural Integrity (20%): {breakdown['structural_failure_reward']*100:.2f} points")
    
    # Structural failure note if applicable
    if breakdown["structural_failure"]:
        report.append("\nStructural Failure detected!")
    
    # Final score (as percentage)
    reward_percent = reward * 100
    report.append(f"\nTOTAL LANDING ACCURACY SCORE: {reward_percent:.2f} / 100")
    
    if reward_percent >= 90:
        report.append("OUTSTANDING LANDING ACCURACY!")
    elif reward_percent >= 75:
        report.append("EXCELLENT LANDING ACCURACY!")
    elif reward_percent >= 60:
        report.append("GOOD LANDING ACCURACY")
    elif reward_percent >= 40:
        report.append("ACCEPTABLE LANDING ACCURACY")
    else:
        report.append("NEEDS IMPROVEMENT IN LANDING PRECISION")
    
    report.append("="*60)
    
    return "\n".join(report)


def calculate_precise_landing_reward(
    landing_distance: float,
    target_landing_distance: float,
    total_cost: float = 0,
    impact_velocity: float = 0,
    structural_failure: bool = False
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate a performance reward based solely on landing precision.
    
    The reward is calculated based on:
    1. Landing accuracy - how close to the target landing spot
    2. Cost-effectiveness of the design
    3. Structural integrity 
    4. Impact velocity (soft landing)
    
    Args:
        landing_distance (float): Distance from launch site to landing site in meters
        target_landing_distance (float): Target distance for landing in meters
        total_cost (float): Total cost of the rocket
        impact_velocity (float): Impact velocity in m/s
        structural_failure (bool): Whether structural failure occurred
        
    Returns:
        tuple: (total_reward, reward_breakdown)
            - total_reward (float): Overall performance score (0-1.0)
            - reward_breakdown (dict): Detailed breakdown of the reward calculation
    """
    reward = 0.0
    reward_breakdown = {}
    
    # Landing accuracy reward - using Gaussian function for more sensitivity
    landing_difference = abs(landing_distance - target_landing_distance)
    landing_sigma = 50  # Standard deviation for landing accuracy (meters)
    landing_reward = math.exp(-(landing_difference**2) / (2 * landing_sigma**2))
    
    reward_breakdown["landing_reward"] = landing_reward
    reward_breakdown["landing_distance"] = landing_distance
    reward_breakdown["target_landing_distance"] = target_landing_distance
    reward_breakdown["landing_error"] = landing_difference
    
    # Structural failure reward
    structural_failure_reward = 0 if structural_failure else 1
    
    # Cost reward (linear version)
    max_cost = 1000
    cost_reward = max(0, 1 - total_cost / max_cost)
    
    # Impact velocity reward (exponential version - emphasizes soft landings)
    max_impact_velocity = 30
    impact_reward = math.exp(-impact_velocity / max_impact_velocity)
    
    # Add rewards with weights prioritizing landing accuracy
    reward = (landing_reward * 0.6 +          # Landing accuracy is most important
              cost_reward * 0.1 +             # Cost is less important
              impact_reward * 0.1 +           # Soft landing still matters
              structural_failure_reward * 0.2)  # Structural integrity is important
    
    # Cap reward at 1.0
    total_reward = min(1.0, reward)
    
    # Update reward breakdown
    reward_breakdown.update({
        "cost_total": total_cost,
        "cost_reward": cost_reward,
        "impact_velocity": impact_velocity,
        "impact_reward": impact_reward,
        "structural_failure": structural_failure,
        "structural_failure_reward": structural_failure_reward,
        "total_reward": total_reward,
        "message": "Simulation successful" if not structural_failure else "Structural failure detected"
    })
    
    return total_reward, reward_breakdown


def format_precise_landing_report(reward: float, breakdown: Dict[str, Any]) -> str:
    """
    Format the precise landing reward calculation as a human-readable report.
    
    Args:
        reward (float): Total reward value
        breakdown (dict): Reward breakdown dictionary
        
    Returns:
        str: Formatted report
    """
    if "error" in breakdown:
        return f"REWARD CALCULATION FAILED: {breakdown['error']}"
    
    report = []
    report.append("="*60)
    report.append(" PRECISE LANDING REWARD ".center(60, "="))
    report.append("="*60)
    
    # Basic stats
    report.append(f"Target Landing Distance: {breakdown['target_landing_distance']:.2f} m")
    report.append(f"Actual Landing Distance: {breakdown['landing_distance']:.2f} m")
    report.append(f"Landing Error: {breakdown['landing_error']:.2f} m")
    
    report.append(f"\nTotal Cost: ${breakdown['cost_total']:.2f}")
    report.append(f"Impact Velocity: {breakdown['impact_velocity']:.2f} m/s")
    
    # Reward breakdown
    report.append("\nReward Components:")
    report.append(f"  Landing Accuracy (60%): {breakdown['landing_reward']*100:.2f} points")
    report.append(f"  Cost Efficiency (10%): {breakdown['cost_reward']*100:.2f} points")
    report.append(f"  Soft Landing (10%): {breakdown['impact_reward']*100:.2f} points")
    report.append(f"  Structural Integrity (20%): {breakdown['structural_failure_reward']*100:.2f} points")
    
    # Structural failure note if applicable
    if breakdown["structural_failure"]:
        report.append("\nStructural Failure detected!")
    
    # Final score (as percentage)
    reward_percent = reward * 100
    report.append(f"\nTOTAL LANDING PRECISION SCORE: {reward_percent:.2f} / 100")
    
    if reward_percent >= 90:
        report.append("OUTSTANDING LANDING PRECISION!")
    elif reward_percent >= 75:
        report.append("EXCELLENT LANDING PRECISION!")
    elif reward_percent >= 60:
        report.append("GOOD LANDING PRECISION")
    elif reward_percent >= 40:
        report.append("ACCEPTABLE LANDING PRECISION")
    else:
        report.append("NEEDS IMPROVEMENT IN LANDING PRECISION")
    
    report.append("="*60)
    
    return "\n".join(report)


def calculate_bullseye_landing_reward(
    landing_x: float,
    landing_y: float,
    target_x: float,
    target_y: float,
    total_cost: float = 0,
    impact_velocity: float = 0,
    structural_failure: bool = False
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate a performance reward based on landing precision to an exact target point.
    
    The reward is calculated based on:
    1. Bullseye accuracy - how close to the exact target landing coordinates
    2. Cost-effectiveness of the design
    3. Structural integrity 
    4. Impact velocity (soft landing)
    
    Args:
        landing_x (float): X-coordinate of landing point
        landing_y (float): Y-coordinate of landing point
        target_x (float): X-coordinate of target landing point
        target_y (float): Y-coordinate of target landing point
        total_cost (float): Total cost of the rocket
        impact_velocity (float): Impact velocity in m/s
        structural_failure (bool): Whether structural failure occurred
        
    Returns:
        tuple: (total_reward, reward_breakdown)
            - total_reward (float): Overall performance score (0-1.0)
            - reward_breakdown (dict): Detailed breakdown of the reward calculation
    """
    reward = 0.0
    reward_breakdown = {}
    
    # Calculate 2D distance from target (Euclidean distance)
    landing_error = math.sqrt((landing_x - target_x)**2 + (landing_y - target_y)**2)
    
    # Landing accuracy reward - using Gaussian function for sensitivity to precision
    # Smaller sigma = tighter precision requirements
    landing_sigma = 25  # Standard deviation for landing accuracy (meters)
    landing_reward = math.exp(-(landing_error**2) / (2 * landing_sigma**2))
    
    # Store info in breakdown
    reward_breakdown["landing_reward"] = landing_reward
    reward_breakdown["landing_x"] = landing_x
    reward_breakdown["landing_y"] = landing_y
    reward_breakdown["target_x"] = target_x
    reward_breakdown["target_y"] = target_y
    reward_breakdown["landing_error"] = landing_error
    
    # Structural failure reward
    structural_failure_reward = 0 if structural_failure else 1
    
    # Cost reward (linear version)
    max_cost = 1000
    cost_reward = max(0, 1 - total_cost / max_cost)
    
    # Impact velocity reward (exponential version - emphasizes soft landings)
    max_impact_velocity = 10
    impact_reward = math.exp(-impact_velocity / max_impact_velocity)
    
    # Add rewards with weights prioritizing landing accuracy
    reward = (landing_reward * 0.7 +          # Landing accuracy is most important
              cost_reward * 0.05 +            # Cost is less important for precision landing
              impact_reward * 0.05 +          # Soft landing still matters
              structural_failure_reward * 0.2)  # Structural integrity is important
    
    # Cap reward at 1.0
    total_reward = min(1.0, reward)
    
    # Update reward breakdown
    reward_breakdown.update({
        "cost_total": total_cost,
        "cost_reward": cost_reward,
        "impact_velocity": impact_velocity,
        "impact_reward": impact_reward,
        "structural_failure": structural_failure,
        "structural_failure_reward": structural_failure_reward,
        "total_reward": total_reward,
        "message": "Simulation successful" if not structural_failure else "Structural failure detected"
    })
    
    return total_reward, reward_breakdown


def format_bullseye_landing_report(reward: float, breakdown: Dict[str, Any]) -> str:
    """
    Format the bullseye landing reward calculation as a human-readable report.
    
    Args:
        reward (float): Total reward value
        breakdown (dict): Reward breakdown dictionary
        
    Returns:
        str: Formatted report
    """
    if "error" in breakdown:
        return f"REWARD CALCULATION FAILED: {breakdown['error']}"
    
    report = []
    report.append("="*60)
    report.append(" BULLSEYE LANDING REWARD ".center(60, "="))
    report.append("="*60)
    
    # Basic stats
    report.append(f"Target Landing Position: ({breakdown['target_x']:.2f}m, {breakdown['target_y']:.2f}m)")
    report.append(f"Actual Landing Position: ({breakdown['landing_x']:.2f}m, {breakdown['landing_y']:.2f}m)")
    report.append(f"Landing Error: {breakdown['landing_error']:.2f}m")
    
    # Success indicators
    if breakdown['landing_error'] < 10:
        report.append("\n🎯 BULLSEYE! Within 10m of target")
    elif breakdown['landing_error'] < 25:
        report.append("\n🎯 Very close! Within 25m of target")
    elif breakdown['landing_error'] < 50:
        report.append("\n👍 Good landing, within 50m of target")
    
    report.append(f"\nTotal Cost: ${breakdown['cost_total']:.2f}")
    report.append(f"Impact Velocity: {breakdown['impact_velocity']:.2f} m/s")
    
    # Reward breakdown
    report.append("\nReward Components:")
    report.append(f"  Landing Accuracy (70%): {breakdown['landing_reward']*100:.2f} points")
    report.append(f"  Cost Efficiency (5%): {breakdown['cost_reward']*100:.2f} points")
    report.append(f"  Soft Landing (5%): {breakdown['impact_reward']*100:.2f} points")
    report.append(f"  Structural Integrity (20%): {breakdown['structural_failure_reward']*100:.2f} points")
    
    # Structural failure note if applicable
    if breakdown["structural_failure"]:
        report.append("\n⚠️ Structural Failure detected!")
    
    # Final score (as percentage)
    reward_percent = reward * 100
    report.append(f"\nTOTAL BULLSEYE SCORE: {reward_percent:.2f} / 100")
    
    if reward_percent >= 90:
        report.append("OUTSTANDING PRECISION!")
    elif reward_percent >= 75:
        report.append("EXCELLENT PRECISION!")
    elif reward_percent >= 60:
        report.append("GOOD PRECISION")
    elif reward_percent >= 40:
        report.append("ACCEPTABLE PRECISION")
    else:
        report.append("NEEDS IMPROVEMENT IN TARGETING PRECISION")
    
    report.append("="*60)
    
    return "\n".join(report)


def calculate_target_point_reward(
    landing_x: float,
    landing_y: float,
    target_x: float,
    target_y: float,
    difficulty_factor: float = 1.0,  # Higher = tighter precision required
    total_cost: float = 0,
    impact_velocity: float = 0,
    structural_failure: bool = False
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate a performance reward based on hitting an exact target landing point.
    
    The reward is calculated using a Gaussian function centered on the target point,
    with precision requirements that scale with the difficulty factor.
    
    Args:
        landing_x (float): X-coordinate of landing point
        landing_y (float): Y-coordinate of landing point
        target_x (float): X-coordinate of target landing point
        target_y (float): Y-coordinate of target landing point
        difficulty_factor (float): Controls how precise the landing must be (1.0=standard, 2.0=twice as demanding)
        total_cost (float): Total cost of the rocket
        impact_velocity (float): Impact velocity in m/s
        structural_failure (bool): Whether structural failure occurred
        
    Returns:
        tuple: (total_reward, reward_breakdown)
            - total_reward (float): Overall performance score (0-1.0)
            - reward_breakdown (dict): Detailed breakdown of the reward calculation
    """
    reward = 0.0
    reward_breakdown = {}
    
    # Calculate 2D distance from target (Euclidean distance)
    landing_error = math.sqrt((landing_x - target_x)**2 + (landing_y - target_y)**2)
    
    # Set the standard deviation (sigma) based on difficulty
    # Higher difficulty = smaller sigma = tighter landing requirements
    base_sigma = 25.0  # meters (standard)
    sigma = base_sigma / difficulty_factor
    
    # Calculate landing reward using Gaussian function
    # This rewards landing closer to the target with rapidly diminishing returns as distance increases
    landing_reward = math.exp(-(landing_error**2) / (2 * sigma**2))
    
    # Store info in breakdown
    reward_breakdown["landing_reward"] = landing_reward
    reward_breakdown["landing_x"] = landing_x
    reward_breakdown["landing_y"] = landing_y
    reward_breakdown["target_x"] = target_x
    reward_breakdown["target_y"] = target_y
    reward_breakdown["landing_error"] = landing_error
    reward_breakdown["precision_requirement"] = sigma
    reward_breakdown["difficulty_factor"] = difficulty_factor
    
    # Structural failure reward
    structural_failure_reward = 0 if structural_failure else 1
    
    # Cost reward (with exponential scaling to reward efficiency more)
    max_cost = 1000
    cost_factor = total_cost / max_cost
    cost_reward = math.exp(-1.5 * cost_factor) if cost_factor < 1.0 else 0
    
    # Impact velocity reward (soft landing reward - exponential)
    max_impact_velocity = 25  # m/s
    impact_factor = impact_velocity / max_impact_velocity
    impact_reward = math.exp(-1.5 * impact_factor) if impact_factor < 1.0 else 0
    
    # Add rewards with weights prioritizing landing accuracy
    reward = (landing_reward * 0.75 +         # Landing accuracy is most important
              cost_reward * 0.05 +            # Cost is less important
              impact_reward * 0.05 +          # Soft landing still matters
              structural_failure_reward * 0.15)  # Structural integrity is important
    
    # Cap reward at 1.0
    total_reward = min(1.0, reward)
    
    # Calculate bullseye classifications for reporting
    bullseye_class = "MISS"
    if landing_error < 5:
        bullseye_class = "PERFECT BULLSEYE"
    elif landing_error < 10:
        bullseye_class = "BULLSEYE"
    elif landing_error < 25:
        bullseye_class = "INNER RING"
    elif landing_error < 50:
        bullseye_class = "OUTER RING"
    
    # Update reward breakdown
    reward_breakdown.update({
        "bullseye_class": bullseye_class,
        "cost_total": total_cost,
        "cost_reward": cost_reward,
        "impact_velocity": impact_velocity,
        "impact_reward": impact_reward,
        "structural_failure": structural_failure,
        "structural_failure_reward": structural_failure_reward,
        "total_reward": total_reward,
        "message": f"{bullseye_class}: {landing_error:.2f}m from target" 
                   if not structural_failure else "Structural failure detected"
    })
    
    return total_reward, reward_breakdown


def format_target_point_report(reward: float, breakdown: Dict[str, Any]) -> str:
    """
    Format the target point reward calculation as a human-readable report.
    
    Args:
        reward (float): Total reward value
        breakdown (dict): Reward breakdown dictionary
        
    Returns:
        str: Formatted report
    """
    if "error" in breakdown:
        return f"REWARD CALCULATION FAILED: {breakdown['error']}"
    
    report = []
    report.append("="*60)
    report.append(" TARGET LANDING REWARD ".center(60, "="))
    report.append("="*60)
    
    # Landing classification
    bullseye_class = breakdown["bullseye_class"]
    if bullseye_class == "PERFECT BULLSEYE":
        report.append("🎯🎯 PERFECT BULLSEYE! 🎯🎯")
    elif bullseye_class == "BULLSEYE":
        report.append("🎯 BULLSEYE! 🎯")
    elif bullseye_class == "INNER RING":
        report.append("👌 INNER RING")
    elif bullseye_class == "OUTER RING":
        report.append("👍 OUTER RING")
    else:
        report.append("❌ MISSED TARGET")
    
    # Basic stats
    report.append(f"\nTarget Position: ({breakdown['target_x']:.2f}m, {breakdown['target_y']:.2f}m)")
    report.append(f"Landing Position: ({breakdown['landing_x']:.2f}m, {breakdown['landing_y']:.2f}m)")
    report.append(f"Landing Error: {breakdown['landing_error']:.2f}m")
    report.append(f"Precision Requirement: ±{breakdown['precision_requirement']:.2f}m")
    report.append(f"Difficulty Factor: {breakdown['difficulty_factor']:.1f}x")
    
    report.append(f"\nTotal Cost: ${breakdown['cost_total']:.2f}")
    report.append(f"Impact Velocity: {breakdown['impact_velocity']:.2f} m/s")
    
    # Structural status
    if breakdown["structural_failure"]:
        report.append("\n⚠️ STRUCTURAL FAILURE DETECTED!")
    else:
        report.append("\n✅ Structural integrity maintained")
    
    # Reward breakdown
    report.append("\nReward Components:")
    report.append(f"  Target Accuracy (75%): {breakdown['landing_reward']*100:.2f} points")
    report.append(f"  Cost Efficiency (5%): {breakdown['cost_reward']*100:.2f} points")
    report.append(f"  Soft Landing (5%): {breakdown['impact_reward']*100:.2f} points")
    report.append(f"  Structural Integrity (15%): {breakdown['structural_failure_reward']*100:.2f} points")
    
    # Final score (as percentage)
    reward_percent = reward * 100
    report.append(f"\nTOTAL TARGET SCORE: {reward_percent:.2f} / 100")
    
    if reward_percent >= 90:
        report.append("PERFECT PRECISION LANDING!")
    elif reward_percent >= 75:
        report.append("EXCELLENT PRECISION!")
    elif reward_percent >= 60:
        report.append("GOOD PRECISION")
    elif reward_percent >= 40:
        report.append("ACCEPTABLE PRECISION")
    else:
        report.append("NEEDS IMPROVEMENT")
    
    report.append("="*60)
    
    return "\n".join(report)


def calculate_dynamic_bullseye_reward(
    landing_x: float,
    landing_y: float,
    target_x: float,
    target_y: float,
    total_cost: float = 0,
    impact_velocity: float = 0,
    structural_failure: bool = False
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate a performance reward based on landing precision with dynamic difficulty.
    
    The reward is calculated with:
    1. Dynamic precision requirements based on target distance
    2. Linear impact velocity reward with cutoff
    3. Cost-effectiveness
    4. Structural integrity
    
    Args:
        landing_x (float): X-coordinate of landing point
        landing_y (float): Y-coordinate of landing point
        target_x (float): X-coordinate of target landing point
        target_y (float): Y-coordinate of target landing point
        total_cost (float): Total cost of the rocket
        impact_velocity (float): Impact velocity in m/s
        structural_failure (bool): Whether structural failure occurred
        
    Returns:
        tuple: (total_reward, reward_breakdown)
            - total_reward (float): Overall performance score (0-1.0)
            - reward_breakdown (dict): Detailed breakdown of the reward calculation
    """
    reward = 0.0
    reward_breakdown = {}
    
    # Calculate target distance from origin
    target_distance_from_origin = math.sqrt(target_x**2 + target_y**2)
    
    # Calculate 2D distance from target (Euclidean distance)
    landing_error = math.sqrt((landing_x - target_x)**2 + (landing_y - target_y)**2)
    
    # Dynamic sigma - 20% of the target distance from origin
    # With a minimum to prevent division by zero
    min_sigma = 5.0  # meters
    landing_sigma = max(min_sigma, 0.2 * target_distance_from_origin)
    
    # Calculate landing reward using Gaussian function
    landing_reward = math.exp(-(landing_error**2) / (2 * landing_sigma**2))
    
    # Store info in breakdown
    reward_breakdown["landing_reward"] = landing_reward
    reward_breakdown["landing_x"] = landing_x
    reward_breakdown["landing_y"] = landing_y
    reward_breakdown["target_x"] = target_x
    reward_breakdown["target_y"] = target_y
    reward_breakdown["target_distance_from_origin"] = target_distance_from_origin
    reward_breakdown["landing_error"] = landing_error
    reward_breakdown["landing_sigma"] = landing_sigma
    
    # Structural failure reward
    structural_failure_reward = 0 if structural_failure else 1
    
    # Cost reward (linear version)
    max_cost = 1000
    cost_reward = max(0, 1 - total_cost / max_cost)
    
    # Impact velocity reward (linear with cutoff)
    max_impact_velocity = 30
    impact_reward = 0 if impact_velocity > max_impact_velocity else max(0, 1 - impact_velocity / max_impact_velocity)
    
    # Add rewards with weights prioritizing landing accuracy
    reward = (landing_reward * 0.7 +          # Landing accuracy is most important
              cost_reward * 0.05 +            # Cost is less important for precision landing
              impact_reward * 0.05 +          # Soft landing still matters
              structural_failure_reward * 0.2)  # Structural integrity is important
    
    # Cap reward at 1.0
    total_reward = min(1.0, reward)
    
    # Calculate bullseye classifications for reporting
    # Using the landing_sigma as a reference
    bullseye_class = "MISS"
    if landing_error < landing_sigma * 0.2:
        bullseye_class = "PERFECT BULLSEYE"
    elif landing_error < landing_sigma * 0.4:
        bullseye_class = "BULLSEYE"
    elif landing_error < landing_sigma * 0.8:
        bullseye_class = "INNER RING"
    elif landing_error < landing_sigma * 1.5:
        bullseye_class = "OUTER RING"
    
    # Update reward breakdown
    reward_breakdown.update({
        "bullseye_class": bullseye_class,
        "cost_total": total_cost,
        "cost_reward": cost_reward,
        "impact_velocity": impact_velocity,
        "impact_reward": impact_reward,
        "structural_failure": structural_failure,
        "structural_failure_reward": structural_failure_reward,
        "total_reward": total_reward,
        "message": f"{bullseye_class}: {landing_error:.2f}m from target" 
                   if not structural_failure else "Structural failure detected"
    })
    
    return total_reward, reward_breakdown


def format_dynamic_bullseye_report(reward: float, breakdown: Dict[str, Any]) -> str:
    """
    Format the dynamic bullseye reward calculation as a human-readable report.
    
    Args:
        reward (float): Total reward value
        breakdown (dict): Reward breakdown dictionary
        
    Returns:
        str: Formatted report
    """
    if "error" in breakdown:
        return f"REWARD CALCULATION FAILED: {breakdown['error']}"
    
    report = []
    report.append("="*60)
    report.append(" DYNAMIC BULLSEYE REWARD ".center(60, "="))
    report.append("="*60)
    
    # Landing classification
    bullseye_class = breakdown["bullseye_class"]
    if bullseye_class == "PERFECT BULLSEYE":
        report.append("🎯🎯 PERFECT BULLSEYE! 🎯🎯")
    elif bullseye_class == "BULLSEYE":
        report.append("🎯 BULLSEYE! 🎯")
    elif bullseye_class == "INNER RING":
        report.append("👌 INNER RING")
    elif bullseye_class == "OUTER RING":
        report.append("👍 OUTER RING")
    else:
        report.append("❌ MISSED TARGET")
    
    # Basic stats
    report.append(f"\nTarget Position: ({breakdown['target_x']:.2f}m, {breakdown['target_y']:.2f}m)")
    report.append(f"Target Distance from Origin: {breakdown['target_distance_from_origin']:.2f}m")
    report.append(f"Landing Position: ({breakdown['landing_x']:.2f}m, {breakdown['landing_y']:.2f}m)")
    report.append(f"Landing Error: {breakdown['landing_error']:.2f}m")
    report.append(f"Dynamic Precision (sigma): {breakdown['landing_sigma']:.2f}m")
    
    report.append(f"\nTotal Cost: ${breakdown['cost_total']:.2f}")
    report.append(f"Impact Velocity: {breakdown['impact_velocity']:.2f} m/s")
    
    # Structural status
    if breakdown["structural_failure"]:
        report.append("\n⚠️ STRUCTURAL FAILURE DETECTED!")
    else:
        report.append("\n✅ Structural integrity maintained")
    
    # Reward breakdown
    report.append("\nReward Components:")
    report.append(f"  Landing Accuracy (70%): {breakdown['landing_reward']*100:.2f} points")
    report.append(f"  Cost Efficiency (5%): {breakdown['cost_reward']*100:.2f} points")
    report.append(f"  Safe Landing Speed (5%): {breakdown['impact_reward']*100:.2f} points")
    report.append(f"  Structural Integrity (20%): {breakdown['structural_failure_reward']*100:.2f} points")
    
    # Final score (as percentage)
    reward_percent = reward * 100
    report.append(f"\nTOTAL BULLSEYE SCORE: {reward_percent:.2f} / 100")
    
    if reward_percent >= 90:
        report.append("OUTSTANDING PRECISION!")
    elif reward_percent >= 75:
        report.append("EXCELLENT PRECISION!")
    elif reward_percent >= 60:
        report.append("GOOD PRECISION")
    elif reward_percent >= 40:
        report.append("ACCEPTABLE PRECISION")
    else:
        report.append("NEEDS IMPROVEMENT IN TARGETING PRECISION")
    
    report.append("="*60)
    
    return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Calculate rewards from simulation results")
    parser.add_argument("--results-file", type=str, help="JSON file with simulation results")
    parser.add_argument("--target-apogee", type=float, required=True, help="Target apogee in meters")
    parser.add_argument("--apogee-weight", type=float, default=0.7, help="Weight for apogee accuracy")
    parser.add_argument("--cost-weight", type=float, default=0.3, help="Weight for cost efficiency")
    parser.add_argument("--structural-penalty", type=float, default=0.5, help="Penalty for structural failure")
    parser.add_argument("--output", type=str, help="Output file for reward report")
    
    args = parser.parse_args()
    
    # Load results
    with open(args.results_file, 'r') as f:
        results = json.load(f)
    
    # Calculate reward
    reward, breakdown = calculate_landing_accuracy_reward(
        apogee=results["simple_results"]["apogee"],
        target_apogee=args.target_apogee,
        landing_distance=results["simple_results"].get("horizontal_distance", 0),
        target_landing_distance=500,  # Set your desired target landing distance
        total_cost=results["simple_results"].get("total_cost", 0),
        impact_velocity=results["full_results"].get('flight', {}).get('impact_velocity', 0),
        structural_failure=results["simple_results"].get("structural_failure", False)
    )
    
    # Generate report
    report = format_landing_accuracy_report(reward, breakdown)
    
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Reward report saved to {args.output}")
    else:
        print(report)
    
    print(f"\nReward score: {reward:.2f} / 100") 