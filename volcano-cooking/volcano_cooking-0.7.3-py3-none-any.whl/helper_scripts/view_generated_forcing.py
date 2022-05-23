"""Load and view the generated forcing.

This script will create a plot of the forcing, i.e. total emission vs time. The last saved
file is used unless a file is specified explicitly.

Providing a custom file means you can view any forcing so long as it is saved in the same
format that the synthetically created files are.
"""

import datetime
import os
import sys
from typing import List, Optional, Tuple

import cftime
import cosmoplots
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

import volcano_cooking.helper_scripts.functions as fnc


def view_forcing(
    ext: Optional[str] = None,
    in_file: Optional[str] = None,
    width: int = 2,
    style: str = "connected",
    dark: bool = False,
    save: bool = False,
    return_fig: bool = False,
) -> Optional[plt.Figure]:
    """View the forcing found in the generated total emission against time.

    Parameters
    ----------
    ext: str
        Extension of the file type used. Valid values are 'npz' and 'nc'.
    in_file: str, optional
        Full path (absolute or relative to where the function i called) and file name of
        a custom file to be used.
    width: int
        Width of the plot in number of columns. Default is 2.
    style: str
        Style of the plot. Default is 'connected'.
    dark: bool
        Plot with dark background. Defaults to False
    save: bool
        Save the plot. Defaults to False.
    return_fig: bool
        Return the figure. Defaults to False.

    Returns
    -------
    plt.Figure
        The figure of the plot.
    """
    _FIG_STD_ = cosmoplots.set_rcparams_dynamo(plt.rcParams, num_cols=width)
    t, tes = frc_datetime2float(ext, in_file)
    if dark:
        plt.style.use("dark_background")
    fig = plt.figure()
    ax = fig.add_axes(_FIG_STD_)
    if style == "connected":
        ax.plot(t, tes, "+-", color="r")
    elif style == "bars":
        bar_width = (t[-1] - t[0]) * 0.005
        ax.bar(t, tes, color="r", width=bar_width)
    else:
        ax.plot(t, tes, "+-", color="r")
    plt.xlabel("Time")
    plt.ylabel("Total Emission")
    if save:
        filename = check_dir(".png")
        plt.savefig(filename, format="png")
        print(f"Saved to: {os.path.join(os.getcwd(), filename)}")
    if return_fig:
        return plt.gcf()
    plt.show()
    return None


def frc_datetime2float(
    ext: Optional[str] = None, in_file: Optional[str] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """Convert time axis from datetime to float.

    Parameters
    ----------
    ext: str
        Extension of the file type used. Valid values are 'npz' and 'nc'.
    in_file: str, optional
        Full path (absolute or relative to where the function i called) and file name of a
        custom file to be used.

    Returns
    -------
    np.ndarray:
        Time axis of the input file
    np.ndarray:
        Values of the input file

    Raises
    ------
    ValueError
        If the date created fails to be formatted from ints to string and datetime objects
    """
    if ext is None and in_file is None:
        yoes, moes, does, tes = load_forcing(".nc", in_file=in_file)
    elif isinstance(ext, str):
        yoes, moes, does, tes = load_forcing(ext, in_file=in_file)
    elif isinstance(in_file, str) and in_file.endswith((".nc", ".npz")):
        ext = in_file.split(".")[-1]
        yoes, moes, does, tes = load_forcing(ext, in_file=in_file)
    else:
        raise ValueError(f"This file cannot be viewed: {in_file} = ")

    dates: List[datetime.datetime] = []
    dates_ap: List[str] = []
    d_app = dates.append
    d_ap_app = dates_ap.append
    for y, m, d in zip(yoes, moes, does):
        y = str("0" * (4 - len(str(y)))) + f"{y}"
        m = str("0" * (2 - len(str(m)))) + f"{m}"
        d = str("0" * (2 - len(str(d)))) + f"{d}"
        if len(y) != 4 or len(m) != len(d) != 2:
            raise ValueError(
                "Year, month and/or day is not formatted properly. "
                + f"{len(y)} = , {len(m)} = , {len(d)} = , need 4, 2, 2."
            )
        d_app(datetime.datetime.strptime(f"{y}{m}{d}", "%Y%m%d"))
        d_ap_app(f"{y}-{m}-{d}")

    shift = dates_ap[0][:4]
    t_0 = f"{shift}-01-01 00:00:00"
    t = (
        cftime.date2num(
            dates, f"days since {t_0}", calendar="noleap", has_year_zero=True
        )
        + float(shift) * 365
    ) / 365
    return t, tes


def check_dir(ext: str) -> str:
    """Check if the directory exist and there is no other file with the same name.

    Parameters
    ----------
    ext: str
        The file ending

    Returns
    -------
    str
        The path and name of the file that can be created
    """
    if ext[0] == ".":
        ext = ext[1:]
    d = os.path.join("data", "output")
    if not os.path.isdir(d):
        os.makedirs(d)
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    out_file = os.path.join(d, f"synthetic_volcanoes_{now}.{ext}")
    if os.path.isfile(out_file):
        sys.exit(f"The file {out_file} already exists.")
    return out_file


def load_forcing(
    ext: str, in_file: Optional[str] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load variables from the last saved file of given extension.

    Data about the date and total emission found in either the last npz or nc file.

    Parameters
    ----------
    ext: str
        Extension of the file that should be used
    in_file: str, optional
        Full path (absolute or relative to where the function i called) and file name of a
        custom file to be used.

    Returns
    -------
    np.ndarray, np.ndarray, np.ndarray, np.ndarray
        Dates and forcing (total emissions) is returnd in the order years, months, days,
        total emission

    Raises
    ------
    NameError
        If the extension is not either 'npz' or 'nc', no files can be found and the
        variables 'yoes', 'moes', 'does' and 'tes' cannot be found.
    """
    if in_file is None:
        file = fnc.find_last_output(ext)
    else:
        file = fnc.find_file(in_file)
    if "npz" in ext:
        with np.load(file, "r", allow_pickle=True) as f:
            yoes = f["yoes"]
            moes = f["moes"]
            does = f["does"]
            tes = f["tes"]
            f.close()
    elif "nc" in ext:
        f = xr.open_dataset(file, decode_times=False)
        yoes = f.variables["Year_of_Emission"].data
        moes = f.variables["Month_of_Emission"].data
        does = f.variables["Day_of_Emission"].data
        tes = f.variables["Total_Emission"].data
    else:
        raise NameError(
            "Names 'yoes', 'moes', 'does' and 'tes' are not found. "
            + f"Extension was {ext} = , but shuld be 'npz' or 'nc'."
        )

    return yoes, moes, does, tes


def main():
    # Remember to remove plt.show() when timing
    # import timeit
    # t1 = timeit.timeit(lambda: view_forcing("nc"), number=1000)
    # t2 = timeit.timeit(lambda: view_forcing("npz"), number=1000)
    # print(f"{t1 = }, {t2 = }")
    view_forcing("npz")  # Twice as fast as nc


if __name__ == "__main__":
    main()
