################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2021, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

from sklearn.utils.validation import check_array
from sklearn.impute import SimpleImputer
from sklearn.impute._base import _BaseImputer
from sklearn.base import clone
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from autoai_ts_libs.srom.imputers.base import TSImputer, FlattenImputer
from sklearn.experimental import enable_iterative_imputer
from autoai_ts_libs.srom.imputers.interpolators import PreMLImputer
from sklearn.impute import KNNImputer
from autoai_ts_libs.srom.imputers.extended_iterative_imputer import ExtendedIterativeImputer
class FlattenIterativeImputer(FlattenImputer):
    """
    Flatten Iterative Imputer.
    Parameters:
        time_column (int): time column.
        missing_values (obj): missing value to be imputed.
        enable_fillna (boolean): fill the backword and forward.
        order (int): lookback window.
        base_imputer(obj): base imputer object.
        model_imputer(obj): model imputer object.
    """

    def __init__(
        self,
        time_column=-1,
        missing_values=np.nan,
        enable_fillna=True,
        order=-1,
        base_imputer=PreMLImputer(),
        model_imputer=ExtendedIterativeImputer(random_state=1),
    ):
        super(FlattenIterativeImputer, self).__init__(
            time_column=time_column,
            missing_values=missing_values,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            model_imputer=model_imputer,
        )


class FlattenKNNImputer(FlattenImputer):
    """
    Flatten KNNImputer.
    Parameters:
        time_column (int): time column.
        missing_values (obj): missing value to be imputed.
        enable_fillna (boolean): fill the backword and forward.
        order (int): lookback window.
        base_imputer(obj): base imputer object.
        model_imputer(obj): model imputer object.
    """

    def __init__(
        self,
        time_column=-1,
        missing_values=np.nan,
        enable_fillna=True,
        order=-1,
        base_imputer=PreMLImputer(),
        model_imputer=KNNImputer(),
    ):
        super(FlattenKNNImputer, self).__init__(
            time_column=time_column,
            missing_values=missing_values,
            enable_fillna=enable_fillna,
            order=order,
            base_imputer=base_imputer,
            model_imputer=model_imputer,
        )
