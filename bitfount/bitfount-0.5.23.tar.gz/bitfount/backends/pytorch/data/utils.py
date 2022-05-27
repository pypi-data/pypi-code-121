"""PyTorch data utility functions to be found here."""
from typing import List, Sequence, Union, cast

import numpy as np
import torch

from bitfount.data.types import _DataBatch, _SingleOrMulti


def _index_tensor_handler(
    idx: Union[int, Sequence[int], torch.Tensor]
) -> Union[int, Sequence[int]]:
    """Converts pytorch tensors to integers or lists of integers for indexing."""
    if torch.is_tensor(idx):
        idx = cast(torch.Tensor, idx)
        list_idx: list = idx.tolist()
        return list_idx
    else:
        idx = cast(Union[int, Sequence[int]], idx)
        return idx


def _convert_batch_to_tensor(
    batch: _DataBatch,
) -> List[_SingleOrMulti[torch.Tensor]]:
    """Converts a batch of data containing numpy arrays to torch tensors.

    Data must be explicitly converted to torch tensors since the PyTorch DataLoader
    which does this automatically is not being used.
    """
    x = [torch.tensor([b[0][i] for b in batch]) for i in range(len(batch[0][0]))]
    y = torch.from_numpy(np.array([b[1] for b in batch]))

    return [x, y]
