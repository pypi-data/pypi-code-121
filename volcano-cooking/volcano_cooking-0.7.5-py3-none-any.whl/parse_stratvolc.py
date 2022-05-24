"""Script to parse forcing files with the `stratvolc` data attribute."""

import os
import sys

import matplotlib.pyplot as plt
import xarray as xr


def sum_over_space():
    """Sum over latitude and longitude.

    Raises
    ------
    TypeError
        If the file extension is not .nc.
    FileNotFoundError
        If the file does not exist.
    """
    # Check file path
    data = sys.stdin.readlines()
    filename = data[0].strip("\n")
    if not isinstance(filename, str) or filename[-3:] != ".nc":
        raise TypeError(f"Are you sure {filename} is a valid .nc file?")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Cannot find file named {filename}.")
    # base = filename[:-3]
    ds = xr.open_dataset(filename, decode_times=False, chunks={"time": 100})
    only_time = ds.sum(dim=("lat", "lon", "altitude"))
    ds.close()
    if hasattr(ds, "date") and hasattr(ds, "datesec"):
        times = (only_time.date.values + only_time.datesec.values / 3600 / 24) / 10000
        plt.plot(times, only_time.stratvolc, "-o")
    elif hasattr(ds, "date"):
        times = only_time.date / 10000
        plt.plot(times, only_time.stratvolc, "-o")
    else:
        plt.plot(only_time.stratvolc, "-o")
    plt.show()


if __name__ == "__main__":
    sum_over_space()
