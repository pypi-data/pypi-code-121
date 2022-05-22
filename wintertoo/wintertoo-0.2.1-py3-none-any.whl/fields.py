from wintertoo.data import summer_fields
import matplotlib.pyplot as plt
import numpy as np
import logging
from astropy.coordinates import SkyCoord

logger = logging.getLogger(__name__)

base_summer_width = 0.25


def get_summer_fields_in_box(ra_lim, dec_lim):
    res = summer_fields.query(
        f"(RA > {ra_lim[0]}) and (RA < {ra_lim[1]}) and (Dec > {dec_lim[0]}) and (Dec < {dec_lim[1]})"
    )
    return res


def get_overlapping_summer_fields(ra_deg, dec_deg):

    summer_width = base_summer_width / np.cos(np.radians(dec_deg))

    res = summer_fields.query(
        f"(RA > {ra_deg - 0.5 * summer_width}) and "
        f"(RA < {ra_deg + 0.5 * summer_width}) and "
        f"(Dec > {dec_deg - 0.5 * summer_width}) and "
        f"(Dec < {dec_deg + 0.5 * summer_width})"
    )

    logger.info(f"Found {len(res)} overlapping fields.")

    return res


def get_best_summer_field(ra_deg, dec_deg, make_plot: bool = True):

    res = get_overlapping_summer_fields(ra_deg, dec_deg)

    c = SkyCoord(ra_deg, dec_deg, unit="deg")

    dists = np.array([c.separation(SkyCoord(x["RA"], x["Dec"], unit="deg")).value for _, x in res.iterrows()])

    closest_mask = dists == np.min(dists)

    closest = res[closest_mask]

    logger.info(f"Best is field {int(closest.iloc[0]['#ID'])}")

    if make_plot:
        plot_overlapping_summer_fields(res, ra_deg, dec_deg, closest)

    return closest.iloc[0]


def plot_field_rectangles(ax, res, color="k"):
    base_summer_width_deg = 0.25

    for index, row in res.iterrows():
        summer_width_deg = base_summer_width_deg / np.cos(np.radians(row["Dec"]))
        rectangle = plt.Rectangle(
            (row["RA"] - 0.5 * summer_width_deg, row["Dec"] - 0.5 * summer_width_deg),
            summer_width_deg,
            summer_width_deg,
            fc="none", ec=color
        )
        ax.add_patch(rectangle)


def plot_summer_fields(res, ra_lim, dec_lim):

    ax = plt.subplot(111)
    plt.scatter(res["RA"], res["Dec"], marker="+")

    rectangle = plt.Rectangle(
        (ra_lim[0], dec_lim[0]),
        (ra_lim[1] - ra_lim[0]),
        (dec_lim[1] - dec_lim[0]),
        fc="red", alpha=0.2
    )
    ax.add_patch(rectangle)

    plot_field_rectangles(ax, res)

    return ax


def plot_overlapping_summer_fields(res, ra_deg, dec_deg, closest=None):

    ax = plt.subplot(111)
    plt.scatter(ra_deg, dec_deg, marker="*")

    plot_field_rectangles(ax, res)

    if closest is not None:
        plot_field_rectangles(ax, closest, color="r")

    return ax
