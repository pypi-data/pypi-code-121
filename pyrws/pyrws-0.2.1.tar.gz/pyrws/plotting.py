"""
.. _plotting:

Plotting Functions
------------------

Module with functions to create different plots relevant to the rigid waist shift configurations.
"""
import matplotlib
import pandas as pd

from loguru import logger
from matplotlib import pyplot as plt

# ----- Beta-Beating Plotters ----- #


def plot_waist_shift_betabeatings(axis: matplotlib.axes.Axes, dataframe: pd.DataFrame, show_ips: bool = False) -> None:
    """Plots the horizontal and vertical beta-beatings on the given *axis*.

    .. note::
        It is expected that the *dataframe* contains ``BBX`` and ``BBY`` columns, with respectively
        the horizontal and vertical beta-beating values to plot.

    Args:
        axis (matplotlib.axes.Axes): the `~matplotlib.axes.Axes` object on which to plot.
        dataframe (pd.DataFrame): the `~pd.DataFrame` containing the beta-beating values to plot along
            the longitudinal coordinate ``S``.
        show_ips (bool): if `True`, will show the IPs locations with vertical lines on the plot.
            Defaults to `False`.
    """
    logger.debug("Plotting waist shift induced beta-beating.")
    axis.plot(
        dataframe.S,
        100 * dataframe.BBX,
        "o",
        ls="",
        mfc="none",
        label=r"$\Delta \beta_x / \beta_x$",
    )
    axis.plot(
        dataframe.S,
        100 * dataframe.BBY,
        "o",
        ls="",
        mfc="none",
        label=r"$\Delta \beta_y / \beta_y$",
    )

    if show_ips:
        _highlight_ips_locations(axis, dataframe)

    axis.set_xlabel(r"$S \ [m]$")
    axis.set_ylabel(r"$\frac{\Delta \beta_{x,y}}{\beta_{x,y}} \ [\%]$")
    axis.legend()


def plot_waist_shift_betabeatings_comparison(
    axis: matplotlib.axes.Axes,
    before: pd.DataFrame,
    after: pd.DataFrame,
    column: str = "BBX",
    show_ips: bool = False,
) -> None:
    """Plots the before and after matching beta-beatings on the given *axis*.

    .. note::
        It is expected that the *before* and *after* dataframes both contain ``BBX`` and
        ``BBY`` columns, with respectively the horizontal and vertical beta-beating values
        to plot.

    Args:
        axis (matplotlib.axes.Axes): the `~matplotlib.axes.Axes` object on which to plot.
        before (pd.DataFrame): the `~pd.DataFrame` containing the beta-beating values along
            the longitudinal coordinate ``S``, for the bare waist shift implementation.
        after (pd.DataFrame): the `~pd.DataFrame` containing the beta-beating values along
            the longitudinal coordinate ``S``, for the improved waist shift implementation
            (a.k.a. after matching).
        column (str): the column to plot. Should be one of ``BBX`` or ``BBY``. Defaults to ``BBX``
            for the horizontal beta-beating.
        show_ips (bool): if `True`, will show the IPs locations with vertical lines on the plot.
            Defaults to `False`.
    """
    assert column in ("BBX", "BBY")
    logger.debug("Plotting waist shift induced beta-beating before and after matching.")
    axis.plot(before.S, 100 * before[column], "o", ls="", mfc="none", label="Bare Waist Shift")
    axis.plot(
        after.S,
        100 * after[column],
        "o",
        ls="",
        mfc="none",
        label="Improved Waist Shift",
    )

    if show_ips:
        _highlight_ips_locations(axis, before)

    ylabel = r"$\frac{\Delta \beta_x}{\beta_x} \ [\%]$" if column == "BBX" else r"$\frac{\Delta \beta_y}{\beta_y} \ [\%]$"
    axis.set_ylabel(ylabel)
    axis.legend()


# ----- Beta Functions Plotters ----- #


def plot_betas_comparison(
    axis: matplotlib.axes.Axes,
    nominal: pd.DataFrame,
    before: pd.DataFrame,
    after: pd.DataFrame,
    column: str = "BETX",
    show_ips: bool = False,
) -> None:
    """
    Plots the ..math:`\beta` functions across the machine for the nominal, bare waist shift
    and improved waist shift scenarii on the given *axis*.

    Args:
        axis (matplotlib.axes.Axes): the `~matplotlib.axes.Axes` object on which to plot.
        nominal (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the nominal
            model.
        before (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the bare waist
            shift implementation.
        after (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the improved waist
            shift implementation.
        column (str): the column to plot. Should be one of ``BETX`` or ``BETY``. Defaults to ``BETX``
            for the horizontal beta-functions.
        show_ips (bool): if `True`, will show the IPs locations with vertical lines on the plot.
            Defaults to `False`.
    """
    assert column in ("BETX", "BETY")
    logger.debug("Plotting beta functions for nominal, bare waist shift and improved waist shift scenarii.")
    axis.plot(
        nominal.S,
        nominal[column],
        ls="--",
        mfc="none",
        label=r"$\beta_x^{nominal}$" if column == "BETX" else r"$\beta_y^{nominal}$",
    )
    axis.plot(
        before.S,
        before[column],
        ls="--",
        mfc="none",
        label=r"$\beta_x^{bare}$" if column == "BETX" else r"$\beta_y^{bare}$",
    )
    axis.plot(
        after.S,
        after[column],
        ls="--",
        mfc="none",
        label=r"$\beta_x^{improved}$" if column == "BETX" else r"$\beta_y^{improved}$",
    )

    if show_ips:
        _highlight_ips_locations(axis, nominal)

    axis.set_ylabel(r"$\beta_{x} \ [m]$" if column == "BETX" else r"$\beta_{y} \ [m]$")
    axis.legend()


def plot_betas_deviation(
    axis: matplotlib.axes.Axes,
    nominal: pd.DataFrame,
    before: pd.DataFrame,
    after: pd.DataFrame,
    column: str = "BETX",
    show_ips: bool = False,
) -> None:
    """
    Plots the ..math:`\beta` functions deviation from the nominal case across the machine for
    the bare waist shift and improved waist shift scenarii on the given *axis*.

    Args:
        axis (matplotlib.axes.Axes): the `~matplotlib.axes.Axes` object on which to plot.
        nominal (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the nominal
            model.
        before (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the bare waist
            shift implementation.
        after (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the improved waist
            shift implementation.
        column (str): the column to plot. Should be one of ``BETX`` or ``BETY``. Defaults to ``BETX``
            for the horizontal beta-functions.
        show_ips (bool): if `True`, will show the IPs locations with vertical lines on the plot.
            Defaults to `False`.
    """
    assert column in ("BETX", "BETY")
    logger.debug("Plotting beta functions deviation from nominal, for bare waist shift and improved waist shift scenarii.")
    axis.plot(
        before.S,
        before[column] - nominal[column],
        ls="--",
        mfc="none",
        label=r"$\Delta \beta_x^{bare}$" if column == "BETX" else r"$\Delta \beta_y^{bare}$",
    )
    axis.plot(
        after.S,
        after[column] - nominal[column],
        ls="--",
        mfc="none",
        label=r"$\Delta \beta_x^{improved}$" if column == "BETX" else r"$\Delta \beta_y^{improved}$",
    )

    if show_ips:
        _highlight_ips_locations(axis, nominal)

    axis.set_ylabel(r"$\Delta \beta_{x} \ [m]$" if column == "BETX" else r"$\Delta \beta_{y} \ [m]$")
    axis.legend()


# ----- Phase Advance Plotters ----- #


def plot_phase_advances_comparison(
    axis: matplotlib.axes.Axes,
    nominal: pd.DataFrame,
    before: pd.DataFrame,
    after: pd.DataFrame,
    column: str = "MUX",
    show_ips: bool = False,
) -> None:
    """
    Plots the phase advances (..math:`\mu_{x,y}`) across the machine for the nominal, bare waist
    shift and improved waist shift scenarii on the given *axis*.

    Args:
        axis (matplotlib.axes.Axes): the `~matplotlib.axes.Axes` object on which to plot.
        nominal (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the nominal
            model.
        before (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the bare waist
            shift implementation.
        after (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the improved waist
            shift implementation.
        column (str): the column to plot. Should be one of ``MUX`` or ``MUY``. Defaults to ``MUX``
            for the horizontal phase advances.
        show_ips (bool): if `True`, will show the IPs locations with vertical lines on the plot.
            Defaults to `False`.
    """
    assert column in ("MUX", "MUY")
    logger.debug("Plotting phase advances for nominal, bare waist shift and improved waist shift scenarii.")
    axis.plot(
        nominal.S,
        nominal[column],
        ls="--",
        mfc="none",
        label=r"$\mu_x^{nominal}$" if column == "MUX" else r"$\mu_y^{nominal}$",
    )
    axis.plot(
        before.S,
        before[column],
        ls="--",
        mfc="none",
        label=r"$\mu_x^{bare}$" if column == "MUX" else r"$\mu_y^{bare}$",
    )
    axis.plot(
        after.S,
        after[column],
        ls="--",
        mfc="none",
        label=r"$\mu_x^{improved}$" if column == "MUX" else r"$\mu_y^{improved}$",
    )

    if show_ips:
        _highlight_ips_locations(axis, nominal)

    axis.set_ylabel(r"$\mu_{x} \ [2 \pi]$" if column == "MUX" else r"$\mu_{y} \ [2 \pi]$")
    axis.legend()


def plot_phase_differences(
    axis: matplotlib.axes.Axes,
    nominal: pd.DataFrame,
    before: pd.DataFrame,
    after: pd.DataFrame,
    show_ips: bool = False,
) -> None:
    """
    Plots the phase advances (..math:`\mu_{x,y}`) across the machine for the nominal, bare waist
    shift and improved waist shift scenarii on the given *axis*.

    .. hint::
        The value ..math:`\mu_x - \muy` is interesting as it is driving the exponential term in the
        calculation of the difference resonance ..math:`f_{1001}`.

    Args:
        axis (matplotlib.axes.Axes): the `~matplotlib.axes.Axes` object on which to plot.
        nominal (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the nominal
            model.
        before (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the bare waist
            shift implementation.
        after (pd.DataFrame): the `~pd.DataFrame` with ``TWISS`` functions from the improved waist
            shift implementation.
        column (str): the column to plot. Should be one of ``MUX`` or ``MUY``. Defaults to ``MUX``
            for the horizontal phase advances.
        show_ips (bool): if `True`, will show the IPs locations with vertical lines on the plot.
            Defaults to `False`.
    """
    logger.debug("Plotting phase advances for nominal, bare waist shift and improved waist shift scenarii.")
    axis.plot(nominal.S, nominal.MUX - nominal.MUY, ls="--", mfc="none", label="Nominal")
    axis.plot(before.S, before.MUX - before.MUY, ls="--", mfc="none", label="Bare Waist Shift")
    axis.plot(
        after.S,
        after.MUX - after.MUY,
        ls="--",
        mfc="none",
        label="Improved Waist Shift",
    )

    if show_ips:
        _highlight_ips_locations(axis, nominal)

    axis.set_ylabel(r"$\mu_{x} - \mu_{y} \ [2 \pi]$")
    axis.legend()


# ----- Helpers ----- #


def _highlight_ips_locations(axis: matplotlib.axes.Axes, dataframe: pd.DataFrame) -> None:
    """
    Figures out the ``S`` coordinate of IP[1258] locations from the given *dataframe* and adds
    vertical lines for each one on the provided *axis*.
    """
    dfcopy = dataframe.reset_index()
    ips_dataframe = dfcopy[dfcopy.NAME.str.contains("^IP[1258]$", case=False)].reset_index(drop=True)
    for row_tuple in ips_dataframe.itertuples():
        axis.axvline(
            row_tuple.S,
            color=plt.get_cmap("Set1").colors[row_tuple.Index],
            ls="--",
            lw=2,
            label=row_tuple.NAME.upper(),
        )
