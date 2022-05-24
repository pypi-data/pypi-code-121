from typing import List, Tuple, Union

import numpy as np
from napari.layers import Points

__all__ = [
    "BroadcastablePoints",
]


class BroadcastablePoints(Points):
    def __init__(
        self, data=None, *, ndim=None, broadcast_dims: List[int] = None, **kwargs
    ):
        """
        Parameters
        ----------
        data :
        """
        if broadcast_dims is None:
            broadcast_dims = []
        # sort to ensure the for loop works correctly
        self._broadcast_dims = sorted(broadcast_dims)
        if data is not None:
            for b in broadcast_dims:
                # need to loop so because doing all at once means that larger
                # values for dim will be placed in the wrong spot
                # data = np.insert(data, b, -np.ones(data.shape[0]), axis=1)
                data = np.insert(data, b, 0, axis=1)

        super().__init__(data, ndim=ndim, **kwargs)

    def _slice_data(self, dims_indices) -> Tuple[List[int], Union[float, np.ndarray]]:
        """Determines the slice of points given the indices.
        Parameters
        ----------
        dims_indices : sequence of int or slice
            Indices to slice with.

        Returns
        -------
        slice_indices : list
            Indices of points in the currently viewed slice.
        scale : float, (N, ) array
            If in `out_of_slice_display` mode then the scale factor of points, where
            values of 1 corresponds to points located in the slice, and values
            less than 1 correspond to points located in neighboring slices.
        """
        # Get a list of the data for the points in this slice
        not_disp = list(self._dims_not_displayed)

        # ignore any dims we are broadcasting over
        for dim in self._broadcast_dims:
            if dim in not_disp:
                # if check to avoid errors when empty
                not_disp.remove(dim)

        indices = np.array(dims_indices)

        if len(self.data) > 0:
            if self.out_of_slice_display is True and self.ndim > 2:
                return super()._slice_data(dims_indices)
            else:
                data = self.data[:, not_disp]
                distances = np.abs(data - indices[not_disp])
                matches = np.all(distances <= 0.5, axis=1)
                slice_indices = np.where(matches)[0].astype(int)
                return slice_indices, 1
        else:
            return [], np.empty(0)
