import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
import pathlib


def get_colormap(cmap_name, reverse=False):

    # make absolute path
    bundle_dir = pathlib.Path(__file__).parent
    cmap_file = (bundle_dir / "colormaps" / (cmap_name + ".dat")).absolute()

    # read ASCII file
    pp = pd.read_csv(cmap_file)
    mm = pp.values
    nc = len(mm)

    # create colormap
    kk = np.ones(nc).reshape(nc, 1)
    newcolors = np.concatenate((mm, kk), axis=1)
    cmap0 = ListedColormap(newcolors)

    # reverse colormap
    if reverse:
        cmap0.colors = np.flip(cmap0.colors, axis=0)

    # retrn colormap
    return cmap0
