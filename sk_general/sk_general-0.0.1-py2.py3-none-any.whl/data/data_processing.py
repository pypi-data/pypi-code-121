from typing import Tuple, Union, Iterable, Any, Dict
from typing import overload, Optional, Literal, List


import pandas as pd
import numpy as np
import logging


log = logging.getLogger(__name__)


def _is_true(series: pd.Series, true_key: Any = "Y", false_key: Optional[Any] = None) -> pd.Series:
    """
    Converts a Series of elements supposed to indicate a boolean to a boolean series.

    :param series: Series of bool-like elements
    :param true_key: element to == True
    :param false_key: Optional: element to == for False

    """
    conditions: List[Union[pd.Series, bool]] = [series == true_key]
    choices = [True, False]
    if false_key is not None:
        conditions.append(series == false_key)
    else:
        conditions.append(True)
    true_values = np.select(conditions, choices, default=np.nan)
    true_series = pd.Series(true_values, index=series.index, name=series.name).astype(bool)

    return true_series


def get_index_pattern_mask(
    df: Union[pd.DataFrame, pd.Series],
    pattern: str,
    axis: Union[str, int] = 0,
    regex: bool = True,
    **contains_kwargs: Dict[str, Any],
) -> np.ndarray:
    """
    Returns a boolean mask of the axis that matches the pattern.

    :param df: DataFrame or Series to filter
    :param pattern: Pattern to match
    :param axis: Axis to filter on
        * 0/"index"
        * 1/"columns"
        * 2, 3, 4... theoretically higher axis orders returned by df.axes. Added for extensibility.

    :param regex: whether to use regex or standard substring contains
    :return: Boolean mask
    """
    if isinstance(axis, str):
        if axis == "columns":
            axis = 1
        elif axis == "index":
            axis = 0
        else:
            raise ValueError("If passed as a str, axis must be one of 'columns' or 'index'")
        log.debug(f"Converted str-type axis to {axis}")
    axes = df.axes
    if len(axes) >= axis:
        return df.axes[axis].str.contains(pattern, regex=regex, **contains_kwargs)
    else:
        raise ValueError(f"Axis {axis} is not in the dataframe")


def extract_target_from_df(
    df: pd.DataFrame, target_name: Optional[str] = None, return_Xy: Optional[bool] = True
) -> Union[Tuple[pd.DataFrame, pd.Series], pd.Series]:
    if target_name is None:
        target_name = "target"
        log.info(f"No target name specified, assuming default: {target_name}")
    log.info(f"Extracting target {target_name} from df")
    target_series = df[target_name]
    if return_Xy:
        log.debug("Returning df and target as (X, y)")
        return df.drop(columns=target_name), target_series
    else:
        log.debug("Returning target variable as Series")
        return df[target_name]


def iter_to_dict(iterable: Iterable[Any], keys: Iterable[Any], **conversion_kwargs: Dict[str, Any]) -> Dict[Any, Any]:
    """
    Converts an iterable of values to a dictionary.
    """
    return dict(zip(keys, iterable))


from typing import Callable


class DataHandler:

    converters: Dict[Tuple[str], Callable] = {
        ("iter", "dict"): iter_to_dict,
    }

    verifiers = {
        "iter": lambda data: isinstance(data, tuple),
    }

    def __init__(
        self,
        input_type: Optional[str] = None,
        output_type: Optional[str] = None,
        transformation_type: Optional[str] = None,
    ) -> None:
        self.input_type = input_type
        self.output_type = output_type

    def convert_data(self, data, input_type, output_type, **conversion_kwargs):
        if input_type == output_type:
            pass
        conversion_keys = (input_type, output_type)
        if all(conversion_keys):
            return self.converters[conversion_keys](data, **conversion_kwargs)
        else:
            return data

    def receive_data(self, data: pd.DataFrame) -> None:
        if self.verify_input_type(data):

            self.data = data

    def verify_input_type(self, data: Any, default: bool = False) -> bool:
        if self.input_type:
            return self.verifiers[self.input_type](data)
        else:
            log.debug("No input checking, assuming correct input type")
            return True

    def emit_data(self):
        return self.data

    def transform_data(self) -> None:
        pass

    def __call__(self, data: Any):
        self.receive_data(data)
        self.transform_data()
        return self.emit_data()
