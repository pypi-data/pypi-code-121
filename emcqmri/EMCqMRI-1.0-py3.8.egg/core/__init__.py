from os.path import dirname, realpath
filepath = realpath(__file__)
parent_dir = dirname(filepath)
rec = 1 # This is always related to where the module is compared to the root of EMCqMRI. In this case, 4 folders down.
for _ in range(rec):
    parent_dir = dirname(parent_dir)
import sys
sys.path.insert(0,parent_dir)

from .base import *
from .engine import build_model, data_loader, estimate, train_model
# from .configuration import pll_configuration
# from .configuration.engine import *
# from .configuration.inference_model import *
from .utilities import *
