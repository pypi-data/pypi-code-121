import os
from typing import Dict, Union

import numpy as np
import pandas as pd

from .. import C


def tsv_to_df(loc: str, file_: str = "logger.csv"):
    """
    Read in the morpheus logging file `file_`, which should be in
    tab-separated tsv format and defaults to "logger.csv", inside
    directory `loc`.

    Parameters
    ----------
    loc: str
        The simulations results folder.
    file_: str, optional (default="logger.csv")
        The logger file containing the results in tsv format.

    Returns
    -------
    data_frame: pandas.DataFrame
        A dataframe of the file contents.
    """
    data_file = os.path.join(loc, file_)
    data_frame = pd.read_csv(data_file, sep="\t")
    return data_frame


def split_list(alist, wanted_parts):
    """
    Take a set of lists based on the number of particles and turn that into a
    set of list based on the number of summary statistics.

    Parameters
    ----------
    alist: str
        list of particles readout
    wanted_parts: int
        should be equal to the number of summary statistics functions.

    Returns
    -------
        A list of lists, were the number of lists equal to the number of
        summary statistic functions.
    """
    return [alist[i::wanted_parts] for i in range(wanted_parts)]


def unscale(
    scaled_par: Dict[str, float], par_scale: Union[Dict[str, str], str]
) -> Dict[str, float]:
    """Unscale parameters from scale to linear scale.

    Keys in `scaled_par` may be only a subset of those in `par_scale`, in case
    only partial parameters are considered.

    Parameters
    ----------
    scaled_par:
        Scaled parameters, keys are parameter ids and values the scaled values.
    par_scale:
        Scales, keys are parameter ids and values the scales.

    Returns
    -------
    unscaled_par:
        Unscaled parameters.
    """
    unscaled_par = {}
    for key, scaled_val in scaled_par.items():
        scale = par_scale if isinstance(par_scale, str) else par_scale[key]
        if scale == C.LIN:
            unscaled_par[key] = scaled_val
        elif scale == C.LOG:
            unscaled_par[key] = np.exp(scaled_val)
        elif scale == C.LOG10:
            unscaled_par[key] = 10.0 ** scaled_val
        elif scale == C.LOG2:
            unscaled_par[key] = 2.0 ** scaled_val
        else:
            raise ValueError(f"Parameter scale {scale} is not supported")

    return unscaled_par
