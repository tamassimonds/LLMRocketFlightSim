"""
Utility for calculating performance rewards based on rocket simulation results.
"""

from typing import Dict, Any, Optional, Union, Tuple


def calculate_reward(
    results: Dict[str, Any],
    target_apogee: float,
    apogee_weight: float = 0.7,
    cost_weight: float = 0.3,
    structural_penalty: float = 0.5
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate a performance reward based on simulation results.
    
    The reward is calculated based on:
    1. Accuracy in reaching target apogee
    2. Cost-effectiveness of the design
    3. Structural integrity
    
    Args:
        results (dict): Simulation results from rocket_designer.py
        target_apogee (float): Target apogee in meters
        apogee_weight (float): Weight for apogee accuracy in total score (0-1)
        cost_weight (float): Weight for cost optimization in total score (0-1)
        structural_penalty (float): Penalty factor for structural failure (0-1)
        
    Returns:
        tuple: (total_reward, reward_breakdown)
            - total_reward (float): Overall performance score (0-100)
            - reward_breakdown (dict): Detailed breakdown of the reward calculation
    """
    # Initialize reward components
    apogee_reward = 0.0
    cost_reward = 0.0
    
    # Check if simulation was successful
    if "error" in results:
        return 0.0, {
            "error": results["error"],
            "apogee_reward": 0.0,
            "cost_reward": 0.0,
            "structural_penalty": 0.0,
            "total_reward": 0.0,
            "message": "Simulation failed"
        }
    
    simple_results = results["simple_results"]
    
    # Calculate apogee accuracy reward
    actual_apogee = simple_results["apogee"]
    apogee_error_percent = simple_results["apogee_error_percent"]
    
    # Apogee reward: 100 points for perfect match, decreasing as error increases
    # Uses an exponential decay function for smoother falloff
    apogee_reward = 100 * (2 ** (-apogee_error_percent / 20))
    # Cap at 100
    apogee_reward = min(apogee_reward, 100)
    
    # Calculate cost reward
    # Assume a reasonable cost range based on target apogee
    # Higher apogees allow for higher costs
    estimated_reasonable_cost = 50 + (target_apogee / 100)  # Base heuristic
    
    total_cost = simple_results["total_cost"]
    
    # Cost reward: 100 points at 50% of reasonable cost, 50 points at reasonable cost
    # 0 points at 2x reasonable cost or higher
    if total_cost <= estimated_reasonable_cost * 0.5:
        cost_reward = 100
    elif total_cost <= estimated_reasonable_cost:
        cost_reward = 50 + 50 * ((estimated_reasonable_cost - total_cost) / (estimated_reasonable_cost * 0.5))
    elif total_cost <= estimated_reasonable_cost * 2:
        cost_reward = 50 * ((estimated_reasonable_cost * 2 - total_cost) / estimated_reasonable_cost)
    else:
        cost_reward = 0
    
    # Apply structural failure penalty if applicable
    structural_failure = simple_results["structural_failure"]
    penalty_factor = 1.0
    
    if structural_failure:
        penalty_factor = 1.0 - structural_penalty
    
    # Calculate weighted total reward
    total_reward = ((apogee_weight * apogee_reward) + 
                    (cost_weight * cost_reward)) * penalty_factor
    
    # Compile reward breakdown
    reward_breakdown = {
        "apogee_target": target_apogee,
        "apogee_actual": actual_apogee,
        "apogee_error_percent": apogee_error_percent,
        "apogee_reward": apogee_reward,
        "apogee_weight": apogee_weight,
        
        "cost_total": total_cost,
        "cost_reasonable_estimate": estimated_reasonable_cost,
        "cost_reward": cost_reward,
        "cost_weight": cost_weight,
        
        "structural_failure": structural_failure,
        "structural_penalty": structural_penalty if structural_failure else 0.0,
        "penalty_factor": penalty_factor,
        
        "total_reward": total_reward,
        "message": "Simulation successful"
    }
    
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
    report.append("=== REWARD CALCULATION ===")
    
    # Basic stats
    report.append(f"Target Apogee: {breakdown['apogee_target']:.2f} m")
    report.append(f"Actual Apogee: {breakdown['apogee_actual']:.2f} m")
    report.append(f"Error: {breakdown['apogee_error_percent']:.2f}%")
    report.append(f"Total Cost: ${breakdown['cost_total']:.2f}")
    
    # Reward breakdown
    report.append("\nReward Components:")
    report.append(f"  Apogee Accuracy: {breakdown['apogee_reward']:.2f} points (weight: {breakdown['apogee_weight']:.2f})")
    report.append(f"  Cost Efficiency: {breakdown['cost_reward']:.2f} points (weight: {breakdown['cost_weight']:.2f})")
    
    # Structural penalty if applicable
    if breakdown["structural_failure"]:
        report.append(f"\nStructural Failure Penalty: {breakdown['structural_penalty'] * 100:.0f}%")
    
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
    
    report.append("==========================")
    
    return "\n".join(report)