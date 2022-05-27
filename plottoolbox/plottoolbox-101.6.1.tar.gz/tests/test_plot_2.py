# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
from tstoolbox import tstoolbox

from plottoolbox import plottoolbox

# Pull this in once.
df = tstoolbox.aggregate(
    agg_interval="D", clean=True, input_ts="tests/02234500_65_65.csv"
)
# Pull this in once.
dfa = tstoolbox.aggregate(
    agg_interval="A", clean=True, input_ts="tests/02234500_65_65.csv"
)
dfa = tstoolbox.equation(
    "x1*120@x2", input_ts=dfa, output_names=["Elevation::mean", "Flow::mean"]
)


@pytest.mark.mpl_image_compare(tolerance=6)
def test_double_mass():
    plt.close("all")
    return plottoolbox.double_mass(
        clean=True,
        input_ts="tests/02234500_65_65.csv",
        ofilename=None,
        plot_styles="classic",
    )


@pytest.mark.mpl_image_compare(tolerance=6)
def test_double_mass_mult():
    plt.close("all")
    return plottoolbox.double_mass(
        columns=[2, 3, 3, 2],
        input_ts="tests/data_daily_sample.csv",
        ofilename=None,
        plot_styles="classic",
    )


@pytest.mark.mpl_image_compare(tolerance=6)
def test_double_mass_marker():
    plt.close("all")
    return plottoolbox.double_mass(
        columns=[2, 3, 3, 2],
        linestyles=" ",
        markerstyles="auto",
        input_ts="tests/data_daily_sample.csv",
        ofilename=None,
        plot_styles="classic",
    )


@pytest.mark.mpl_image_compare(tolerance=6)
def test_boxplot():
    plt.close("all")
    xdf = tstoolbox.read(
        "tests/02234500_65_65.csv",
        "tests/data_gainesville_daily_precip.csv",
        clean=True,
        append="combine",
    )
    return plottoolbox.boxplot(
        input_ts=xdf,
        clean=True,
        columns=[2, 3],
        ofilename=None,
        plot_styles="classic",
    )


# @pytest.mark.mpl_image_compare(tolerance=6)
# def test_scatter_matrix():
#     plt.close("all")
#     return plottoolbox.scatter_matrix(
#         clean=True,
#         input_ts="tests/02234500_65_65.csv",
#         ofilename=None,
#         plot_styles="classic",
#     )


@pytest.mark.mpl_image_compare(tolerance=6)
def test_lag_plot():
    plt.close("all")
    return plottoolbox.lag_plot(
        columns=1, input_ts=df, ofilename=None, plot_styles="classic"
    )


# Can't have a bootstrap test since random selections are made.
# @image_comparison(baseline_images=['bootstrap'],
#                   tol=0.019, extensions=['png'])
# def test_bootstrap():
#     return plottoolbox.plot(type='bootstrap',
#                    clean=True,
#                    columns=2,
#                    input_ts='tests/02234500_65_65.csv')


@pytest.mark.mpl_image_compare(tolerance=6)
def test_probability_density():
    plt.close("all")
    return plottoolbox.probability_density(
        clean=True,
        input_ts="tests/02234500_65_65.csv",
        ofilename=None,
        plot_styles="classic",
    )


@pytest.mark.mpl_image_compare(tolerance=6)
def test_bar():
    plt.close("all")
    return plottoolbox.bar(input_ts=dfa, plot_styles="classic", ofilename=None)


@pytest.mark.mpl_image_compare(tolerance=6)
def test_barh():
    plt.close("all")
    return plottoolbox.barh(input_ts=dfa, plot_styles="classic", ofilename=None)


@pytest.mark.mpl_image_compare(tolerance=6)
def test_bar_stacked():
    plt.close("all")
    return plottoolbox.bar_stacked(input_ts=dfa, plot_styles="classic", ofilename=None)


@pytest.mark.mpl_image_compare(tolerance=6)
def test_barh_stacked():
    plt.close("all")
    return plottoolbox.barh_stacked(input_ts=dfa, plot_styles="classic", ofilename=None)
