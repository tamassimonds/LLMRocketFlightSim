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
    max_cost = 1000.0  # Base cost scale
    cost_factor = total_cost / max_cost
    cost_reward = 1.0 - cost_factor
    cost_reward = max(0, cost_reward)  # Clamp to minimum of 0
    
    # Impact velocity reward (linear version)
    max_impact_velocity = 25  # m/s
    impact_factor = abs(impact_velocity) / max_impact_velocity
    impact_reward = 1.0 - impact_factor
    impact_reward = max(0, impact_reward)  # Clamp to minimum of 0
    
    # Add additional rewards with weights
    reward = (distance_reward*0.5 +
              horz_distance_reward * 0.1 + 
               cost_reward * 0.15 + 
               impact_reward * 0.15 + 
               structural_failure_reward * 0.1)

    
    
    # Update reward breakdown
    reward_breakdown.update({
        
        "distance_reward": distance_reward,
        "horz_distance": horizontal_distance,
        "horz_distance_reward": horz_distance_reward,
        "cost_total": total_cost,
        "cost_reward": cost_reward,
        "impact_velocity": impact_velocity,
        "impact_reward": impact_reward,
        "structural_failure": structural_failure,
        "structural_failure_reward": structural_failure_reward,
        "total_reward": reward,
        "message": "Simulation successful" if not structural_failure else "Structural failure detected"
    })
    print(reward_breakdown)
    return reward, reward_breakdown


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
    target_distance = math.sqrt(target_x**2 + target_y**2)
    
    # Landing accuracy reward - using Gaussian function for sensitivity to precision
    # Smaller sigma = tighter precision requirements
    landing_sigma = 0.2 * target_distance  # 20% of distance to target
    landing_reward = math.exp(-0.5 * (landing_error / landing_sigma)**2)
    
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
    max_cost = 1000.0  # Base cost scale
    cost_factor = total_cost / max_cost
    cost_reward = 1.0 - cost_factor
    cost_reward = max(0, cost_reward)  # Clamp to minimum of 0
    
    # Impact velocity reward (linear version)
    max_impact_velocity = 25  # m/s
    impact_factor = abs(impact_velocity) / max_impact_velocity
    impact_reward = 1.0 - impact_factor
    impact_reward = max(0, impact_reward)  # Clamp to minimum of 0
    
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
    target_distance = math.sqrt(target_x**2 + target_y**2)  # Distance from origin to target
    landing_reward = 1.0 - (landing_error / target_distance)
    landing_reward = max(0, landing_reward)  # Clamp to minimum of 0
    
    # Store info in breakdown
    reward_breakdown["landing_reward"] = landing_reward
    reward_breakdown["landing_x"] = landing_x
    reward_breakdown["landing_y"] = landing_y
    reward_breakdown["target_x"] = target_x
    reward_breakdown["target_y"] = target_y
    reward_breakdown["landing_error"] = landing_error
    reward_breakdown["precision_requirement"] = 0
    reward_breakdown["difficulty_factor"] = difficulty_factor
    
    # Structural failure reward
    structural_failure_reward = 0 if structural_failure else 1
    
    # Cost reward (with exponential scaling to reward efficiency more)
    max_cost = 1000.0  # Base cost scale
    cost_factor = total_cost / max_cost
    cost_reward = 1.0 - cost_factor
    cost_reward = max(0, cost_reward)  # Clamp to minimum of 0
    
    # Impact velocity reward (soft landing reward - exponential)
    max_impact_velocity = 25  # m/s
    impact_factor = abs(impact_velocity) / max_impact_velocity
    impact_reward = 1.0 - impact_factor
    impact_reward = max(0, impact_reward)
    
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


def calculate_complex_bullseye_reward(
    landing_x: float,
    landing_y: float,
    target_x: float,
    target_y: float,
    actual_apogee: float,
    target_apogee: float,
    total_cost: float,
    impact_velocity: float,
    structural_failure: bool
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate a complex reward that considers both precision landing and apogee targeting.
    
    Args:
        landing_x, landing_y: Actual landing coordinates (meters)
        target_x, target_y: Target landing coordinates (meters)
        actual_apogee: Achieved maximum altitude (meters)
        target_apogee: Desired maximum altitude (meters)
        total_cost: Total cost of the rocket (USD)
        impact_velocity: Landing velocity (m/s)
        structural_failure: Whether the rocket structure failed
        
    Returns:
        Tuple of (total_reward, reward_breakdown)
    """
    reward_breakdown = {}
    
    # Landing accuracy (50% of total score)
    landing_error = math.sqrt((landing_x - target_x)**2 + (landing_y - target_y)**2)
    target_distance = math.sqrt(target_x**2 + target_y**2)  # Distance from origin to target

    # Linear reward that scales with distance to target
    landing_error_percent = landing_error / target_distance
    landing_reward = 1.0 - landing_error_percent
    landing_reward = max(0, landing_reward)  # Clamp to minimum of 0

    # Classify landing accuracy (keep this part)
    if landing_error <= 10:
        bullseye_class = "BULLSEYE"
    elif landing_error <= 25:
        bullseye_class = "EXCELLENT"
    elif landing_error <= 50:
        bullseye_class = "GOOD"
    elif landing_error <= 100:
        bullseye_class = "FAIR"
    else:
        bullseye_class = "MISS"
    
    # Apogee accuracy (35% of total score)
    if target_apogee < 1:
        apogee_error_percent = abs(actual_apogee - target_apogee)
    else:
        apogee_error_percent = abs(actual_apogee - target_apogee) / target_apogee

    apogee_reward = 1.0 - apogee_error_percent
    apogee_reward = max(0, apogee_reward)  # Clamp to minimum of 0

    # Cost efficiency (10% of total score)
    max_cost = 1000.0  # Base cost scale
    cost_factor = total_cost / max_cost
    cost_reward = 1.0 - cost_factor
    cost_reward = max(0, cost_reward)  # Clamp to minimum of 0
    
    # Safety (20% of total score)
    if structural_failure:
        safety_reward = 0.0
    else:
        # Impact velocity component
        safe_velocity = 10.0  # m/s
        velocity_reward = math.exp(-0.5 * ((impact_velocity - safe_velocity) / 5)**2)
        safety_reward = velocity_reward
    
    # Calculate weighted total reward
    total_reward = (
        0.85 * landing_reward +    # Landing accuracy
        # 0.35 * apogee_reward +     # Apogee accuracy
        0.10 * cost_reward +       # Cost efficiency
        0.05 * safety_reward       # Safety
    )
    
    # Build reward breakdown dictionary
    reward_breakdown = {
        "landing_error": landing_error,
        "landing_reward": landing_reward,
        "landing_error_percent": landing_error_percent * 100,  # Convert to percentage for reporting
        "apogee_error_percent": apogee_error_percent * 100,  # Convert to percentage for reporting
        "apogee_reward": apogee_reward,
        "cost_reward": cost_reward,
        "safety_reward": safety_reward,
        "impact_velocity": impact_velocity,
        "structural_failure": structural_failure,
        "total_cost": total_cost,
        "bullseye_class": bullseye_class,
        "weights": {
            "landing": 0.50,
            "apogee": 0.35,
            "cost": 0.10,
            "safety": 0.05
        }
    }
    
    return total_reward, reward_breakdown

def format_complex_bullseye_report(reward: float, breakdown: Dict[str, Any]) -> str:
    """Format a detailed report of the complex bullseye reward calculation."""
    report = [
        "=== COMPLEX BULLSEYE LANDING REPORT ===",
        f"Total Score: {reward * 100:.2f}/100",
        "",
        "Landing Accuracy:",
        f"  • Error: {breakdown['landing_error']:.2f}m",
        f"  • Class: {breakdown['bullseye_class']}",
        f"  • Score: {breakdown['landing_reward'] * 100:.2f}/100",
        "",
        "Apogee Targeting:",
        f"  • Error: {breakdown['apogee_error_percent']:.2f}%",
        f"  • Score: {breakdown['apogee_reward'] * 100:.2f}/100",
        "",
        "Cost Efficiency:",
        f"  • Total Cost: ${breakdown['total_cost']:.2f}",
        f"  • Score: {breakdown['cost_reward'] * 100:.2f}/100",
        "",
        "Safety:",
        f"  • Impact Velocity: {breakdown['impact_velocity']:.2f} m/s",
        f"  • Structural Integrity: {'FAILED' if breakdown['structural_failure'] else 'PASSED'}",
        f"  • Score: {breakdown['safety_reward'] * 100:.2f}/100",
    ]
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
    
   
   
    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Reward report saved to {args.output}")
    else:
        print(report)
    
    print(f"\nReward score: {reward:.2f} / 100") 