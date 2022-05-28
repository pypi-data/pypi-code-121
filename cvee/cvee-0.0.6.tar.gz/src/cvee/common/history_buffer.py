# https://github.com/facebookresearch/fvcore/blob/main/fvcore/common/history_buffer.py
# https://github.com/open-mmlab/mmcv/blob/master/mmcv/runner/log_buffer.py
from collections import OrderedDict

import numpy as np

from cvee.utils import to_number


class HistoryBuffer:
    def __init__(self):
        self.val_history = OrderedDict()
        self.n_history = OrderedDict()
        self.output = OrderedDict()

    def add(self, vars, n=1):
        """
        Args:
            vars (dict): variables to be added
            n (int): number of steps for the variable (differs from mmcv),
                avg would be: vars/n
        """
        if not isinstance(vars, dict):
            raise TypeError(f"vars should be a dict, but got {type(vars)}")

        for key, val in vars.items():
            if key not in self.val_history:
                self.val_history[key] = []
                self.n_history[key] = []

            self.val_history[key].append(to_number(val))
            self.n_history[key].append(n)

    def avg(self, window_size=0, keys=None, is_ordered=False):
        if window_size < 0:
            raise ValueError(f"window_size should be greater than 0, but got {window_size}")

        output = {} if not is_ordered else OrderedDict()
        if keys is None:
            keys = self.val_history.keys()
        else:
            keys = [k for k in self.val_history.keys() if k in keys]

        for key in keys:
            values = np.array(self.val_history[key][-window_size:])
            nums = np.array(self.n_history[key][-window_size:])
            avg = np.sum(values) / np.sum(nums)
            output[key] = avg
        return output

    def one_line(self, window_size=0, keys=None, str_fmt=".4f"):
        output = self.avg(window_size=window_size, keys=keys, is_ordered=True)
        output_str = ", ".join([f"{k}: {v:{str_fmt}}" for k, v in output.items()])
        return output_str


if __name__ == "__main__":
    import cvee
    import torch

    use_cuda = torch.cuda.is_available()

    history = HistoryBuffer()
    for i in range(5):
        for j in range(5):
            history.add({"i": i, "j": torch.tensor(j).cuda() if use_cuda else torch.tensor(j)})
            cvee.print(history.one_line())
