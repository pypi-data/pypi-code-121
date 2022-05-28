"""Plot cmat/aset to html via holoviews and plotly.

aset = cmat2aset(cmat.T)
arr = np.array(aset)
# arr[arr == ""] = np.nan
arr[arr == ""] = 0
arr = arr.astype(float)

# set value to np.nan for ""
_ = [elm.tolist() if elm[2] != 0 else elm.tolist()[:2] + [np.nan] for elm in arr]


# remove rows containing nan
arr = arr[~np.isnan(arr).any(axis=1)]
_ = arr.copy()

# remove rows with first entry being nan
arr = arr[~np.isnan(arr[:, 0])]
_ = arr.copy()

# remove rows with first/second entry being nan
arr = arr[~(np.isnan(arr[:, 0]) | np.isnan(arr[:, 1]))]
_ = arr.copy()

tfv = np.isnan(arr)
arr[np.logical_not(tfv)]

"""
# pylint: disable=invalid-name

import os
from pathlib import Path
from typing import List, Optional

# from icecream import ic
# from holoviews import opts
import holoviews as hv
import joblib
import numpy as np
from cmat2aset import cmat2aset  # pylint: disable=import-error  # likely caused by pyc
from logzero import logger

# hv.extension('bokeh')
hv.extension("plotly")


def cmat2html(
    # data: np.ndarray,
    cmat: np.ndarray,
    aset: Optional[List] = None,
    xlabel: str = "x",
    ylabel: str = "y",
    # startfile: bool = True,
    show_plot: bool = True,
):
    """Plot cmat/aset to html via holoviews and plotly.

    Args:
        cmat: correlation matrix
        xlabel: x-axis label in the plots
        ylabel: y-axis label in the plots
        aset: align set
        show_plot: try to show html in a browser if set (default True) via os.startfile

    e.g.
    cmat = gen_cmat(en, zh)
    data2html(cmat, xlable="zh (x)", ylabel="en (y)")

    aset = cmat2aset(cmat)
    # (32, 35, 0.5)
    i, j, llh = aset[-1]
    assert round(cmat[j, i], 2) == llh
    en[i]. zh[j], llh
    # ('Homepage', '返回首页', 0.5)

    # (26, 28, 0.48)
    i, j, llh = aset[-8]
    assert round(cmat[j, i], 2) == llh
    en[i], zh[j], llh
    # ("`Were you asked to tea?' she demanded, tying an apron over her neat black frock, and standing with a spoonful of the leaf poised over the pot.",
    # '“是请你来吃茶的吗？”她问，把一条围裙系在她那干净的黑衣服上，就这样站着，拿一匙茶叶正要往茶壶里倒。',
    # 0.48)

    """
    # data changed to cmat
    # ic(data.shape)

    # _ = [[*elm] + [data[elm]] for elm in np.ndindex(data.shape)]

    # _ = [[*elm] + [v] for elm, v in np.ndenumerate(data)]
    _ = [[*elm, v] for elm, v in np.ndenumerate(cmat)]
    hm1 = hv.HeatMap(
        _,
        label="(z) likelihood heatmap",
        name="name1",
    )

    hm1.opts(
        # xticks=None,
        # tools=['hover'],  # only for bokeh
        # colorbar=True,
        # cmap="viridis_r",
        xlabel=xlabel,
        ylabel=ylabel,
        # cmap="viridis_r",
        # cmap="viridis",
        cmap="gist_earth_r",
        # cmap="summer_r",
        # cmap="fire_r",
    )

    # aset
    # aset = cmat2aset(cmat.T)
    # cmat
    if aset is None:
        # aset = cmat2aset(cmat.T)
        aset = cmat2aset(cmat)

    arr = np.array(aset, dtype=object)

    # convert "" in col3 to nan
    arr[:, 2][arr[:, 2] == ""] = np.nan
    arr[arr == ""] = 0
    arr = arr.astype(float)

    # set value to np.nan for "": old way
    # _ = [elm.tolist() if elm[2] != 0 else elm.tolist()[:2]
    # + [np.nan] for elm in arr]

    hm2 = hv.HeatMap(
        arr,
        label="(z) likelihood align trace",
    )

    hm2.opts(
        # xticks=None,
        # tools=['hover'],  # only for bokeh
        colorbar=True,
        # cmap="viridis_r",
        xlabel=xlabel,
        ylabel=ylabel,
        # cmap="viridis_r",
        # cmap="viridis",
        cmap="gist_earth_r",
        # cmap="summer_r",
        # cmap="fire_r",
        # labelled=["en", "zh", "llh"]  # ["x", "y", "z"]
    )
    # hv.save(hm, 'heatmap.html')
    # os.startfile("heatmap.html")

    hv.save(hm1 + hm2, "heatmap12.html")
    # hv.save(hm1 * hm, "heatmap1x2.html")

    logger.info(" html file written to %s", Path("heatmap12.html").resolve())

    # if startfile:
    if show_plot:
        try:
            os.startfile("heatmap12.html")
            logger.info(" Showing heatmap12.html in the default browser.")
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    # 36x33
    _ = joblib.load(r"data\cmat_36x33(zh-en).lzma")
    cmat2html(_)
