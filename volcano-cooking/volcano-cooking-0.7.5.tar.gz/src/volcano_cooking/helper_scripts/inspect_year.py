"""Print out the data from all ten variables in a table, starting at any given year."""

import xarray as xr

import volcano_cooking.helper_scripts.functions as fnc


def inspect_year() -> None:
    year = 1865

    file = fnc.find_last_output("nc")
    print(file)

    f = xr.open_dataset(file, decode_times=False)

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
    var_list_short = [
        "Eru",
        "VEI",
        "YoE",
        "MoE",
        "DoE",
        "Lat",
        "Lon",
        "TE",
        "MaxIH",
        "MinIH",
    ]

    col_width = 12
    print("".join(element.ljust(col_width) for element in var_list_short))
    for i, y in enumerate(f.variables["Year_of_Emission"].data):
        if y <= year:
            p_list = [str(f.variables[var_list[j]].data[i])[:10] for j in range(10)]
            print("".join(element.ljust(col_width) for element in p_list))


def main():
    inspect_year()


if __name__ == "__main__":
    main()
