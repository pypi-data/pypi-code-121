"""
.. _checks:

Checkers Functionality
----------------------

Module with functions to perform checks after having created a
rigid waist shift knob for a given optics configuration.
"""
import pandas as pd

# ----- ??? ----- #


def style_fields_dataframe(dataframe: pd.DataFrame):
    """
    Return a `~pandas.io.formats.style.Styler` object from the nominal or matched
    provided fields *dataframe*, to easily display the reach of limits.

    .. important::
        The provided *dataframe* should hold columns with checks of the reach of limits
        powering, namely ``imax``, ``ampere`` and ``percent``. This is a regular
        output of the knob creation of this package.
    """
    # fmt: off
    return dataframe[["imax", "ampere", "percent"]].style \
        .highlight_between(left=0, right=80, axis=1, props="color:white; background:green;") \
        .highlight_between(left=80, right=90, axis=1, props="color:black; background:yellow;") \
        .highlight_between(left=90, right=95, axis=1, props="color:black; background:orange;") \
        .highlight_between(left=95, right=100, axis=1, props="color:white; background:red;") \
        .set_caption("Nominal Powering of Affected Magnets")
    # fmt: on


def style_fields_changes(nominal_fields_dataframe: pd.DataFrame, matched_fields_dataframe: pd.DataFrame):
    """
    Return a `~pandas.io.formats.style.Styler` object from the nominal and matched
    fields dataframes, to easily display the change of powering for relevant magnets.

    .. important::
        The provided dataframes should hold columns with checks of the reach of limits
        powering, namely the ``percent`` column is used in this function. This is a regular
        output of the knob creation of this package.
    """
    # fmt: off
    return (matched_fields_dataframe[["percent"]] - nominal_fields_dataframe[["percent"]]).style \
    .highlight_between(left=-100, right=-5, axis=1, props="color:white; background:red;") \
    .highlight_between(left=-5, right=-2, axis=1, props="color:black; background:orange;") \
    .highlight_between(left=-2, right=-1, axis=1, props="color:black; background:yellow;") \
    .highlight_between(left=-1, right=1, axis=1, props="color:white; background:green;") \
    .highlight_between(left=1, right=2, axis=1, props="color:black; background:yellow;") \
    .highlight_between(left=2, right=5, axis=1, props="color:black; background:orange;") \
    .highlight_between(left=5, right=100, axis=1, props="color:white; background:red;") \
    .set_caption("Change in Powering of Affected Magnets [% of max powering]")
    # fmt: on
