# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for computing similarity matrices. This module provides a wrapper around scipy distance package."""

import sys
import warnings
import logging
import scipy.spatial.distance as dist
import pandas as pd
import numpy as np


class Similarities:

    @staticmethod
    def compute_similarities(X, metric='jaccard', return_dataframe=True, cols=None, **kwargs):
        """A wrapper around scipy pdist function to compute similarity matrices.

        :param X: the input in binarized form
        :param metric: the metric to use (all metric supported by scipy can be used here)
        :param return_dataframe: a flag to define is the output should be returned in dataframe format
        :param cols: the columns to use if the return value is set to be a dataframe
        :param kwargs: kwargs to pass to pdist function
        :return: the similarity matrix

        Note: the scipy pdist computes the distances. 1 - dist is returned for similarity calculations
        """
        if X.shape[1] < 2:
            logging.error("The input matrix for similarity calculations must have more than 1 columns. Exiting...")
            sys.exit(1)

        # Note: transpose is needed to get the correct results
        matrix = 1 - dist.squareform(dist.pdist(X.T, metric, kwargs))

        if metric is 'jaccard' and np.array_equal(X, X.astype(bool)) is False:
            logging.error("Non-binary matrix is passed when calculating Jaccard distance."
                          " Make sure the matrix is binarized")
            sys.exit(1)

        if return_dataframe and cols is None:
            warnings.warn("No column names were passed to create the dataframe, "
                          "The default RangeIndex (0, 1, 2, …, n) will be used...", Warning)
            return pd.DataFrame(matrix)

        if return_dataframe and cols is not None:
            try:
                return pd.DataFrame(matrix, columns=cols)
            except ValueError:
                logging.exception("The length of the passed cols %s is %i, which doesn't match the expected length %i",
                                  cols, len(cols), matrix.shape[1])
                raise

        return matrix
