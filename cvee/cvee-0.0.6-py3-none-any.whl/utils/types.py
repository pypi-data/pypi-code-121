import numbers

import numpy as np
import torch


def to_number(x):
    if isinstance(x, torch.Tensor):
        return x.detach().cpu().item()
    elif isinstance(x, np.ndarray):
        return x.item()
    elif isinstance(x, numbers.Number):
        return x
    elif isinstance(x, str):
        return float(x)
    else:
        raise TypeError("Not supported type")
