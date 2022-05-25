# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Convenience names for long types."""
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import scipy
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

ColumnNameType = Union[str, List[str]]
FeaturizerType = Union[List[BaseEstimator], BaseEstimator, Pipeline]

# Convenience type for general data input
CoreDataInputType = Union[np.ndarray, pd.DataFrame, scipy.sparse.spmatrix]

# Convenience type for single column data input
CoreDataSingleColumnInputType = Union[np.ndarray, pd.Series, pd.Categorical]

# Convenience type representing transformers
# First param: column selector, either a column name string or a list of column name strings.
# Second param: list of sklearn transformation pipeline.
# Third param: dictionary of parameter options and value pairs to apply for the transformation.
TransformerType = Tuple[Union[str, List[str]], List[TransformerMixin], Dict[str, str]]

# Convenience type for grains
GrainType = Union[Tuple[str], str, List[str]]

# Convenience type for function inputs to DataFrame.apply (either a function or the name of one)
DataFrameApplyFunction = Union["Callable[..., Optional[Any]]", str]

# Convenience type representing transformer params for input columns
# First param: set of column inputs transformer takes (e.g. MiniBatchKMeans takes multiple columns as input).
# Second param: dictionary of parameter options and value pairs to apply for the transformation.
ColumnTransformerParamType = Tuple[List[str], Dict[str, Any]]

# Convenience type for featurization summary
FeaturizationSummaryType = List[Dict[str, Optional[Any]]]
