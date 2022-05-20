# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements all scoring functions that are not readily available"""

import math
from sklearn.metrics import mean_squared_error


def root_mean_squared_error(*args, **kwargs):
    """Because root_mean_squared_error is not readily available but mean_squared_error is, we compute mean_squared_error
    and return the squared root to get root_mean_squared_error.

    :param args: the positional arguments, these are y_true and y_pred
    :param kwargs: the keywords arguments if there are any
    :return: the root mean squared error
    """
    return math.sqrt(mean_squared_error(args[0], args[1], **kwargs))
