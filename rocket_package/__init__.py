"""
rocket_package - A package for simulating rocket designs
"""

# Import directly from the local structure
from .src.models import *
from .src.utils import *
from .src.analysis import *

# Also expose any main modules
try:
    from .main import *
    from .rocket_simulator import *
    from .rocket_designer import *
    from .rocket_interface import *
    from .calculate_reward import *
    from .default_configs import *
    from .simulate import *
except ImportError:
    pass

__version__ = "0.1.0"
