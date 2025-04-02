"""
Module for parsing and processing LLM model outputs.
"""

import re
import json
from typing import Dict, Any
from pathlib import Path
import os

def extract_config_from_response(response: str) -> Dict[str, Any]:
    """
    Extract the Python dictionary configuration from the LLM response.
    
    Args:
        response (str): Raw LLM response
        
    Returns:
        dict: The extracted configuration dictionary
    """
    # Find content between triple backticks with python
    pattern = r"```(?:python)?\s*(config\s*=\s*\{[\s\S]*?\})\s*```"
    matches = re.findall(pattern, response)
    
    if not matches:
        # Try without python tag
        pattern = r"```\s*(config\s*=\s*\{[\s\S]*?\})\s*```"
        matches = re.findall(pattern, response)
        
    if not matches:
        # Try finding just a dictionary
        pattern = r"config\s*=\s*(\{[\s\S]*?\})"
        matches = re.findall(pattern, response)
    
    if not matches:
        raise ValueError("Could not extract configuration from LLM response")
    
    # Get the first match, which should be the dictionary definition
    config_str = matches[0]
    
    # Replace tuples if needed
    config_str = config_str.replace("(", "[").replace(")", "]")
    
    # Try to extract just the dictionary part
    if config_str.startswith("config"):
        try:
            config_str = config_str.split("=", 1)[1].strip()
        except IndexError:
            pass
    
    # Try to evaluate the string to get the dictionary
    # This is safer than using eval directly
    local_vars = {}
    try:
        exec(f"result = {config_str}", {"__builtins__": {}}, local_vars)
        return local_vars["result"]
    except Exception as e:
        raise ValueError(f"Failed to parse configuration: {e}")

def add_wind_settings(config: Dict[str, Any], wind_speed: float, wind_direction: str) -> Dict[str, Any]:
    """
    Add wind settings to the configuration.
    
    Args:
        config (dict): The rocket configuration
        wind_speed (float): Wind speed in m/s
        wind_direction (str): Wind direction (N, S, E, W)
        
    Returns:
        dict: Updated configuration with wind settings
    """
    if "env" not in config:
        config["env"] = {}
    
    # Convert wind direction to u,v components
    if wind_direction.upper() == "N":
        config["env"]["wind_u"] = 0
        config["env"]["wind_v"] = wind_speed
    elif wind_direction.upper() == "E":
        config["env"]["wind_u"] = wind_speed
        config["env"]["wind_v"] = 0
    elif wind_direction.upper() == "S":
        config["env"]["wind_u"] = 0
        config["env"]["wind_v"] = -wind_speed
    elif wind_direction.upper() == "W":
        config["env"]["wind_u"] = -wind_speed
        config["env"]["wind_v"] = 0
    else:
        # Default to the provided wind_speed in u direction
        config["env"]["wind_u"] = wind_speed
        config["env"]["wind_v"] = 0
    
    return config

def save_model_outputs(
    output_dir: str,
    llm_response: str,
    config: Dict[str, Any],
    save_final_config: bool = False
) -> Dict[str, str]:
    """
    Save model outputs and configurations to files.
    
    Args:
        output_dir (str): Directory to save outputs
        llm_response (str): Raw LLM response
        config (dict): Extracted configuration
        save_final_config (bool): Whether to save the final configuration
        
    Returns:
        dict: Paths to saved files
    """
    os.makedirs(output_dir, exist_ok=True)
    saved_files = {}
    
    # Save raw LLM response
    raw_response_path = os.path.join(output_dir, "llm_response.txt")
    with open(raw_response_path, 'w') as f:
        f.write(llm_response)
    saved_files["raw_response"] = raw_response_path
    
    # Save initial configuration
    initial_config_path = os.path.join(output_dir, "initial_rocket_config.json")
    with open(initial_config_path, 'w') as f:
        json.dump(config, f, indent=2)
    saved_files["initial_config"] = initial_config_path
    
    # Save final configuration if requested
    if save_final_config:
        final_config_path = os.path.join(output_dir, "rocket_config.json")
        with open(final_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        saved_files["final_config"] = final_config_path
    
    return saved_files 