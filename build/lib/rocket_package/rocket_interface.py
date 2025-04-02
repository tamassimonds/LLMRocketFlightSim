#!/usr/bin/env python3
"""
Rocket Interface - A simple interface for processing LLM responses, running simulations,
and calculating rewards.

This script provides a fault-tolerant way to:
1. Process raw LLM responses
2. Extract configuration from the response
3. Run a simulation with the configuration
4. Calculate and return rewards based on performance

Usage:
  from rocket_interface import process_llm_response
  result = process_llm_response(llm_response, target_apogee=100)
"""

import os
import sys
import json
import asyncio
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Import required modules with error handling
try:
    # Import for configuration extraction
    from.src.utils.model_parser import (
        extract_config_from_response,
        add_wind_settings,
        save_model_outputs
    )
    
    # Import for design rule check
    from.src.utils.design_rule_check import check_rocket_configuration
    
    # Import for simulation
    from.src.models.simulation import RocketSimulation
    
    # Import for reward calculation from existing module
    from.src.utils.reward import calculate_reward, format_reward_report
    
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you are running this script from the project root directory")
    sys.exit(1)


# Custom JSON encoder to handle tuples
class TupleEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, tuple):
            return list(obj)
        return super().default(obj)


async def simulate_from_config(
    config: Dict[str, Any],
    target_apogee: float,
    output_dir: str = "outputs",
    wind_speed: float = 0,
    wind_direction: str = "N",
    skip_drc: bool = False,
    save_outputs: bool = True
) -> Dict[str, Any]:
    """
    Run a simulation from a rocket configuration.
    
    Args:
        config (dict): Rocket configuration
        target_apogee (float): Target apogee in meters
        output_dir (str): Directory for saving outputs
        wind_speed (float): Wind speed in m/s
        wind_direction (str): Wind direction
        skip_drc (bool): Whether to skip the Design Rule Check
        save_outputs (bool): Whether to save simulation outputs
        
    Returns:
        dict: Simulation results and reward information
    """
    try:
        # Add wind settings to configuration
        config = add_wind_settings(config, wind_speed, wind_direction)
        
        # Save configuration if requested
        if save_outputs:
            os.makedirs(output_dir, exist_ok=True)
            config_path = os.path.join(output_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2, cls=TupleEncoder)
        
        # Step 1: Perform Design Rule Check (DRC) if not skipped
        if not skip_drc:
            print("Performing Design Rule Check (DRC)...")
            drc_passed, drc_issues = check_rocket_configuration(config)
            
            if not drc_passed:
                print("\nDesign Rule Check failed")
                return {
                    "error": "Design Rule Check failed",
                    "drc_issues": drc_issues,
                    "config": config,
                    "reward": 0,
                    "reward_breakdown": {
                        "message": "Design failed DRC checks"
                    }
                }
        
        # Step 2: Run the simulation
        print("Running flight simulation...")
        simulation = RocketSimulation(config, output_dir=output_dir)
        simulation.setup_environment()
        simulation.build_rocket()
        simulation.run_simulation()
        results = simulation.analyze_results()
        
        # Generate plots if saving outputs
        if save_outputs:
            print("Generating plots...")
            saved_files = simulation.save_plots()
        
        # Step 3: Calculate reward
        flight_results = results["flight"]
        structural_results = results["structural"]
        material_results = results["materials"]
        
        # Format simple results for reward calculation
        simple_results = {
            "apogee": flight_results["max_apogee"],
            "apogee_error": abs(flight_results["max_apogee"] - target_apogee),
            "apogee_error_percent": (abs(flight_results["max_apogee"] - target_apogee) / target_apogee) * 100,
            "flight_time": flight_results["flight_time"],
            "max_speed": flight_results["max_speed"],
            "max_acceleration": flight_results["max_acceleration"],
            "horizontal_distance": flight_results["horizontal_distance"],
            "structural_failure": structural_results["overall_failure"],
            "total_cost": material_results["total_cost"],
            "plots_dir": output_dir
        }
        
        # Calculate reward using imported function
        reward, reward_breakdown = calculate_reward({
            "simple_results": simple_results,
            "full_results": results,
            "config": config
        }, target_apogee)
        
        # Save reward information if requested
        if save_outputs:
            reward_path = os.path.join(output_dir, "reward.json")
            with open(reward_path, 'w') as f:
                json.dump(reward_breakdown, f, indent=2, cls=TupleEncoder)
            
            report_path = os.path.join(output_dir, "reward_report.txt")
            with open(report_path, 'w') as f:
                f.write(format_reward_report(reward, reward_breakdown))
        
        # Return results
        return {
            "simulation_success": True,
            "simple_results": simple_results,
            "full_results": results,
            "config": config,
            "reward": reward,
            "reward_breakdown": reward_breakdown,
            "output_dir": output_dir
        }
    
    except Exception as e:
        print(f"Error in simulation: {e}")
        traceback.print_exc()
        
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "config": config,
            "simulation_success": False,
            "reward": 0,
            "reward_breakdown": {
                "message": f"Simulation failed: {str(e)}"
            }
        }


def process_llm_response(
    llm_response: str,
    target_apogee: float,
    output_dir: str = "outputs",
    wind_speed: float = 0,
    wind_direction: str = "N",
    skip_drc: bool = False,
    save_outputs: bool = True,
    timeout: int = 300
) -> Dict[str, Any]:
    """
    Process an LLM response, extract configuration, run simulation, and calculate reward.
    
    Args:
        llm_response (str): Raw response from LLM
        target_apogee (float): Target apogee in meters
        output_dir (str): Directory for saving outputs
        wind_speed (float): Wind speed in m/s
        wind_direction (str): Wind direction
        skip_drc (bool): Whether to skip the Design Rule Check
        save_outputs (bool): Whether to save the outputs
        timeout (int): Maximum simulation time in seconds
        
    Returns:
        dict: Results including configuration, simulation results, and reward
    """
    try:
        # Save the raw LLM response if requested
        if save_outputs:
            os.makedirs(output_dir, exist_ok=True)
            response_path = os.path.join(output_dir, "llm_response.txt")
            with open(response_path, 'w') as f:
                f.write(llm_response)
        
        print("Extracting configuration from LLM response...")
        # Step 1: Extract configuration from response
        try:
            config = extract_config_from_response(llm_response)
            
            # Convert any tuple values to lists for JSON compatibility
            # Especially for 'noise' parameters in parachutes
            if "parachutes" in config:
                for chute_key, chute_data in config["parachutes"].items():
                    if "noise" in chute_data and isinstance(chute_data["noise"], tuple):
                        chute_data["noise"] = list(chute_data["noise"])
            
        except Exception as e:
            print(f"Error extracting configuration: {e}")
            return {
                "error": f"Failed to extract configuration: {str(e)}",
                "llm_response": llm_response,
                "parsing_success": False,
                "reward": 0,
                "reward_breakdown": {
                    "message": f"Failed to parse LLM response: {str(e)}"
                }
            }
        
        # Step 2: Run simulation with timeout protection
        try:
            results = asyncio.run(
                asyncio.wait_for(
                    simulate_from_config(
                        config=config,
                        target_apogee=target_apogee,
                        output_dir=output_dir,
                        wind_speed=wind_speed,
                        wind_direction=wind_direction,
                        skip_drc=skip_drc,
                        save_outputs=save_outputs
                    ), 
                    timeout=timeout
                )
            )
            return results
            
        except asyncio.TimeoutError:
            print(f"Simulation timed out after {timeout} seconds")
            return {
                "error": "Simulation timed out",
                "config": config,
                "parsing_success": True,
                "simulation_success": False,
                "reward": 0,
                "reward_breakdown": {
                    "message": f"Simulation timed out after {timeout} seconds"
                }
            }
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        
        return {
            "error": f"Unexpected error: {str(e)}",
            "traceback": traceback.format_exc(),
            "llm_response": llm_response,
            "parsing_success": False,
            "simulation_success": False,
            "reward": 0,
            "reward_breakdown": {
                "message": f"Process failed with error: {str(e)}"
            }
        }


def print_result_summary(result: Dict[str, Any], target_apogee: float) -> None:
    """
    Print a summary of the processing results.
    
    Args:
        result (dict): Result dictionary from process_llm_response
        target_apogee (float): Target apogee in meters
    """
    print("\n" + "="*60)
    print(" RESULT SUMMARY ".center(60, "="))
    print("="*60)
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
    
    if "parsing_success" in result and not result["parsing_success"]:
        print("❌ Failed to parse LLM response")
    elif "simulation_success" in result and not result["simulation_success"]:
        print("❌ Simulation failed")
    elif "simulation_success" in result and result["simulation_success"]:
        print("✅ Simulation successful!")
        
        # Print flight metrics
        simple_results = result["simple_results"]
        print("\nFlight Metrics:")
        print(f"  Target Apogee: {target_apogee:.2f} m")
        print(f"  Actual Apogee: {simple_results['apogee']:.2f} m")
        print(f"  Error: {simple_results['apogee_error_percent']:.2f}%")
        print(f"  Max Speed: {simple_results['max_speed']:.2f} m/s")
        print(f"  Flight Time: {simple_results['flight_time']:.2f} s")
        print(f"  Structural Integrity: {'FAIL' if simple_results['structural_failure'] else 'PASS'}")
        print(f"  Total Cost: ${simple_results['total_cost']:.2f}")
    
    # Print reward score
    print(f"\nReward Score: {result['reward']:.2f} / 100")
    
    if "output_dir" in result:
        print(f"\nOutput directory: {result['output_dir']}")
    
    print("="*60)


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process LLM responses for rocket design")
    parser.add_argument("--response-file", type=str, help="File containing the LLM response")
    parser.add_argument("--response", type=str, help="Raw LLM response string")
    parser.add_argument("--apogee", type=float, required=True, help="Target apogee in meters")
    parser.add_argument("--wind-speed", type=float, default=0, help="Wind speed in m/s")
    parser.add_argument("--wind-direction", type=str, default="N", help="Wind direction")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Output directory")
    parser.add_argument("--skip-drc", action="store_true", help="Skip Design Rule Check")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    # Get LLM response
    if args.response_file:
        with open(args.response_file, 'r') as f:
            llm_response = f.read()
    elif args.response:
        llm_response = args.response
    else:
        print("Error: Must provide either --response-file or --response")
        sys.exit(1)
    
    # Process the response
    result = process_llm_response(
        llm_response=llm_response,
        target_apogee=args.apogee,
        output_dir=args.output_dir,
        wind_speed=args.wind_speed,
        wind_direction=args.wind_direction,
        skip_drc=args.skip_drc,
        timeout=args.timeout
    )
    
    # Print summary
    print_result_summary(result, args.apogee) 