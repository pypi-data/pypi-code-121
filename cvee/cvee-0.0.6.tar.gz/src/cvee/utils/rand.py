import numpy as np
import torch


# TODO: Write test cases
def sample(array, sample_num, dim=0, is_sorted=True):
    return_tensor = isinstance(array, torch.Tensor)

    array_num = array.shape[dim]
    if not return_tensor:
        if array_num >= sample_num:
            rand_indices = np.random.choice(array_num, sample_num, replace=False)
        else:
            rand_indices = np.random.choice(array_num, sample_num, replace=True)
        if is_sorted:
            rand_indices = sorted(rand_indices)
        return np.take(array, rand_indices, axis=dim)


def rand_indices(size, sample_num, is_sorted=True):
    if size >= sample_num:
        rand_indices = np.random.choice(size, sample_num, replace=False)
    else:
        rand_indices = np.random.choice(size, sample_num, replace=True)
    if is_sorted:
        rand_indices = sorted(rand_indices)
    return rand_indices
