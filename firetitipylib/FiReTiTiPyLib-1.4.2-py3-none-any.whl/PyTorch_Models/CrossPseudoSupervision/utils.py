import torch
import numpy as np

def lamdba_scaling(epoch, cps_weight):
    if epoch <= 5:
        return 1e-5
    elif epoch <= 20:
        m = (cps_weight - 1e-5) / 15
        b = cps_weight - 20 * m
        return m * epoch + b
    else:
        return cps_weight

class Dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def poly_lr_linear_warmup(base_lr, iter, max_iter):
    if iter < 1500:
        slope = base_lr / 1500
        lr = slope * iter
    else:
        lr = base_lr * (1 - iter / max_iter)
    return lr

def detach_to_numpy(tensor: torch.Tensor) -> np.ndarray:
    return tensor.detach().clone().cpu().numpy()