from typing import Union

import numpy as np
import torch

ArrayLike = Union[int, float, list, tuple, np.ndarray]

ArrayOrTensor = Union[np.ndarray, torch.Tensor]
ArrayLikeOrTensor = Union[ArrayLike, torch.Tensor]
