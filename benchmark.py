import os
import argparse
import asyncio
import json
import math
from typing import Dict, Any, List, Tuple, Optional
from utils.inference import generate_text
from rocket_package.src.utils.model_parser import extract_config_from_response, add_wind_settings
from rocket_package.rocket_interface import simulate_from_config, print_result_summary
from rocket_package.calculate_reward import (
    calculate_reward,
    format_reward_report,
    calculate_complex_bullseye_reward,
    format_complex_bullseye_report
)

async def llm_benchmark(
    prompt: str,
    model: str,
    target_apogee: float,
    max_iterations: int = 3,
    wind_speed: float = 0,
    wind_direction: str = "N",
    output_dir: str = "outputs",
    save_plots: bool = False,
    target_x: Optional[float] = None,
    target_y: Optional[float] = None
) -> Dict[str, Any]:
    """
    Run an iterative benchmarking process with an LLM for rocket design optimization.
    
    Args:
        prompt: Initial prompt for the LLM
        model: LLM model to use (e.g., "gpt-4", "claude-3-opus")
        target_apogee: Target altitude in meters
        max_iterations: Maximum number of improvement iterations
        wind_speed: Wind speed in m/s
        wind_direction: Wind direction as string
        output_dir: Base directory for outputs
        save_plots: Whether to save simulation plots
        target_x: Optional X-coordinate for bullseye landing target
        target_y: Optional Y-coordinate for bullseye landing target
        
    Returns:
        Dictionary with benchmark results
    """
    # Determine if we're in bullseye mode
    bullseye_mode = target_x is not None and target_y is not None
    
    history = []
    best_result = None
    best_score = 0
    
    for iteration in range(max_iterations):
        print(f"\n=== ITERATION {iteration+1}/{max_iterations} ===")
        iter_dir = os.path.join(output_dir, f"iteration_{iteration+1}")
        os.makedirs(iter_dir, exist_ok=True)
        
        # Build the full prompt with history
        full_prompt = prompt
        if history:
            full_prompt += "\n\n=== PREVIOUS ATTEMPTS ===\n"
            for i, entry in enumerate(history):
                full_prompt += f"\n--- ATTEMPT {i+1} ---\n"
                full_prompt += f"Design:\n{entry['response']}\n"
                full_prompt += f"Score: {entry['score']:.2f}/100\n"
                if 'simple_results' in entry['result']:
                    r = entry['result']['simple_results']
                    
                    if bullseye_mode:
                        # Include bullseye-specific information in prompt
                        landing_x = r.get('landing_x', 0)
                        landing_y = r.get('landing_y', 0)
                        landing_error = math.sqrt((landing_x - target_x)**2 + (landing_y - target_y)**2)
                        full_prompt += f"Target Position: ({target_x}m, {target_y}m), Landing Position: ({landing_x:.2f}m, {landing_y:.2f}m), Error: {landing_error:.2f}m\n"
                    else:
                        # Include apogee-specific information in prompt
                        full_prompt += f"Target Apogee: {target_apogee}m, Actual: {r['apogee']:.2f}m, Error: {r['apogee_error_percent']:.2f}%\n"
                    
                    full_prompt += f"Structural integrity: {'FAILED' if r['structural_failure'] else 'PASSED'}\n"
                    full_prompt += f"Cost: ${r['total_cost']:.2f}\n"
        
        # Add instruction for improvement if not first iteration
        if iteration > 0:
            if bullseye_mode:
                full_prompt += f"\n\nBased on previous attempts, please provide an improved rocket design that will precisely land at the target coordinates ({target_x}m, {target_y}m)."
            else:
                full_prompt += f"\n\nBased on previous attempts, please provide an improved rocket design that will reach the target apogee of {target_apogee}m."
            
        # Save the prompt
        with open(os.path.join(iter_dir, "prompt.txt"), "w") as f:
            f.write(full_prompt)
            
        print(f"Generating response using {model}...")
        llm_response = await generate_text(model=model, prompt=full_prompt)
        
        # Save the raw response
        with open(os.path.join(iter_dir, "response.txt"), "w") as f:
            f.write(llm_response)
            
        # Process the response and run simulation
        print(f"Running simulation with the generated design...")
        try:
            # Extract configuration from response
            config = extract_config_from_response(llm_response)
            
            # Run simulation
            result = await simulate_from_config(
                config=config,
                target_apogee=target_apogee,
                output_dir=iter_dir,
                wind_speed=wind_speed,
                wind_direction=wind_direction,
                save_outputs=save_plots
            )
            
            # Get the specific values needed for reward calculation
            if "simple_results" in result and "full_results" in result:
                simple_results = result["simple_results"]
                flight_results = result["full_results"].get("flight", {})
                
                # Extract common values
                apogee = simple_results["apogee"]
                total_cost = simple_results["total_cost"]
                horizontal_distance = simple_results["horizontal_distance"]
                impact_velocity = flight_results.get("impact_velocity", 10.0)
                structural_failure = simple_results["structural_failure"]
                
                # Extract or calculate landing coordinates
                landing_x = float(flight_results.get("x_final", 0))
                landing_y = float(flight_results.get("y_final", 0))
                
                # Add landing coordinates to simple_results for future iterations
                simple_results["landing_x"] = landing_x
                simple_results["landing_y"] = landing_y
                
                # Calculate reward based on mode
                if bullseye_mode:
                    # Bullseye landing reward calculation
                    reward_score, reward_breakdown = calculate_complex_bullseye_reward(
                        landing_x=landing_x,
                        landing_y=landing_y,
                        target_x=target_x,
                        target_y=target_y,
                        total_cost=total_cost,
                        impact_velocity=impact_velocity,
                        structural_failure=structural_failure,
                        actual_apogee=apogee,
                        target_apogee=target_apogee
                    )
                    
                    # Format reward report
                    reward_report = format_complex_bullseye_report(reward_score, reward_breakdown)
                else:
                    # Traditional apogee-based reward calculation
                    reward_score, reward_breakdown = calculate_reward(
                        apogee=apogee,
                        target_apogee=target_apogee,
                        horizontal_distance=horizontal_distance,
                        total_cost=total_cost,
                        impact_velocity=impact_velocity,
                        structural_failure=structural_failure
                    )
                    
                    # Format reward report
                    reward_report = format_reward_report(reward_score, reward_breakdown)
                
                # Override the reward in the result
                result["reward"] = reward_score * 100  # Convert to percentage
                result["reward_breakdown"] = reward_breakdown
                
                # Get the score
                score = reward_score * 100
                
                # Save reward report
                with open(os.path.join(iter_dir, "reward_report.txt"), "w") as f:
                    f.write(reward_report)
            else:
                # If simple_results is not available, use the original reward
                score = result.get("reward", 0)
            
            print(f"Score: {score:.2f}/100")
            
            # Print summary based on mode
            if bullseye_mode:
                print_bullseye_summary(result, target_x, target_y)
            else:
                print_result_summary(result, target_apogee)
            
            # Save to history
            history.append({
                "iteration": iteration + 1,
                "response": llm_response,
                "result": result,
                "score": score
            })
            
            # Update best result if needed
            if score > best_score:
                best_result = result
                best_score = score
                print(f"New best score: {best_score:.2f}/100")
                
        except Exception as e:
            print(f"Error processing response: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Add to history with zero score
            history.append({
                "iteration": iteration + 1,
                "response": llm_response,
                "result": {"error": str(e)},
                "score": 0
            })
    
    # Compile final results
    benchmark_result = {
        "model": model,
        "target_apogee": target_apogee,
        "mode": "bullseye" if bullseye_mode else "apogee",
        "iterations": len(history),
        "best_score": best_score,
        "best_iteration": next((h["iteration"] for h in history if h["score"] == best_score), None),
        "history": history,
        "best_result": best_result
    }
    
    # Add bullseye target info if applicable
    if bullseye_mode:
        benchmark_result["target_x"] = target_x
        benchmark_result["target_y"] = target_y
    
    # Save benchmark result
    with open(os.path.join(output_dir, "benchmark_result.json"), "w") as f:
        json.dump(benchmark_result, f, default=lambda o: str(o) if not isinstance(o, (dict, list, str, int, float, bool, type(None))) else o, indent=2)
        
    return benchmark_result

def print_bullseye_summary(result: Dict[str, Any], target_x: float, target_y: float) -> None:
    """Special summary printer for bullseye mode"""
    print("\n" + "="*60)
    print(" BULLSEYE LANDING SUMMARY ".center(60, "="))
    print("="*60)
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    if "simple_results" in result and "full_results" in result:
        simple_results = result["simple_results"]
        flight_results = result["full_results"].get("flight", {})
        
        # Extract landing coordinates
        landing_x = flight_results.get("x_final", 0)
        landing_y = flight_results.get("y_final", 0)
        
        # Calculate landing error
        landing_error = math.sqrt((landing_x - target_x)**2 + (landing_y - target_y)**2)
        
        print("✅ Simulation successful!")
        print(f"\nTarget Position: ({target_x:.2f}m, {target_y:.2f}m)")
        print(f"Landing Position: ({landing_x:.2f}m, {landing_y:.2f}m)")
        print(f"Landing Error: {landing_error:.2f}m")
        print(f"Max Apogee: {simple_results['apogee']:.2f}m")
        print(f"Structural Integrity: {'FAIL' if simple_results['structural_failure'] else 'PASS'}")
        print(f"Total Cost: ${simple_results['total_cost']:.2f}")
    
    print(f"\nReward Score: {result['reward']:.2f} / 100")
    print("="*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Rocket Design Benchmark")
    parser.add_argument("--prompt", type=str, required=True, help="Path to prompt file or raw prompt")
    parser.add_argument("--model", type=str, required=True, help="LLM model to use")
    parser.add_argument("--apogee", type=float, required=False, help="Target apogee in meters")
    parser.add_argument("--iterations", type=int, default=3, help="Maximum iterations")
    parser.add_argument("--wind-speed", type=float, default=0, help="Wind speed in m/s")
    parser.add_argument("--wind-direction", type=str, default="N", help="Wind direction")
    parser.add_argument("--output-dir", type=str, default="benchmarks", help="Output directory")
    parser.add_argument("--save-plots", action="store_true", help="Save simulation plots and outputs")
    parser.add_argument("--target-x", type=float, help="X-coordinate for bullseye landing target")
    parser.add_argument("--target-y", type=float, help="Y-coordinate for bullseye landing target")
    
    args = parser.parse_args()
    
    # Get the prompt
    if os.path.isfile(args.prompt):
        with open(args.prompt, "r") as f:
            prompt = f.read()
    else:
        prompt = args.prompt
    
    # Create run-specific output directory
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Add mode indicator to directory name
    mode_indicator = "bullseye" if (args.target_x is not None and args.target_y is not None) else "apogee"
    output_dir = os.path.join(args.output_dir, f"{args.model.replace('/', '_')}_{mode_indicator}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the benchmark
    result = asyncio.run(llm_benchmark(
        prompt=prompt,
        model=args.model,
        target_apogee=args.apogee,
        max_iterations=args.iterations,
        wind_speed=args.wind_speed,
        wind_direction=args.wind_direction,
        output_dir=output_dir,
        save_plots=args.save_plots,
        target_x=args.target_x,
        target_y=args.target_y
    ))
    
    # Print final results
    print("\n========== BENCHMARK COMPLETE ==========")
    print(f"Model: {args.model}")
    print(f"Mode: {'Bullseye Landing' if result['mode'] == 'bullseye' else 'Apogee Targeting'}")
    if result['mode'] == 'bullseye':
        print(f"Target: ({result['target_x']:.2f}m, {result['target_y']:.2f}m)")
    else:
        print(f"Target Apogee: {result['target_apogee']:.2f}m")
    print(f"Best score: {result['best_score']:.2f}/100 (Iteration {result['best_iteration']})")
    
    # Print score summary for all iterations
    print("\n----- ITERATION SCORES -----")
    for entry in result["history"]:
        iteration = entry["iteration"]
        score = entry["score"]
        status = "BEST" if score == result["best_score"] else ""
        print(f"Iteration {iteration}: {score:.2f}/100 {status}")
    
    print(f"Results saved to: {output_dir}")
