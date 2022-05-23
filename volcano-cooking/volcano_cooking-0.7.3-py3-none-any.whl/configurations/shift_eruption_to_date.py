"""Shift the second eruption to a given date.

Note
----
This script is intended to be used with the `--shift-eruption-to-date` flag. If no
'synthetic_volcanoes' file is present, it will create one and try and shift the eruption
generated in that file, before a second file is saved with the shifted eruption.
"""


from typing import Optional, Tuple

import numpy as np
import xarray as xr

import volcano_cooking.helper_scripts.functions as fnc
import volcano_cooking.modules.create as create


def shift_eruption_to_date(
    eruption_date: Tuple[int, int, int], file: Optional[str]
) -> None:
    """Shift the eruption date of the synthetic volcanoes file.

    Parameters
    ----------
    eruption_date: Tuple[int, int, int]
        Tuple with the new eruption date.
    file: str
        Full path (absolute or relative to where the function is called) and file name of
        a custom file to be used.

    Raises
    ------
    ValueError
        If the eruption date is not a valid date or if it is before or after the first and
        last eruptions.
    """
    if eruption_date[0] < 0 or eruption_date[0] > 9999:
        raise ValueError("Year of eruption must be between 0 and 9999, inclusive.")
    if eruption_date[1] < 1 or eruption_date[1] > 12:
        raise ValueError("Month of eruption must be between 1 and 12, inclusive.")
    if eruption_date[2] < 1 or eruption_date[2] > 28:
        raise ValueError("Day of eruption must be between 1 and 28, inclusive.")
    arrs = open_file("nc", file)
    first = arrs[1][0] * 10000 + arrs[2][0] * 100 + arrs[3][0]
    last = arrs[1][-1] * 10000 + arrs[2][-1] * 100 + arrs[3][-1]
    new = eruption_date[0] * 10000 + eruption_date[1] * 100 + eruption_date[2]
    if new < first or new > last:
        raise ValueError(
            f"The eruption date ({new}) is not in between "
            + f"the first and last eruption ({first}, {last})."
        )
    arrs[1][1] = eruption_date[0]
    arrs[2][1] = eruption_date[1]
    arrs[3][1] = eruption_date[2]
    frc_cls = create.Data(*arrs)
    frc_cls.make_dataset()
    frc_cls.save_to_file()


def open_file(ext: str, in_file: Optional[str] = None) -> Tuple[np.ndarray, ...]:
    """Load variables from the last saved file of given extension.

    Parameters
    ----------
    ext: str
        Extension of the file that should be used
    in_file: str, optional
        Full path (absolute or relative to where the function i called) and file name of a
        custom file to be used.

    Returns
    -------
    np.ndarray, ...
        All arrays saved in the synthetic_volcanoes file, same format as the input of the
        `create.Data` class.

    Raises
    ------
    NameError
        If the extension is not either 'npz' or 'nc', no files can be found and the
        variables 'yoes', 'moes', 'does' and 'tes' cannot be found.
    """
    if in_file is None:
        file = fnc.find_last_output(ext)
    elif in_file.split(".")[-1] == "npz":
        file = fnc.find_file("".join(in_file.split(".")[:-1]) + ".nc")
    else:
        file = fnc.find_file(in_file)
    if "nc" not in ext:
        raise NameError(
            "Data arrays cannot be found. "
            + f"Extension was {ext} = , but should be `nc`."
        )

    with xr.open_dataset(file, decode_times=False) as f:
        yoes = f.variables["Year_of_Emission"].data
        moes = f.variables["Month_of_Emission"].data
        does = f.variables["Day_of_Emission"].data
        tes = f.variables["Total_Emission"].data
        eruptions = f.variables["Eruption"].data
        lats = f.variables["Latitude"].data
        lons = f.variables["Longitude"].data
        veis = f.variables["VEI"].data
        miihs = f.variables["Minimum_Injection_Height"].data
        mxihs = f.variables["Maximum_Injection_Height"].data
    return eruptions, yoes, moes, does, lats, lons, tes, veis, miihs, mxihs
