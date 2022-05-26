import numpy as np
from scipy import integrate
from scipy.interpolate import interp1d
import matplotlib.pylab as plt

def getfitnesspenalty(
    self, ref, com, y="gr", abs=False, figs=True, nosamples=100, norm=False
):
    """
    Calculates - as a measure of fitness - the area between typically
    two growth rate versus OD curves, normalized by the length along the
    OD-axis where they overlap.

    Parameters
    -----------
    ref: list of strings
        For only a single experiment, a list of two strings. The first string
        specifies the condition and the second specifies the strain to be used
        for the reference to which fitness is to be calculated.
        With multiple experiments, a list of three strings. The first string
        specifies the experiment, the second specifies the condition, and the
        third specifies the strain.
    com: list of strings
        For only a single experiment, a list of two strings. The first string
        specifies the condition and the second specifies the strain to be
        compared with the reference.
        With multiple experiments, a list of three strings. The first string
        specifies the experiment, the second specifies the condition, and the
        third specifies the strain.
    y: string, optional
        The variable to be compared.
    figs: boolean, optional
        If True, a plot of the area between the two growth rate versus OD
        curves is shown.
    nosamples: integer
        The number bootstraps used to estimate the error.
    norm: boolean
        If True, returns the mean and variance of the area under the reference
        strain for normalisation.

    Returns
    -------
    fp: float
        The area between the two curves.
    err: float
        An estimate of the error in the calculated error, found by
        bootstrapping.
    reffp: float, optional
        The area beneath the reference strain.
    referr: float, optional
        An estimate of the erroe in the calculated area for the reference
        strain.

    Example
    -------
    >>> p.getfitnesspenalty(['1% raf 0.0µg/ml cyclohex', 'WT'],
    ...                     ['1% raf 0.5µg/ml cyclohex', 'WT'])
    """
    if len(self.allexperiments) == 1:
        ref.insert(0, self.allexperiments[0])
        com.insert(0, self.allexperiments[0])
    # get and sample from Gaussian processes
    if nosamples and y == "gr":
        # estimate errors
        try:
            # sample from Gaussian process
            f0s, g0s, h0s = self.progress["getstatsGP"][ref[0]][ref[1]][
                ref[2]
            ].fitderivsample(nosamples)
            f1s, g1s, h1s = self.progress["getstatsGP"][com[0]][com[1]][
                com[2]
            ].fitderivsample(nosamples)
            xsref, ysref = np.exp(f0s), g0s
            xscom, yscom = np.exp(f1s), g1s
        except KeyError:
            raise errors.GetFitnessPenalty(
                "getstats('OD') needs to be run for these strains to "
                "estimate errors or else set nosamples= 0"
            )
    else:
        # no estimates of errors
        if nosamples:
            print(
                "Cannot estimate errors - require y= 'gr' and a recently "
                "run getstats"
            )
        xsref = self.s.query(
            "experiment == @ref[0] and condition == @ref[1] and "
            "strain == @ref[2]"
        )["OD mean"][:, None]
        ysref = self.s.query(
            "experiment == @ref[0] and condition == @ref[1] and "
            "strain == @ref[2]"
        )[y].to_numpy()[:, None]
        xscom = self.s.query(
            "experiment == @com[0] and condition == @com[1] and "
            "strain == @com[2]"
        )["OD mean"].to_numpy()[:, None]
        yscom = self.s.query(
            "experiment == @com[0] and condition == @com[1] and "
            "strain == @com[2]"
        )[y].to_numpy()[:, None]
        if xsref.size == 0 or ysref.size == 0:
            print(ref[0] + ": Data missing for", ref[2], "in", ref[1])
            return np.nan, np.nan
        elif xscom.size == 0 or yscom.size == 0:
            print(com[0] + ": Data missing for", com[2], "in", com[1])
            return np.nan, np.nan
    fps = np.zeros(xsref.shape[1])
    nrm = np.zeros(xsref.shape[1])
    samples = zip(
        np.transpose(xsref),
        np.transpose(ysref),
        np.transpose(xscom),
        np.transpose(yscom),
    )
    # process samples
    for j, (xref, yref, xcom, ycom) in enumerate(samples):
        # remove any double values in OD because of OD plateau'ing
        uxref, uiref = np.unique(xref, return_inverse=True)
        uyref = np.array(
            [
                np.median(yref[np.nonzero(uiref == i)[0]])
                for i in range(len(uxref))
            ]
        )
        uxcom, uicom = np.unique(xcom, return_inverse=True)
        uycom = np.array(
            [
                np.median(ycom[np.nonzero(uicom == i)[0]])
                for i in range(len(uxcom))
            ]
        )
        # interpolate data
        iref = interp1d(uxref, uyref, fill_value="extrapolate", kind="slinear")
        icom = interp1d(uxcom, uycom, fill_value="extrapolate", kind="slinear")
        # find common range of x
        uxi = np.max([uxref[0], uxcom[0]])
        uxf = np.min([uxref[-1], uxcom[-1]])
        # perform integration to find normalized area between curves
        if abs:

            def igrand(x):
                return np.abs(iref(x) - icom(x))

        else:

            def igrand(x):
                return iref(x) - icom(x)

        fps[j] = integrate.quad(igrand, uxi, uxf, limit=100, full_output=1)[
            0
        ] / (uxf - uxi)
        if norm:
            # calculate area under curve of reference strain as a normalisation
            def igrand(x):
                return iref(x)

            nrm[j] = integrate.quad(
                igrand, uxi, uxf, limit=100, full_output=1
            )[0] / (uxf - uxi)
        # an example figure
        if figs and j == 0:
            plt.figure()
            plt.plot(uxref, uyref, "k-", uxcom, uycom, "b-")
            x = np.linspace(uxi, uxf, np.max([len(uxref), len(uxcom)]))
            plt.fill_between(x, iref(x), icom(x), facecolor="red", alpha=0.5)
            plt.xlabel("OD")
            plt.ylabel(y)
            plt.legend(
                [
                    ref[0] + ": " + ref[2] + " in " + ref[1],
                    com[0] + ": " + com[2] + " in " + com[1],
                ],
                loc="upper left",
                bbox_to_anchor=(-0.05, 1.15),
            )
            plt.show()
    if norm:
        return (
            np.median(fps),
            statserr(fps),
            np.median(nrm),
            statserr(nrm),
        )
    else:
        return np.median(fps), statserr(fps)
