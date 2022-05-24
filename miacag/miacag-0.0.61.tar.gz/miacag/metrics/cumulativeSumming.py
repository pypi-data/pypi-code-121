import torch

from monai.transforms import isnan
from monai.utils import convert_data_type

from monai.metrics import Cumulative


class CumulativeSumming(Cumulative):
    """
    Costum class by Christian
    """

    def __init__(self) -> None:
        super().__init__()
        self.sum = None
        self.not_nans = None

    def reset(self):
        """
        Reset all the running status, including buffers, sum, not nans count, etc.

        """
        super().reset()
        self.sum = None
        self.not_nans = None

    def aggregate(self):  # type: ignore
        """
        Sync data from all the ranks and compute the average value with previous sum value.

        """
        data = self.get_buffer()

        # compute SUM across the batch dimension
        nans = isnan(data)
        not_nans = convert_data_type((~nans), dtype=torch.float32)[0].sum(0)
        data[nans] = 0
        f = data.sum(0)
        

        # clear the buffer for next update
        super().reset()
        self.sum = f if self.sum is None else (self.sum + f)
        self.not_nans = not_nans if self.not_nans is None else (self.not_nans + not_nans)

        return self.sum
