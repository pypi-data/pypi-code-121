"""Compare two variables across the original and synthetic forcing files."""

import matplotlib.pyplot as plt
import xarray as xr

import volcano_cooking.helper_scripts.functions as fnc


def x_vs_y() -> None:
    yax_file = fnc.find_original()
    xax_file = fnc.find_last_output("nc")

    f1 = xr.open_dataset(xax_file, decode_times=False)
    l1 = "Synthetic"
    f2 = xr.open_dataset(yax_file, decode_times=False)
    l2 = "Data set"

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

    x_ax = 7
    y_ax = 8
    x1 = f1.variables[var_list[x_ax]].data
    y1 = f1.variables[var_list[y_ax]].data
    x2 = f2.variables[var_list[x_ax]].data
    y2 = abs(f2.variables[var_list[y_ax]].data)

    plt.figure(figsize=(12, 9))
    plt.loglog()
    shift = 0.05 if x_ax == 1 else 0
    plt.scatter(x1 - shift, y1, marker="d", label=l1)
    plt.scatter(x2 + shift, y2, marker="x", label=l2)
    plt.xlabel(var_list[x_ax])
    plt.ylabel(var_list[y_ax])
    plt.legend()
    plt.show()


def main():
    x_vs_y()


if __name__ == "__main__":
    main()
