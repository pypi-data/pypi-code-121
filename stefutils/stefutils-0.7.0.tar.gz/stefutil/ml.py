"""
machine learning
"""

import sys
from typing import Union

import torch

from stefutil.prettier import fmt_num

__all__ = ['model_param_size', 'get_model_num_trainable_parameter', 'is_on_colab']


def get_torch_device():
    return 'cuda' if torch.cuda.is_available() else 'cpu'


def model_param_size(m: torch.nn.Module, as_str=True) -> Union[int, str]:
    num = sum(p.numel() for p in m.parameters())
    return fmt_num(num) if as_str else num


def get_model_num_trainable_parameter(model: torch.nn.Module, readable: bool = True) -> Union[int, str]:
    n = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return fmt_num(n) if readable else n


def is_on_colab() -> bool:
    return 'google.colab' in sys.modules
