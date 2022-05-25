# Copyright 2021 Cognite AS
import pandas as pd

from indsl.versioning import register

from . import versioning_test_  # noqa


@register(version="2.0", deprecated=True, changelog="Added verbose parameter")
def versioning_test_op(series: pd.Series, verbose: bool):
    """New versioning test
    This new function is used only for testing purposes

    Args:
        series: Dummy input
        verbose: Dummy flag

    Returns:
        pandas.Series: Dummy output
    """
    return series
