"""
Utilities for setting up the simulation environment.
"""
import os
import datetime
import shutil
import numpy as np
import pandas as pd
from rocketpy import Environment, Function

def setup_environment_from_data(data_env):
    """
    Set up an environment using data dictionary.
    
    Args:
        data_env (dict): Dictionary with height, pressure, temperature, wind_u, wind_v.
        
    Returns:
        Environment: Configured RocketPy Environment.
    """
    df = pd.DataFrame(data_env)

    # Create Function objects to represent the profiles
    pressure_func = Function(np.column_stack([df['height'], df['pressure']]))
    temperature_func = Function(np.column_stack([df['height'], df['temperature']]))
    wind_u_func = Function(np.column_stack([df['height'], df['wind_u']]))
    wind_v_func = Function(np.column_stack([df['height'], df['wind_v']]))

    # Set up the environment
    env = Environment()
    env.set_atmospheric_model(
        type="custom_atmosphere",
        pressure=pressure_func,
        temperature=temperature_func,
        wind_u=wind_u_func,
        wind_v=wind_v_func,
    )
    
    return env

def setup_environment_with_cache(lat=32.990254, lon=-106.974998, elev=1400, cache_file='environment.json'):
    """
    Set up an environment with caching support.
    
    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        elev (float): Elevation in meters.
        cache_file (str): Path to cache file.
        
    Returns:
        Environment: Configured RocketPy Environment.
    """
    # Check if we have a saved environment file
    if os.path.exists(cache_file):
        print(f"Loading environment from {cache_file}")
        env = Environment()
        env.import_environment(filename=cache_file)
    else:
        print("Creating new environment and saving it for future use")
        # Create a new environment with location data
        env = Environment(latitude=lat, longitude=lon, elevation=elev)
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))
        
        # Set up the atmospheric model
        try:
            print("Fetching weather data...")
            env.set_atmospheric_model(type="Forecast", file="GFS")
        except Exception as e:
            print(f"Failed to fetch forecast data: {e}")
            print("Falling back to standard atmosphere model")
            env.set_atmospheric_model(type="standard_atmosphere")
        
        # Save the environment for future use
        env.export_environment(filename=cache_file)
        print(f"Environment saved to {cache_file}")
    
    return env

def create_constant_wind_environment(wind_speed_u=5, wind_speed_v=5, heights=None):
    """
    Create an environment with constant wind at multiple heights.
    
    Args:
        wind_speed_u (float): East-West wind component in m/s.
        wind_speed_v (float): North-South wind component in m/s.
        heights (list): List of heights in meters.
        
    Returns:
        dict: Data environment dictionary.
    """
    if heights is None:
        heights = [0, 1000, 2000, 5000, 10000]
    
    # Create wind arrays with constant values at each height
    wind_u = [wind_speed_u] * len(heights)
    wind_v = [wind_speed_v] * len(heights)
    
    # Standard atmosphere values for pressure and temperature
    pressures = [101325 * np.exp(-h / 8000) for h in heights]  # Simple barometric formula
    temperatures = [288.15 - 0.0065 * h for h in heights]      # Simple temperature lapse rate
    
    data_env = {
        'height': heights,
        'pressure': pressures,
        'temperature': temperatures,
        'wind_u': wind_u,
        'wind_v': wind_v,
    }
    
    return data_env 