# general functions for a variety of purposes
import numpy as np


def mergedicts(original, update):
    """
    Given two dicts, merge them into a new dict

    Arguments
    --
    x: first dict
    y: second dict
    """
    z = original.copy()
    z.update(update)
    return z


###


def findsmoothvariance(y, filtsig=0.1, nopts=False):
    """
    Estimates and then smooths the variance over replicates of data

    Arguments
    --
    y: data - one column for each replicate
    filtsig: sets the size of the Gaussian filter used to smooth the variance
    nopts: if set, uses estimateerrorbar to estimate the variance
    """
    from scipy.ndimage import filters

    if y.ndim == 1:
        # one dimensional data
        v = estimateerrorbar(y, nopts) ** 2
    else:
        # multi-dimensional data
        v = np.var(y, 1)
    # apply Gaussian filter
    vs = filters.gaussian_filter1d(v, int(len(y) * filtsig))
    return vs


###


def estimateerrorbar(y, nopts=False):
    """
    Estimates measurement error for each data point of y by calculating
    the standard deviation of the nopts data points closest to that
    data point

    Arguments
    --
    y: data - one column for each replicate
    nopts: number of points used to estimate error bars
    """
    y = np.asarray(y)
    if y.ndim == 1:
        ebar = np.empty(len(y))
        if not nopts:
            nopts = np.round(0.1 * len(y))
        for i in range(len(y)):
            ebar[i] = np.std(np.sort(np.abs(y[i] - y))[:nopts])
        return ebar
    else:
        print("estimateerrorbar: works for 1-d arrays only.")


###


def natural_keys(text):
    """
    Used to sort a list of strings by the numeric values in the list entries.

    Eg sorted(list, key= natural_keys)

    Arguments
    --
    text: a string (but see above example)
    """
    import re

    def atof(text):
        try:
            retval = float(text)
        except ValueError:
            retval = text
        return retval

    return [
        atof(c)
        for c in re.split(r"[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)", text)
    ]


###


def absorbdf(blob, victim, cols):
    """
    Absorb one dataframe into another using a list of columns as an index
    to align the dataframes.
    Any NaNs in the victim will replace those in blob (not the default
    behaviour of pd.update).

    Arguments
    --
    blob: the absorbing dataframe
    victim: the dataframe to be absorbed
    cols: a list of columns to align the dataframes
    """
    df = blob.set_index(cols)
    victim.update(victim.fillna(np.inf))
    df.update(victim.set_index(cols))
    df.replace(np.inf, np.nan, inplace=True)
    return df.reset_index()


###


def islistempty(ell):
    """
    Check if a list of lists is empty, e.g. [[]]

    Arguments
    --
    ell: list
    """
    if isinstance(ell, list):  # Is a list
        return all(map(islistempty, ell))
    return False  # Not a list


###


def findiqr(d):
    """
    Finds the interquartile range of data in an array

    Arguments
    --
    d: a one-dimensional array of data
    """
    return np.subtract(*np.percentile(d, [75, 25]))


###


def makelist(c):
    """
    Ensures that a variable is a list

    Arguments
    --
    c: variable to be made into a list
    """
    import numpy as np

    if type(c) == np.ndarray:
        return list(c)
    elif type(c) is not list:
        return [c]
    else:
        return c


###


def figs2pdf(savename):
    """
    Save all open figures to a pdf file
    """
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt

    if "." not in savename:
        savename += ".pdf"
    with PdfPages(savename) as pp:
        for i in plt.get_fignums():
            plt.figure(i)
            pp.savefig()
