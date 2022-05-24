"""Compare values in two .nc files.

A quick way of comparing all relevant information found in the forcing data file used by
CESM2 (or similar) with the values stored in the file with synthetic data. The latest
created file with synthetic data is used.
"""

import pprint

import xarray as xr

import volcano_cooking.helper_scripts.functions as fnc


def compare_nc_files() -> None:
    original_file = fnc.find_original()
    synthetic_file = fnc.find_last_output("nc")

    forcing = xr.open_dataset(original_file, decode_times=False)
    my_forcing = xr.open_dataset(synthetic_file, decode_times=False)
    files = [forcing, my_forcing]

    # Just np.arange(241), one integer for each volcano
    print("Eruption_Number")
    pprint.pprint([f["Eruption_Number"] for f in files])
    print("")
    # print(forcing)
    # print(forcing.data_vars.keys())
    var_list = [
        "Eruption",
        "VEI",
        "Year_of_Emission",
        "Month_of_Emission",
        "Day_of_Emission",
        "Latitude",
        "Longitude",
        "Total_Emission",
        "Maximum_Injection_Height",
        "Minimum_Injection_Height",
    ]
    for v in var_list:
        print(v)
        pprint.pprint([f.variables[v].data for f in files])
        print("")


def main():
    compare_nc_files()


if __name__ == "__main__":
    main()
