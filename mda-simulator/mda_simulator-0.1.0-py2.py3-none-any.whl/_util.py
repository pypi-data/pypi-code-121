from __future__ import annotations
import numpy as np

__all__ = [
    "fast_disk",
]
def fast_disk(center, r, img_shape: tuple[int, int]):
    """disk, but much faster skimage version"""
    # based on https://stackoverflow.com/a/10032271/835607
    xx, yy = np.mgrid[:img_shape[0], :img_shape[1]]
    return  ((xx - center[0]) ** 2 + (yy - center[1]) ** 2) < r