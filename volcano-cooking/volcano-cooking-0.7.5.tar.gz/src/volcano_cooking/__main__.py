"""Main file to run the program."""

import os
import ssl
import subprocess
import sys
from typing import List, Optional

import click
import wget

import volcano_cooking.configurations.shift_eruption_to_date as shift_eruption_to_date
import volcano_cooking.synthetic_volcanoes as sv
from volcano_cooking import __version__


@click.command()
@click.version_option(version=__version__)
@click.option(
    "-o",
    "--option",
    count=True,
    show_default=True,
    help="Set the data creation option. "
    + "The default is option 0, -o gives option 1.",
)
@click.option(
    "frc",
    "-f",
    type=int,
    default=0,
    show_default=True,
    help="Choose what forcing generator to use. "
    + "See volcano-cooking --lst for a list of all available generators.",
)
@click.option(
    "init_year",
    "-init",
    type=int,
    default=[1850, 1, 15],
    show_default=True,
    multiple=True,
    help="Set the first model year. If used with 'shift-eruption-to-date', "
    + "this becomes the year of the eruption and three instances can be used to specify "
    + "year, month, and day of the eruption. ",
)
@click.option(
    "size",
    "-s",
    type=int,
    default=3000,
    show_default=True,
    help="Set the number of volcanoes to generate.",
)
@click.option(
    "--lst/--no-lst",
    default=False,
    show_default=True,
    type=bool,
    help="Show a list of available forcing generators.",
)
@click.option(
    "--shift-eruption-to-date",
    "shift_eruption",
    is_flag=False,
    flag_value=True,
    default=False,
    show_default=True,
    type=str,
    help="Shift eruptions of provided file to 'init_year'. "
    + "If no file is provided, the last created file is used.",
)
@click.option(
    "--run-ncl",
    "run_ncl",
    is_flag=True,
    default=False,
    show_default=True,
    type=bool,
    help="Run the shell script that generate forcing from emission file.",
)
@click.option(
    "--package-last",
    "package_last",
    is_flag=True,
    default=False,
    show_default=True,
    type=bool,
    help="Move all last created files to a 'source-file' directory.",
)
def main(
    frc: int,
    init_year: List[int],
    size: int,
    lst: bool,
    option: int,
    shift_eruption: str,
    run_ncl: bool,
    package_last: bool,
) -> None:
    if lst:
        for cl in sv.__GENERATORS__:
            print(f"{cl}: {sv.__GENERATORS__[cl].__name__}")
        return
    if run_ncl:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        shell_file = f"{this_dir}/create_cesm_frc.sh"
        subprocess.call(["sh", shell_file, this_dir])
        return
    if package_last:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        shell_file = f"{this_dir}/package_last.sh"
        subprocess.call(["sh", shell_file])
        return
    _init_year = [1850, 1, 15]
    _init_year[: len(init_year)] = init_year
    if shift_eruption == "False":
        if option == 1:
            location = os.path.join(os.getcwd(), "data", "originals")
            file = "VolcanEESMv3.11_SO2_850-2016_Mscale_Zreduc_2deg_c191125.nc"
            if not os.path.isfile(os.path.join(location, file)):
                get_forcing_file(file)
            file = "fv_1.9x2.5_L30.nc"
            if not os.path.isfile(os.path.join(os.getcwd(), file)):
                get_forcing_file(
                    file,
                    url="https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata"
                    + "/atm/cam/coords/fv_1.9x2.5_L30.nc",
                    not_forcing=True,
                )
        sv.create_volcanoes(
            size=size, init_year=_init_year[0], version=frc, option=option
        )
    elif shift_eruption == "True":
        shift_eruption_to_date.shift_eruption_to_date(tuple(_init_year), None)
    else:
        shift_eruption_to_date.shift_eruption_to_date(tuple(_init_year), shift_eruption)


def get_forcing_file(
    file: str, url: Optional[str] = None, not_forcing: bool = False
) -> None:
    """Download the original forcing file.

    It will be placed in `data/originals` inside the current working directory.

    Parameters
    ----------
    file: str
        The filename the file to download will be saved as.
    url: str, optional
        Provide the full url for where to download the file.
    not_forcing: bool
        If some other file is downloaded, use generic text without file size warning.
    """
    here = os.path.join(os.getcwd(), "data", "originals")
    os.makedirs(here, exist_ok=True)
    print(f"{file} was not found in {here}.")
    query_ = "Do you want to download the original forcing file? (2.2 GB)"
    query = f"Do you want to download '{file}'?" if not_forcing else query_
    if click.confirm(query):
        url_ = (
            "https://svn-ccsm-inputdata.cgd.ucar.edu/trunk/inputdata/atm/cam/chem"
            + "/stratvolc/VolcanEESMv3.11_SO2_850-2016_Mscale_Zreduc_2deg_c191125.nc"
        )
        url = url_ if url is None else url
        ssl._create_default_https_context = ssl._create_unverified_context
        wget.download(url, os.path.join(here, file))
        print("")
        if os.path.isfile(os.path.join(here, file)):
            print(f"Successfully downloaded {os.path.join(here, file)}.")
        else:
            sys.exit(
                "Failed to place the file in the correct directory. "
                + f"You may check if the file '{file}' was downloaded somewhere else, "
                + f"and if so place it in {here}."
            )
    else:
        sys.exit("Okay, I won't download it. Exiting gracefully.")
