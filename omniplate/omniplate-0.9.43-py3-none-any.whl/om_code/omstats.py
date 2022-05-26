# functions to calculate the statistics from the Gaussian process
# fit to the data
# and getfitnesspenalty

import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from scipy import integrate
from scipy.interpolate import interp1d
import om_code.omgenutils as gu


def statserr(d):
    """
    Errors in statistics calculated from samples from a
    Gaussian process are half the interquartile range (consistent with
    fitderiv).
    """
    return gu.findiqr(d) / 2

###


def cleansc(self):
    """
    Ensure that NaNs do not change numeric variables from being floats.
    """
    floatvars = [
        "log2 OD ratio",
        "log2 OD ratio err",
        "local max gr",
        "local max gr err",
        "time of local max gr",
        "time of local max gr err",
        "area under gr vs OD",
        "area under gr vs OD err",
        "normalized area under gr vs OD",
        "normalized area under gr vs OD err",
        "area under OD",
        "area under OD err",
        "normalized area under OD",
        "normalized area under OD err",
        "OD logmaxlike",
        "max gr",
        "max gr err",
        "time of max gr",
        "time of max gr err",
        "doubling time",
        "doubling time err",
        "max OD",
        "max OD err",
        "lag time",
        "lag time err",
    ]
    for var in floatvars:
        if var in self.sc.columns:
            self.sc[var] = self.sc[var].astype(float)

###


def findsummarystats(
    dtype,
    derivname,
    logs,
    nosamples,
    f,
    t,
    e,
    c,
    s,
    findareas,
    figs,
    plotlocalmax,
    axgr,
    showpeakproperties,
    **kwargs,
):
    """
    Finds summary statistics from GP fit to time series of dtype
    """
    warning = None
    odtype = "log(" + dtype + ")" if logs else dtype
    outdf = pd.DataFrame(
        {
            "experiment": e,
            "condition": c,
            "strain": s,
            "time": t,
            "f" + odtype: f.f,
            "f" + odtype + " err": np.sqrt(f.fvar),
            derivname: f.df,
            derivname + " err": np.sqrt(f.dfvar),
            "d/dt " + derivname: f.ddf,
            "d/dt " + derivname + " err": np.sqrt(f.ddfvar),
        }
    )
    # check derivative has been sensibly defined
    if (
        np.max(np.abs(f.df)) < 1.0e-20
        and np.max(np.abs(np.diff(f.dfvar))) < 1.0e-20
    ):
        warning = (
            "\nWarning: getstats may have failed for "
            + e
            + ": "
            + s
            + " in "
            + c
        )
    # find summary statistics
    fs, gs, hs = f.fitderivsample(nosamples)
    # find local maximal derivative
    da, dt = findlocalmaxderiv(
        f, gs, axgr, figs, plotlocalmax, showpeakproperties, **kwargs
    )
    # find area under df vs f and area under f vs t
    if findareas:
        adff, andff, aft, anft = findareasunder(t, fs, gs, logs)
    else:
        adff, andff, aft, anft = np.nan, np.nan, np.nan, np.nan
    # store results
    statsdict = {
        "experiment": e,
        "condition": c,
        "strain": s,
        "local max " + derivname: np.median(da),
        "local max " + derivname + " err": statserr(da),
        "time of local max " + derivname: np.median(dt),
        "time of local max " + derivname + " err": statserr(dt),
        "area under " + derivname + " vs " + dtype: np.median(adff),
        "area under " + derivname + " vs " + dtype + " err": statserr(adff),
        "normalized area under " + derivname + " vs " + dtype: np.median(andff),
        "normalized area under " + derivname + " vs " + dtype + " err": statserr(andff),
        "area under " + dtype: np.median(aft),
        "area under " + dtype + " err": statserr(aft),
        "normalized area under " + dtype: np.median(anft),
        "normalized area under " + dtype + " err": statserr(anft),
    }
    return outdf, statsdict, warning

###


def findlocalmaxderiv(
    f, gs, axgr, figs, plotlocalmax, showpeakproperties, **kwargs
):
    """
    Check the derivative for local maxima. If so, find the local maximum
    with the highest derivative using samples, gs, of df. The keyword variables
    kwargs are passed to scipy's find_peaks.
    """
    # find peaks in mean df
    lpksmn, lpksmndict = find_peaks(f.df, **kwargs)
    if np.any(lpksmn):
        if showpeakproperties:
            # display properties of peaks
            print("Peak properties\n---")
            for prop in lpksmndict:
                print("{:15s}".format(prop), lpksmndict[prop])
        # da: samples of local max df
        # dt: samples of time of local max df
        da, dt = [], []
        # find peaks of sampled df
        for gsample in np.transpose(gs):
            tpks = find_peaks(gsample, **kwargs)[0]
            if np.any(tpks):
                da.append(np.max(gsample[tpks]))
                dt.append(f.t[tpks[np.argmax(gsample[tpks])]])
        if figs and plotlocalmax:
            # plot local max df as a point
            axgr.plot(
                np.median(dt),
                np.median(da),
                "o",
                color="yellow",
                markeredgecolor="k",
            )
        return da, dt
    else:
        # mean df has no peaks
        return np.nan, np.nan

###


def findareasunder(t, fs, gs, logs):
    """
    Given samples of f, as arguments fs, and of df, as arguments gs,
    either find the area under df/dt vs f and the area under f vs t
    or if logs find the area under d/dt log(f) vs f and the area
    under f vs t.
    """
    # adff: samples of area under df vs f
    # andff: samples of normalised area under df vs f
    # aft: samples of area under f vs t
    # anft: samples of normalised area under f vs t
    adff, andff, aft, anft = [], [], [], []
    for fsample, gsample in zip(np.transpose(fs), np.transpose(gs)):
        sf = np.exp(fsample) if logs else fsample
        # area under df vs f: integrand has f as x and df as y
        def integrand(x): return interp1d(sf, gsample)(x)
        iresult = integrate.quad(
            integrand, np.min(sf), np.max(sf), limit=100, full_output=1
        )[0]
        adff.append(iresult)
        andff.append(iresult / (np.max(sf) - np.min(sf)))
        # area under f vs t: integrand has t as x and f as y
        def integrand(x): return interp1d(t, sf)(x)
        iresult = integrate.quad(
            integrand, np.min(t), np.max(t), limit=100, full_output=1
        )[0]
        aft.append(iresult)
        anft.append(iresult / (np.max(t) - np.min(t)))
    return adff, andff, aft, anft
