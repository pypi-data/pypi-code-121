"""
.. _utils:

Utilities
---------

Provides miscellaneous utility functions.
"""
import shlex

from pathlib import Path
from typing import Dict, Sequence, Tuple, Union

import numpy as np
import pandas as pd

from cpymad.madx import Madx
from loguru import logger

from pyhdtoolkit.cpymadtools.lhc import get_lhc_tune_and_chroma_knobs
from pyrws.constants import EXPORT_TWISS_COLUMNS

Array = Union[np.ndarray, pd.Series]

# ----- Querying Utilities ----- #


def get_triplets_powering_knobs(madx: Madx, ip: int) -> Dict[str, float]:
    """
    Returns the triplets powering knob values at the given IP.

    Args:
        madx (cpymad.madx.Madx): an instantiated `~cpymad.madx.Madx` object.
        ip (int): the IP for which to get the triplets powering knob values for.

    Returns:
        A `dict` of the knob names and their values.
    """
    logger.debug(f"Querying triplets powering knob values around IP{ip:d}.")
    right_knob, left_knob = f"kqx.r{ip:d}", f"kqx.l{ip:d}"  # IP triplet default knobs (no trims)
    return {right_knob: madx.globals[right_knob], left_knob: madx.globals[left_knob]}


def get_independent_quadrupoles_powering_knobs(madx: Madx, quad_numbers: Sequence[int], ip: int, beam: int) -> Dict[str, float]:
    """
    Returns the powering knob values for the provided quadrupoles around the given IP.

    Args:
        madx (cpymad.madx.Madx): an instantiated `~cpymad.madx.Madx` object.
        quad_numbers (Sequence[int]): quadrupoles to get the powering for, by number
            (aka position from IP).
        ip (int): the IP around which to get the quadrupoles powering knobs for.

    Returns:
        A `dict` of the knob names and their values.
    """
    logger.debug(f"Querying powering knob values for quadrupoles {quad_numbers} around IP{ip:d}.")
    powering_knobs = {}
    sides = ("r", "l")
    for quad in quad_numbers:
        for side in sides:
            logger.trace(f"Getting powering knob for Q{quad}{side.upper()}{ip}")
            knob = f"kq{'t' if quad >= 11 else ''}{'l' if quad == 11 else ''}{quad}.{side}{ip}b{beam}"
            powering_knobs[knob] = madx.globals[knob]
    return powering_knobs


def get_tunes_and_chroma_knobs(madx: Madx, beam: int, telescopic_squeeze: bool = True) -> Dict[str, float]:
    """
    Returns the tunes and chroma knobs.

    Args:
        madx (cpymad.madx.Madx): an instantiated `~cpymad.madx.Madx` object.
        beam (int): the beam number to get knob values for.
        telescopic_squeeze (bool): if set to `True`, returns the knobs for Telescopic
            Squeeze configuration. Defaults to `True` to reflect run III scenarios.

    Returns:
        A `dict` of the knob names and their values.
    """
    logger.debug("Querying tune and chroma knobs")
    knobs = get_lhc_tune_and_chroma_knobs("lhc", beam, telescopic_squeeze)
    return {knob_name: madx.globals[knob_name] for knob_name in knobs}


# ----- Computing Utilities ----- #


def betabeating(nominal: Array, modified: Array) -> Array:
    """
    Compute the beta-beating from the provided arrays.

    Args:
        nominal (Union[np.ndarray, pd.Series]): the nominal beta values.
        modified (Union[np.ndarray, pd.Series]): the beta values to get the
            beta-beating for.

    Returns:
        A new array with the computed beta-beating values.
    """
    return (modified - nominal) / nominal


def add_betabeating_columns(dataframe: pd.DataFrame, nominal: pd.DataFrame) -> pd.DataFrame:
    """
    Adds coupling ``RDTs`` :math:`\\f_{1001}` and :math:`\\f_{1010}` as well as beta-beating
    columns to the dataframe.

    Args:
        dataframe (pd.DataFrame): the `~pd.DataFrame` to add the columns to.
        nominal (pd.DataFrame): the `~pd.DataFrame` with reference values for the
            beta-beating calculations.

    Returns:
        A copy of the original *dataframe* with the new columns added.
    """
    df = dataframe.copy(deep=True)
    df["BBX"] = betabeating(nominal.BETX, df.BETX)
    df["BBY"] = betabeating(nominal.BETY, df.BETY)
    return df


def powering_delta(nominal_knobs: Dict[str, float], modified_knobs: Dict[str, float]) -> Dict[str, float]:
    """
    Compute the delta between the modified and nominal knobs, to determine the powering
    change that should be given in LSA.

    Args:
        nominal_knobs (Dict[str, float]): a `~dict` of the nominal knobs and their values.
        modified_knobs (Dict[str, float]): a `~dict` of the modified knobs and their values.

    Returns:
        A dictionary of the knob names and powering delta from the modifying scenario to the
        nominal scenario.
    """
    logger.debug("Computing the delta between modified and nominal knobs.")
    assert nominal_knobs.keys() == modified_knobs.keys()
    return {key: modified_knobs[key] - nominal_knobs[key] for key in nominal_knobs.keys()}


# ----- Subsampling Utilities ----- #


def only_export_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a sub-selection of the *dataframe* with only certain columns,
    meant for writing to disk.

    Args:
        dataframe (pd.DataFrame): the `~pd.DataFrame` to do a selection of columns for.

    Returns:
        A copy of the original *dataframe* with only the desired columns in.
    """
    df = dataframe.reset_index().copy(deep=True)
    intersect_columns = [val for val in df.columns if val in EXPORT_TWISS_COLUMNS]
    df = df[intersect_columns]
    return df


def only_monitors(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a sub-selection of the *dataframe* with only rows corresponding to monitor
    elements (aka BPMs), meant for writing to disk.

    Args:
        dataframe (pd.DataFrame): the `~pd.DataFrame` to do a selection of columns for.

    Returns:
        A copy of the original *dataframe* with only the desired rows in.
    """
    df = dataframe.copy(deep=True)
    df = df[df.KEYWORD == "monitor"]
    return df


# ----- FileSystem Utilities ----- #


def prepare_output_directories(outputdir: Path) -> Tuple[Dict[str, Path], Dict[str, Path]]:
    """
    Creates the proper directories where the output files will be written.

    Args:
        outputdir (Path): the path to the main output directory, as given by the user
            at the command line.

    Returns:
        A `dict` for each beam, with as keys the `~pathlib.Path` objects to the created output
        directories. In order, these are for main directory, tfs files dir, knobs dir and plots
        dir. The keys or the `dict` are ``main``, ``tfs``, ``knobs`` and ``plots``.
    """
    logger.debug(f"Creating output directory at '{outputdir.absolute()}'.")
    outputdir.mkdir(parents=True, exist_ok=True)

    # ----- Beam 1 Directories ----- #
    beam1_dir = outputdir / "BEAM1"
    logger.trace(f"Creating BEAM directory at '{beam1_dir.absolute()}'.")
    beam1_dir.mkdir(parents=True, exist_ok=True)

    beam1_tfs_dir = beam1_dir / "TFS"
    logger.trace(f"Creating TFS directory at '{beam1_tfs_dir.absolute()}'.")
    beam1_tfs_dir.mkdir(parents=True, exist_ok=True)

    beam1_knobs_dir = beam1_dir / "KNOBS"
    logger.trace(f"Creating B1 knobs sub-directory at '{beam1_knobs_dir.absolute()}'.")
    beam1_knobs_dir.mkdir(parents=True, exist_ok=True)

    beam1_plots_dir = beam1_dir / "PLOTS"
    logger.trace(f"Creating B1 plots sub-directory at '{beam1_plots_dir.absolute()}'.")
    beam1_plots_dir.mkdir(parents=True, exist_ok=True)

    # ----- Beam 2 Directories ----- #
    beam2_dir = outputdir / "BEAM2"
    logger.trace(f"Creating BEAM directory at '{beam2_dir.absolute()}'.")
    beam2_dir.mkdir(parents=True, exist_ok=True)

    beam2_tfs_dir = beam2_dir / "TFS"
    logger.trace(f"Creating TFS directory at '{beam2_tfs_dir.absolute()}'.")
    beam2_tfs_dir.mkdir(parents=True, exist_ok=True)

    beam2_knobs_dir = beam2_dir / "KNOBS"
    logger.trace(f"Creating B2 knobs sub-directory at '{beam2_knobs_dir.absolute()}'.")
    beam2_knobs_dir.mkdir(parents=True, exist_ok=True)

    beam2_plots_dir = beam2_dir / "PLOTS"
    logger.trace(f"Creating B2 plots sub-directory at '{beam2_plots_dir.absolute()}'.")
    beam2_plots_dir.mkdir(parents=True, exist_ok=True)

    return (
        {"main": beam1_dir, "tfs": beam1_tfs_dir, "knobs": beam1_knobs_dir, "plots": beam1_plots_dir},
        {"main": beam2_dir, "tfs": beam2_tfs_dir, "knobs": beam2_knobs_dir, "plots": beam2_plots_dir},
    )


def write_knob_powering(file_path: Path, knob_dict: Dict[str, float]) -> None:
    """
    Write the absolute powering values of the given knob `~dict` to the given file.
    """
    logger.trace(f"Writing knob powering to '{file_path.absolute()}'.")
    with file_path.open("w") as knob_file:
        for knob, value in knob_dict.items():
            knob_file.write(f"{knob:<10} = {value:>22};\n")


def write_knob_delta(file_path: Path, nominal_knobs: Dict[str, float], matched_knobs: Dict[str, float]) -> None:
    """
    Figure out the delta from the matched knobs to the nominal knobs, and write it down to the given file.
    """
    deltas_dict = powering_delta(nominal_knobs, matched_knobs)
    logger.trace(f"Writing knob deltas to '{file_path.absolute()}'.")
    with file_path.open("w") as delta_file:
        for knob, delta in deltas_dict.items():
            operation: str = "-" if delta < 0 else "+"
            delta_file.write(f"{knob:<10} = {knob:>10}  {operation}  {abs(delta):>22};\n")


def load_knobs_file(filepath: Path) -> Dict[str, float]:
    """
    Loads the knob values from the file they are written in by `~.write_knob_powering`.

    Args:
        filepath (Path): `~pathlib.Path` object to the file with the saved knob values.

    Returns:
        A `~dict` of knob names and their values, in absolute powering.
    """
    logger.debug(f"Loading knob values from '{filepath.absolute()}'.")
    knob_dict = {}
    for line in filepath.read_text().splitlines():
        knob_name = shlex.split(line)[0]
        knob_value = float(shlex.split(line)[-1][:-1])  # last element is value, and we ignore the ;
        knob_dict[knob_name] = knob_value
    return knob_dict


def load_knobs_change_file(filepath: Path) -> Dict[str, float]:
    """
    Loads the knob values from the file they are written in by `~.write_knob_powering`.

    Args:
        filepath (Path): `~pathlib.Path` object to the file with the saved knob values.

    Returns:
        A `~dict` of knob names and their values, in absolute powering.
    """
    logger.debug(f"Loading knob values from '{filepath.absolute()}'.")
    knob_dict = {}
    for line in filepath.read_text().splitlines():
        knob_name = shlex.split(line)[0]
        sign, delta = shlex.split(line)[-2:]
        delta = delta.replace(";", "")  # we ignore the ; at the end of the line
        knob_value = float(sign + delta)  # last element is value, and we ignore the ;
        knob_dict[knob_name] = knob_value
    return knob_dict
