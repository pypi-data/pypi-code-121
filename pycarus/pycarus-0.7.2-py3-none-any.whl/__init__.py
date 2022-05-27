import os
from importlib.util import find_spec

import pkg_resources

__version__ = pkg_resources.get_distribution("pycarus").version

if not find_spec("torch"):
    error_msg = "PyTorch is not installed. Install it by running: "
    dirname = os.path.dirname(os.path.realpath(__file__))
    error_msg += f"source {dirname}/install_torch.sh"
    raise ModuleNotFoundError(error_msg)

if not find_spec("pytorch3d"):
    error_msg = "PyTorch3D is not installed. Install it by running: "
    dirname = os.path.dirname(os.path.realpath(__file__))
    error_msg += f"source {dirname}/install_torch.sh"
    raise ModuleNotFoundError(error_msg)
