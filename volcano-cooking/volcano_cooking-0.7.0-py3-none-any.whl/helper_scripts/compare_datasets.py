"""Compare two xarray datasets' dimensions and variables."""

import os
from typing import List, Union

import xarray as xr


def compare_datasets(*args: Union[str, xr.Dataset]) -> None:
    """Compare any number of xarray datasets.

    This function checks the dimensions; their names and if it has variable attributes,
    the variables; their size and their attributes.

    Parameters
    ----------
    args: Union[str, xr.Dataset]
        Any number of paths to netCDF files or xarray dataset objects

    Raises
    ------
    TypeError
        If the input parameters are not of type `str` or `xr.Dataset`
    """
    xr_list: List[xr.Dataset] = []
    xr_app = xr_list.append
    for arr in args:
        if isinstance(arr, str):
            if not os.path.isfile(arr):
                raise TypeError(f"{arr} is not a file")
            xr_app(xr.open_dataset(arr, decode_times=False))
        elif isinstance(arr, xr.Dataset):
            xr_app(arr)
        else:
            raise TypeError(
                f"Object is type {type(arr)}. Must be 'str' or 'xr.Dataset'."
            )

    print("Checking dimensions...")
    for i, arr in enumerate(xr_list):
        print(f"\tArray {i}:\t{arr.dims}")

    print("\nChecking coordinates...")
    for i, arr in enumerate(xr_list):
        print(f"\tArray {i}:\t{list(arr.coords)}")
        # print(f"\tArray {i}:\t{arr.coords}")

    print("\nChecking variables...")
    for i, arr in enumerate(xr_list):
        print(
            f"\tArray {i}:\t{[f'{v}, {arr[v].dims}, {arr[v].shape}' for v in arr.data_vars]}"
        )
        # print(f"\tArray {i}:\t{arr.data_vars}")
        for v in arr.data_vars:
            print(f"\t\t{list(arr[v].attrs)}")

    print("\nChecking attributes...")
    for i, arr in enumerate(xr_list):
        print(f"\tArray {i}:\t{list(arr.attrs)}")
