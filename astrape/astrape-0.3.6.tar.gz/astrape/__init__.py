import sys
import warnings

import pkg_resources
from pkg_resources import parse_version


from .experiment import Experiment
from .model_selection import CrossValidation

MIN_TORCH_VERSION = '1.1.0'
MIN_LIGHTNING_VERSION = '1.6.0'

try:
    import torch
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named 'torch', and astrape depends on PyTorch "
        "(aka 'torch'). "
        "Visit https://pytorch.org/ for installation instructions.")


try:
    import pytorch_lightning
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named 'pytorch-lightning', and astrape depends on PyTorch-Lightning "
        "(aka 'pytorch_lightning'). "
        "Visit https://www.pytorchlightning.ai/ for installation instructions.")

torch_version = pkg_resources.get_distribution('torch').version
if parse_version(torch_version) < parse_version(MIN_TORCH_VERSION):
    msg = ('astrape depends on a newer version of PyTorch (at least {req}, not '
           '{installed}). Visit https://pytorch.org for installation details')
    raise ImportWarning(msg.format(req=MIN_TORCH_VERSION, installed=torch_version))

lightning_version = pkg_resources.get_distribution('pytorch_lightning').version
if parse_version(lightning_version) < parse_version(MIN_LIGHTNING_VERSION):
    msg = ('astrape depends on a newer version of PyTorch (at least {req}, not '
           '{installed}). Visit https://www.pytorchlightning.ai/ for installation details')
    raise ImportWarning(msg.format(req=MIN_LIGHTNING_VERSION, installed=lightning_version))


from astrape.experiment import Experiment
from astrape.model_selection import CrossValidation
from astrape.project import Project
from astrape.utilities.dataloader_lightning import DataModule
from astrape.utilities.utils_lightning import initialize_datamodule, initialize_model
from astrape.models.models_lightning import MLP, ContractingMLP, CustomMLP, VGG, UNet
from astrape.base.experiment_base import BaseExperiment
from astrape.constants.astrape_constants import *
__all__ = [
    'Experiment',
    'CrossValidation',
    'Project',
    'DataModule',
    'MLP',
    'ContractingMLP',
    'CustomMLP',
    'VGG',
    'UNet',
    'BaseExperiment'
]

__import__("pkg_resources").declare_namespace(__name__)

try:
    __version__ = pkg_resources.get_distribution('astrape').version
except:
    __version__ = 'n/a'