import os

# Bring all entities from the extension module into this namespace
from .teqp import * 

def get_datapath():
    """Get the absolute path to the folder containing the root of multi-fluid data"""
    return os.path.abspath(os.path.dirname(__file__)+"/fluiddata")

from .teqp import __version__
