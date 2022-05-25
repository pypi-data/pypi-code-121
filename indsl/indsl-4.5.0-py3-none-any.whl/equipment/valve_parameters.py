# Copyright 2022 Cognite AS
from typing import Literal, Union

import numpy as np
import pandas as pd

from indsl import versioning
from indsl.resample.auto_align import auto_align
from indsl.ts_utils.ts_utils import scalar_to_pandas_series
from indsl.type_check import check_types
from indsl.validations import UserValueError

from . import valve_parameters_  # noqa


@versioning.register(
    version="2.0", changelog="The order of function parmeters was changed, with 'type' getting a default value."
)
@check_types
def flow_through_valve(
    inlet_P: Union[pd.Series, float],
    outlet_P: Union[pd.Series, float],
    valve_opening: Union[pd.Series, float],
    SG: float,
    min_opening: float,
    max_opening: float,
    min_Cv: float,
    max_Cv: float,
    type: Literal["Linear", "EQ"] = "Linear",
    align_timestamps: bool = False,
) -> pd.Series:
    r"""Valve volumetric flow rate

    This calculation can be used when there is no flow meter, but the pressure difference over the valve is known.
    The calculated flow rate is only exactly applicable for ideal fluids (incompressible and with zero viscosity).
    The availible valve characteristics are

    * Linear: :math:`C_v = ax + b`.
    * Equal percentage: :math:`C_v = ae^x + b`.

    The formula for the flow rate is

    .. math:: Q = C_v \sqrt{\frac{p_{in} - p_{out}}{SG}}.

    Args:
        inlet_P: Pressure at inlet [bar].
        outlet_P: Pressure at outlet [bar].
        valve_opening: Valve opening [-].
            Note that this is the proportional and not percentage valve opening.
        SG: Specific gravity of fluid [-].
        min_opening: Min opening [-].
            Valve opening at minimum flow.
        max_opening: Max opening [-].
            Valve opening at maximum flow.
        min_Cv: Min :math:`C_v` [:math:`\mathrm{\frac{gpm}{psi^{0.5}}}`].
            Valve :math:`C_v` at minimum flow.
            Note that the flow coefficient should be expressed in imperial units.
        max_Cv: Max :math:`C_v` [:math:`\mathrm{\frac{gpm}{psi^{0.5}}}`].
            Valve :math:`C_v` at maximum flow.
            Note that the flow coefficient should be expressed in imperial units.
        type: Valve characteristic.
            Valve characteristic, either "Linear" or "EQ" (equal percentage). Default is "Linear".
        align_timestamps: Auto-align.
            Automatically align time stamp of input time series. Default is False.

    Raises:
        ValueError: If the valve characteristic is not recognized.

    Returns:
        pd.Series: Valve flow rate [m3/h].
    """
    if SG < 0:
        raise UserValueError("Specific gravity cannot be negative.")

    inlet_P, outlet_P, valve_opening = auto_align([inlet_P, outlet_P, valve_opening], align_timestamps)

    if type == "Linear":
        Cv = (max_Cv - min_Cv) / (max_opening - min_opening) * valve_opening + (
            min_Cv * max_opening - min_opening * max_Cv
        ) / (max_opening - min_opening)
    elif type == "EQ":
        exp_coef = (max_Cv - min_Cv) / (np.exp(max_opening) - np.exp(min_opening))
        intercept = (min_Cv * np.exp(max_opening) - np.exp(min_opening) * max_Cv) / (
            np.exp(max_opening) - np.exp(min_opening)
        )
        Cv = exp_coef * np.exp(valve_opening) + intercept
    else:
        raise UserValueError("Only 'Linear' or 'EQ' valve characteristics are supported.")

    Q = 0.865 * Cv * np.sqrt((inlet_P - outlet_P) / SG)

    return scalar_to_pandas_series(Q)
