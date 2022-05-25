# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import scipy

from azureml._base_sdk_common._docstring_wrapper import experimental

from .._types import CoreDataInputType, CoreDataSingleColumnInputType

logger = logging.getLogger(__name__)


def _get_indices_missing_labels_output_column(y: np.ndarray) -> np.ndarray:
    """
    Return the indices of missing values in y.

    :param y: Array of training labels
    :return: Array of indices in y where the value is missing
    """
    if np.issubdtype(y.dtype, np.number):
        return np.argwhere(np.isnan(y)).flatten()
    else:
        return np.argwhere(np.isin(y, [None, "", "nan"]) | pd.isna(y)).flatten()


@experimental
def _remove_nan_rows_in_X_y(
    X: CoreDataInputType,
    y: CoreDataSingleColumnInputType,
    sample_weight: Optional[np.ndarray] = None,
    is_timeseries: bool = False,
    target_column: Optional[str] = None,
) -> Tuple[CoreDataInputType, CoreDataSingleColumnInputType, Optional[CoreDataSingleColumnInputType]]:
    """Remove the NaN columns in y and the corresponding rows in X."""
    X_new = X
    y_new = y
    sample_weight_new = sample_weight

    if X is not None and y is not None:
        if isinstance(y, pd.DataFrame):
            y = y.values.ravel()
        nan_y_index = _get_indices_missing_labels_output_column(y)

        logger.info("Inspecting target column for missing values.")

        if len(nan_y_index) > 0:
            logger.info("Dropping rows with invalid or empty values [np.nan, 'nan', '', None] in the target column.")
            y_new = np.delete(y, nan_y_index)
            if scipy.sparse.issparse(X):
                X_new = X_new.toarray()
            if isinstance(X_new, pd.DataFrame):
                X_new = X_new.iloc[list(set(range(X_new.shape[0])) - set(nan_y_index))]
            else:
                X_new = np.delete(X_new, nan_y_index, axis=0)
            if sample_weight is not None and sample_weight_new is not None:
                if scipy.sparse.issparse(sample_weight):
                    sample_weight_new = sample_weight_new.toarray()
                sample_weight_new = np.delete(sample_weight_new, nan_y_index, axis=0)
            # if input is sparse, convert back to csr
            if scipy.sparse.issparse(X):
                X_new = scipy.sparse.csr_matrix(X_new)
            if scipy.sparse.issparse(sample_weight):
                sample_weight_new = scipy.sparse.csr_matrix(sample_weight_new)
    return X_new, y_new, sample_weight_new


drop_nan_rows = _remove_nan_rows_in_X_y
