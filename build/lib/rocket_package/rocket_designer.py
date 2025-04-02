#!/usr/bin/env python3
"""
Rocket Designer - End-to-end workflow for AI-powered rocket design and simulation.

This script:
1. Takes design requirements as input
2. Generates a prompt for an LLM
3. Sends the prompt to an LLM API
4. Parses the LLM response to extract a rocket configuration
5. Runs a design rule check (DRC) to verify basic design constraints
6. Runs a flight simulation with the configuration
7. Returns key flight statistics and analysis

Requirements:
- OpenAI or Anthropic API key set as environment variable
- RocketPy and related dependencies
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Import required modules
from.src.utils.generate_prompt import generate_rocket_design_prompt
from.src.utils.inference import generate_text
from.src.utils.model_parser import (
    extract_config_from_response,
    add_wind_settings,
    save_model_outputs
)
from.src.utils.design_rule_check import check_rocket_configuration, generate_drc_report
from.src.models.simulation import RocketSimulation
from.src.models.materials import materials
from.src.models.motors import motors as available_motor_configs

# Check for API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
    print("Error: No API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
    sys.exit(1)

# Import API clients based on available keys
if OPENAI_API_KEY:
    import openai
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

if ANTHROPIC_API_KEY:
    import anthropic
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

async def generate_rocket_design(prompt: str, model: str = "gpt-4") -> str:
    """
    Generate a rocket design by sending a prompt to an LLM.
    
    Args:
        prompt (str): The prompt to send to the LLM
        model (str): The model to use (default: gpt-4)
        
    Returns:
        str: The raw response from the LLM
    """
    response = await generate_text(model=model, prompt=prompt)
    return response

async def design_and_simulate_rocket(
    target_apogee: float,
    payload_mass: Optional[float] = None,
    stability_margin: Optional[float] = None,
    wind_speed: float = 0,
    wind_direction: str = "N",
    price_bonus: bool = False,
    llm_model: str = "gpt-4",
    output_dir: str = "outputs",
    save_config: bool = False,
    verbose: bool = False,
    skip_drc: bool = False
) -> Dict[str, Any]:
    """
    End-to-end workflow: design a rocket with an LLM and simulate its flight.
    
    Args:
        target_apogee (float): Target apogee in meters
        payload_mass (float, optional): Payload mass in kg
        stability_margin (float, optional): Target stability margin in calibers
        wind_speed (float): Wind speed in m/s
        wind_direction (str): Wind direction
        price_bonus (bool): Whether to emphasize cost optimization
        llm_model (str): LLM model to use
        output_dir (str): Directory for saving outputs
        save_config (bool): Whether to save the generated configuration
        verbose (bool): Whether to print detailed output
        skip_drc (bool): Whether to skip the Design Rule Check
        
    Returns:
        dict: Simulation results and statistics
    """
    # Step 1: Generate the prompt
    prompt = generate_rocket_design_prompt(
        target_apogee=target_apogee,
        payload_mass=payload_mass,
        stability_margin=stability_margin,
        price_bonus=price_bonus,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        material_options=None  # Use default materials
    )
    
    if verbose:
        print("=== GENERATED PROMPT ===")
        print(prompt)
        print("=======================\n")
    
    # Step 2: Send the prompt to the LLM
    print(f"Generating rocket design using {llm_model}...")
    llm_response = await generate_rocket_design(prompt, model=llm_model)
    
    if verbose:
        print("=== LLM RESPONSE ===")
        print(llm_response)
        print("===================\n")
    
    # Step 3: Extract and process the configuration
    print("Extracting configuration...")
    try:
        # Extract configuration from response
        config = extract_config_from_response(llm_response)
        
        # Save model outputs and configurations
        saved_files = save_model_outputs(
            output_dir=output_dir,
            llm_response=llm_response,
            config=config,
            save_final_config=save_config
        )
        print(f"Model outputs saved to {output_dir}")
        
        # Add wind settings to configuration
        config = add_wind_settings(config, wind_speed, wind_direction)
        
        if verbose:
            print("=== EXTRACTED CONFIGURATION ===")
            print(json.dumps(config, indent=2))
            print("==============================\n")
    
    except Exception as e:
        print(f"Error extracting configuration: {e}")
        return {"error": str(e), "llm_response": llm_response}
    
    # Step 4: Perform Design Rule Check (DRC) if not skipped
    if not skip_drc:
        print("Performing Design Rule Check (DRC)...")
        drc_passed, drc_issues = check_rocket_configuration(config)
        drc_report = generate_drc_report(config)
        print(drc_report)
        
        # Save DRC report to file
        drc_report_path = os.path.join(output_dir, "drc_report.txt")
        with open(drc_report_path, 'w') as f:
            f.write(drc_report)
        
        # Exit if DRC failed
        if not drc_passed:
            print("\nDesign Rule Check failed. Please check the configuration and try again.")
            return {
                "error": "Design Rule Check failed",
                "drc_issues": drc_issues,
                "drc_report": drc_report,
                "config": config,
                "llm_response": llm_response
            }
    else:
        print("Design Rule Check (DRC) skipped.")
        drc_passed = True
        drc_issues = []
        drc_report = "DRC skipped"
    
    # Step 5: Run the simulation
    print("Running flight simulation...")
    try:
        simulation = RocketSimulation(config, output_dir=output_dir)
        simulation.setup_environment()
        simulation.build_rocket()
        simulation.run_simulation()
        results = simulation.analyze_results()
        
        # Step 6: Generate plots
        print("Generating plots...")
        saved_files = simulation.save_plots()
        
        # Print a summary if verbose
        if verbose:
            simulation.print_summary()
        
        # Step 7: Compile and return the results
        flight_results = results["flight"]
        structural_results = results["structural"]
        material_results = results["materials"]
        
        # Calculate error from target apogee
        apogee_error = abs(flight_results["max_apogee"] - target_apogee)
        apogee_error_percent = (apogee_error / target_apogee) * 100
        
        # Format the simple results
        simple_results = {
            "apogee": flight_results["max_apogee"],
            "apogee_error": apogee_error,
            "apogee_error_percent": apogee_error_percent,
            "flight_time": flight_results["flight_time"],
            "max_speed": flight_results["max_speed"],
            "max_acceleration": flight_results["max_acceleration"],
            "horizontal_distance": flight_results["horizontal_distance"],
            "structural_failure": structural_results["overall_failure"],
            "total_cost": material_results["total_cost"],
            "plots_dir": output_dir
        }
        
        # Return both simple and full results
        return {
            "simple_results": simple_results,
            "full_results": results,
            "config": config,
            "plots": saved_files
        }
    
    except Exception as e:
        print(f"Error in simulation: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "config": config if 'config' in locals() else None,
            "drc_report": drc_report,
            "drc_passed": drc_passed
        }

def main():
    """Main function to run the rocket design and simulation workflow."""
    parser = argparse.ArgumentParser(description="AI-powered rocket design and simulation")
    parser.add_argument("--apogee", type=float, required=True, help="Target apogee in meters")
    parser.add_argument("--payload", type=float, help="Payload mass in kg")
    parser.add_argument("--stability", type=float, help="Target stability margin in calibers")
    parser.add_argument("--wind-speed", type=float, default=0, help="Wind speed in m/s")
    parser.add_argument("--wind-direction", type=str, default="N", help="Wind direction (N, S, E, W)")
    parser.add_argument("--price-bonus", action="store_true", help="Emphasize cost optimization")
    parser.add_argument("--model", type=str, default="gpt-4", help="LLM model to use")
    parser.add_argument("--output", type=str, default="outputs", help="Output directory")
    parser.add_argument("--save-config", action="store_true", help="Save the generated configuration")
    parser.add_argument("--verbose", action="store_true", help="Print detailed output")
    parser.add_argument("--output-file", type=str, help="File to save results as JSON")
    parser.add_argument("--skip-drc", action="store_true", help="Skip Design Rule Check")
    
    args = parser.parse_args()
    
    # Run the workflow
    results = asyncio.run(design_and_simulate_rocket(
        target_apogee=args.apogee,
        payload_mass=args.payload,
        stability_margin=args.stability,
        wind_speed=args.wind_speed,
        wind_direction=args.wind_direction,
        price_bonus=args.price_bonus,
        llm_model=args.model,
        output_dir=args.output,
        save_config=args.save_config,
        verbose=args.verbose,
        skip_drc=args.skip_drc
    ))
    
    # Check for errors
    if "error" in results:
        error_message = results["error"]
        print(f"\nError: {error_message}")
        
        # Special handling for DRC failures
        if error_message == "Design Rule Check failed":
            print("\nThe rocket design failed the Design Rule Check. Details:")
            for i, issue in enumerate(results["drc_issues"], 1):
                print(f"  {i}. {issue}")
            print(f"\nSee the full DRC report at {args.output}/drc_report.txt")
            print("\nTry modifying your prompt or using a different model.")
        
        sys.exit(1)
    
    # Print a summary of the results
    simple_results = results["simple_results"]
    print("\n=== SIMULATION RESULTS ===")
    print(f"Apogee: {simple_results['apogee']:.2f} m (target: {args.apogee:.2f} m)")
    print(f"Apogee Error: {simple_results['apogee_error']:.2f} m ({simple_results['apogee_error_percent']:.2f}%)")
    print(f"Flight Time: {simple_results['flight_time']:.2f} s")
    print(f"Max Speed: {simple_results['max_speed']:.2f} m/s")
    print(f"Max Acceleration: {simple_results['max_acceleration']:.2f} m/s²")
    print(f"Horizontal Distance: {simple_results['horizontal_distance']:.2f} m")
    print(f"Structural Failure: {simple_results['structural_failure']}")
    print(f"Total Cost: ${simple_results['total_cost']:.2f}")
    print(f"Plots saved to: {simple_results['plots_dir']}")
    
    # Save the results to a file if requested
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output_file}")
    
    # Return success or failure based on structural integrity
    if simple_results["structural_failure"]:
        print("\nDesign failed due to structural issues.")
        sys.exit(1)
    else:
        print("\nDesign succeeded!")
        sys.exit(0)

if __name__ == "__main__":
    main() 