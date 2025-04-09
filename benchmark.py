import os
import argparse
import asyncio
import json
from typing import Dict, Any, List
from utils.inference import generate_text
from rocket_package.src.utils.model_parser import extract_config_from_response, add_wind_settings
from rocket_package.rocket_interface import simulate_from_config, print_result_summary
from rocket_package.calculate_reward import calculate_reward

async def llm_benchmark(
    prompt: str,
    model: str,
    target_apogee: float,
    max_iterations: int = 3,
    wind_speed: float = 0,
    wind_direction: str = "N",
    output_dir: str = "outputs",
    save_plots: bool = False
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
        
    Returns:
        Dictionary with benchmark results
    """
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
                    full_prompt += f"Target Apogee: {target_apogee}m, Actual: {r['apogee']:.2f}m, Error: {r['apogee_error_percent']:.2f}%\n"
                    full_prompt += f"Structural integrity: {'FAILED' if r['structural_failure'] else 'PASSED'}\n"
                    full_prompt += f"Cost: ${r['total_cost']:.2f}\n"
        
        # Add instruction for improvement if not first iteration
        if iteration > 0:
            full_prompt += "\n\nBased on previous attempts, please provide an improved rocket design."
            
        # Save the prompt
        with open(os.path.join(iter_dir, "prompt.txt"), "w") as f:
            f.write(full_prompt)
            
        print(f"Generating response using {model}...")
        llm_response = await generate_text(model=model, prompt=full_prompt)
        
        # Save the raw response
        with open(os.path.join(iter_dir, "response.txt"), "w") as f:
            f.write(llm_response)
            
        # Process the response and run simulation directly using the async function
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
            if "simple_results" in result:
                simple_results = result["simple_results"]
                apogee = simple_results["apogee"]
                horizontal_distance = simple_results["horizontal_distance"]
                total_cost = simple_results["total_cost"]
                impact_velocity = result.get("full_results", {}).get("flight", {}).get("impact_velocity", 0)
                structural_failure = simple_results["structural_failure"]
                
                # Calculate reward directly like in main.py
                reward_score, reward_breakdown = calculate_reward(
                    apogee=apogee,
                    target_apogee=target_apogee,
                    horizontal_distance=horizontal_distance,
                    total_cost=total_cost,
                    impact_velocity=impact_velocity,
                    structural_failure=structural_failure
                )
                
                # Override the reward in the result
                result["reward"] = reward_score * 100  # Convert to percentage
                result["reward_breakdown"] = reward_breakdown
                
                # Get the score
                score = reward_score * 100
            else:
                # If simple_results is not available, use the original reward
                score = result.get("reward", 0)
            
            print(f"Score: {score:.2f}/100")
            
            # Print summary
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
        "iterations": len(history),
        "best_score": best_score,
        "best_iteration": next((h["iteration"] for h in history if h["score"] == best_score), None),
        "history": history,
        "best_result": best_result
    }
    
    # Save benchmark result
    with open(os.path.join(output_dir, "benchmark_result.json"), "w") as f:
        json.dump(benchmark_result, f, default=lambda o: str(o) if not isinstance(o, (dict, list, str, int, float, bool, type(None))) else o, indent=2)
        
    return benchmark_result

def print_summary(result: Dict[str, Any], target_apogee: float) -> None:
    """Simple summary printer"""
    print("\n" + "="*60)
    print(" RESULT SUMMARY ".center(60, "="))
    print("="*60)
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    if "simulation_success" in result and result["simulation_success"]:
        simple_results = result["simple_results"]
        print("✅ Simulation successful!")
        print(f"\nTarget Apogee: {target_apogee:.2f} m")
        print(f"Actual Apogee: {simple_results['apogee']:.2f} m")
        print(f"Error: {simple_results['apogee_error_percent']:.2f}%")
        print(f"Structural Integrity: {'FAIL' if simple_results['structural_failure'] else 'PASS'}")
        print(f"Total Cost: ${simple_results['total_cost']:.2f}")
    
    print(f"\nReward Score: {result['reward']:.2f} / 100")
    print("="*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Rocket Design Benchmark")
    parser.add_argument("--prompt", type=str, required=True, help="Path to prompt file or raw prompt")
    parser.add_argument("--model", type=str, required=True, help="LLM model to use")
    parser.add_argument("--apogee", type=float, required=True, help="Target apogee in meters")
    parser.add_argument("--iterations", type=int, default=3, help="Maximum iterations")
    parser.add_argument("--wind-speed", type=float, default=0, help="Wind speed in m/s")
    parser.add_argument("--wind-direction", type=str, default="N", help="Wind direction")
    parser.add_argument("--output-dir", type=str, default="benchmarks", help="Output directory")
    parser.add_argument("--save-plots", action="store_true", help="Save simulation plots and outputs")
    
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
    output_dir = os.path.join(args.output_dir, f"{args.model.replace('/', '_')}_{timestamp}")
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
        save_plots=args.save_plots
    ))
    
    # Print final results
    print("\n========== BENCHMARK COMPLETE ==========")
    print(f"Model: {args.model}")
    print(f"Best score: {result['best_score']:.2f}/100 (Iteration {result['best_iteration']})")
    
    # Print score summary for all iterations
    print("\n----- ITERATION SCORES -----")
    for entry in result["history"]:
        iteration = entry["iteration"]
        score = entry["score"]
        status = "BEST" if score == result["best_score"] else ""
        print(f"Iteration {iteration}: {score:.2f}/100 {status}")
    
    print(f"Results saved to: {output_dir}")
