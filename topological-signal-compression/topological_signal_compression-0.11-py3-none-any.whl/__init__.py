# Gary Koplik
# gary<dot>koplik<at>geomdata<dot>com
# Februrary, 2020
# __init__.py


"""
Topological Signal Compression (TSC).
"""


import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from timeseries import Signal
import warnings


def signal_persistence(signal: np.ndarray) -> pd.DataFrame:
    """
    Build a persistence diagram for a signal.
    
    :param signal: (n, 2) array where the first column represents the times / domain / x points of the signal
        and the second column represents the scalars / range / y points corresponding to each time.
    :return: DataFrame of signal persistence.
    :rtype: ``pandas.DataFrame``.
    """
    ts = Signal(values=signal[:, 1], times=signal[:, 0])
    ts.make_pers()
    return ts.pers.diagram
    

def compress_tsc(signal: np.ndarray, pers_diag: pd.DataFrame or None = None,
                 persistence_cutoff: int or None = None,
                 num_indices_to_keep: int or float or str = None) -> np.ndarray:
    """
    Removes the least persistent critical point pairs from a signal on a 1-dimensional domain.

    To maintain spanning the same domain of the signal, even if the edge values are not top critical points,
    (or not critical points at all), the function will always return the edge values.

    When specifying ``num_indices_to_keep=n``, the function will return *no more than* ``n`` values. Note, if the user
    requests ``n`` greater than the number of critical points, then only the endpoints and critical points will be
    returned.

    When instead specifying ``persistence_cutoff=k``, the function will return all critical points with persistence
    greater than ``k`` along with the edge values if not already included.

    An empty persistence diagram (e.g. no critical points) or if choosing a persistence threshold that keeps zero
    indices from the persistence diagram will result in a reconstruction of a straight line signal containing solely the
    two endpoints of the original ``signal`` input.

    Note: the user can either specify a ``persistence_cutoff``, or retain a desired number of points using
    ``num_indices_to_keep``, but exactly one of these must be specified as non-``None``.

    :param signal: ``(n, 2)`` array where the first column represents the times / domain / x points of the signal
        and the second column represents the scalars / range / y points corresponding to each time.
    :param pers_diag: output of persistence information as called from ``tsc.signal_persistence()``.
        Default ``None`` computes persistence diagram for ``signal`` in the method call.
    :param persistence_cutoff: a non-``None`` value will reconstruct the signal using only critical point pairs with
        persistence greater than this value. Note: the user can either specify a ``persistence_cutoff``, or retain a
        desired number of points using ``num_indices_to_keep``, but exactly one of these must be specified as
        non-``None``.
    :param num_indices_to_keep: number of points to keep from ``signal`` when reconstructing the signal. Can also offer
        the string "all" here for a reconstruction using the full persistence diagram (plus endpoints), or offer a
        decimal in (0, 1) to return a percentage of critical points. If specifying an ``int``, must specify
        an integer greater than 2, as the edge values at minimum will always be returned. If the user requests more
        indices than the sum of endpoints plus all critical points, then the returned signal will still only consist of
        those endpoints and all critical points. Note: the user can either specify a ``persistence_cutoff``, or retain
        a desired number of points using ``num_indices_to_keep``, but exactly one of these must be specified as
        non-``None``.
    :return: ``(k, 2)`` array (``k`` <= ``n``) representing the reconstructed signal where the first column
        represents the times / domain / x points of the signal and the second column represents the
        scalars / range / y points corresponding to each time.
    :rtype: ``np.ndarray``.

    .. note::
        The Morse Cancellation Lemma guarantees that the dot of lowest persistence corresponds to
        a pair of *adjacent* critical points (and also guarantees that "un-kinking" that pair of critical
        points will not un-kink any other pair).

        Technically, this Lemma requires that the two neighbors of any given critical point be distinct.
        If this assumption fails, we could create non-unique solutions. However, leaving this at the mercy
        of pandas sorting by persistence will still return a *correct* result regardless, even though it may
        not be unique.

        Furthermore, this Lemma only applies to removing the lowest persistence critical point, but as long as we
        remove the n lowest critical points, the order in which we remove them should not matter (in other words, at
        least when replacing critical points with linear interpolation, removing these critical points is commutative).

    :references:
        Edelsbrunner, Herbert, Dmitriy Morozov, and Valerio Pascucci.
        "Persistence-sensitive simplification functions on 2-manifolds."
        Proceedings of the twenty-second annual symposium on Computational geometry. 2006.
    """

    if persistence_cutoff is None and num_indices_to_keep is None:
        raise NotImplementedError(
            "Must Specify either `persistence_cutoff` or `num_indices_to_keep`"
        )

    if persistence_cutoff is not None and num_indices_to_keep is not None:
        raise NotImplementedError(
            "Must Specify *exactly* one of `persistence_cutoff` or `num_indices_to_keep`"
        )
    
    if num_indices_to_keep is not None and num_indices_to_keep != "all":
        assert num_indices_to_keep >= 2 or 0 < num_indices_to_keep < 1, \
            "`num_indices_to_keep` must be >=2 since we always at least return the edge values\n" + \
            "or be in (0, 1) representing returning a reconstruction using only a percentage of the persistence values"

    # we will reference the Signal object for knowing min and max indices later
    ts = Signal(values=signal[:, 1], times=signal[:, 0])
    
    if pers_diag is None:
        ts.make_pers()
        pers_diag = ts.pers.diagram
        
    # work with a sorted persistence diagram to remove the lowest persistence points
    pers_diag = pers_diag.sort_values('pers', ascending=False)
    
    # know the index bounds so we can guarantee we maintain the domain
    start_index = ts.components.index.min()
    stop_index = ts.components.index.max()

    # take our desired subset of the persistence diagram for reconstruction
    if num_indices_to_keep is not None:
        
        if num_indices_to_keep == "all":
            # all critical pairs + endpoints
            indices = [start_index, stop_index] + \
                list(pers_diag.loc[:, ['birth_index', 'death_index']].values.flatten())
            # remove redundancies
            indices = list(set(indices))
                
        else:
            # convert decimal to a number of indices
            if 0 < num_indices_to_keep < 1:
                num_indices_to_keep = int(signal.shape[0] * num_indices_to_keep)
                if num_indices_to_keep < 2:
                    warnings.warn("Decimal `num_indices_to_keep` results in less than 2 points, "
                                  "defaulting to return just the 2 edges", stacklevel=2)
                    num_indices_to_keep = 2
            # exactly `num_indices_to_keep` points
            # start with all possible values
            ordered_indices = [start_index, stop_index] + \
                list(pers_diag.loc[:, ['birth_index', 'death_index']].values.flatten())
            
            # if we're already below our threshold for number of values, stop
            if len(list(set(ordered_indices))) <= num_indices_to_keep:
                indices = list(set(ordered_indices))
            
            # otherwise make sure we hit our exact cutoff
            else:
                # make sure we get the top *unique* indices:
                num_indices = num_indices_to_keep
                while True:
                    new_indices = ordered_indices[:num_indices]
                    if len(list(set(new_indices))) == num_indices_to_keep:
                        break
                    num_indices += 1
                # remove redundancies
                indices = list(set(new_indices))
            
    elif persistence_cutoff is not None:
        pers_diag = pers_diag[pers_diag.pers > persistence_cutoff]
        
        indices = [start_index, stop_index] + \
            list(pers_diag.loc[:, ['birth_index', 'death_index']].values.flatten())
        
        # remove redundancies
        indices = list(set(indices))

    return signal[sorted(indices), :]


def reconstruct_tsc(signal: np.ndarray, x_values: list = None) -> np.ndarray:
    """
    Reconstructs a Topological Signal Compression-compressed signal (``signal``) back to its original size, linearly
    interpolating signal values for the missing time indices in ``x_values``.
    This is useful when feeding a reconstructed signal into a machine learning pipeline expecting a specifically-sized
    input.

    Expects an input generated by the :py:func:`~tsc.__init__.compress_tsc()` method.

    .. note::
        This method takes advantage of the fact that all compression methods used in this package always return the
        first and last index signal value. Beware running this on code on other compression methods outside this
        package.

    :param signal: ``(k, 2)`` array of the signal to reconstruct, where the first column
        represents the times / domain / x points of the signal and the second column represents the
        scalars / range / y points corresponding to each time.
    :param x_values: values for the final time / domain / x points of the signal for which to reconstruct. Default
        ``None`` uses the ``int`` values between ``signal[0, 0]`` and ``signal[-1, 0]``. Reconstruction of missing
        values done via linear interpolation.
    :return: 2D array of compressed and reconstructed ``signal`` array, where the first column
        represents the times / domain / x points of the signal (``x_values``) and the second column represents the
        scalars / range / y points corresponding to each time.
    :rtype: ``np.ndarray``.
    """
    reco_fcn = interp1d(x=signal[:, 0], y=signal[:, 1], fill_value="extrapolate")
    if x_values is None:
        x_values = np.arange(signal[0, 0], signal[-1, 0] + 1)
    res = reco_fcn(x_values)
    return np.c_[x_values, res]


def tsc_pipeline(signal: np.ndarray, n_keep: float or int or str, pers_diag: pd.DataFrame or None = None) -> np.ndarray:
    """
    Perform topological signal compression and reconstruction. Reconstructs the signal to output at its original size
    with linear interpolation.

    :param signal: 1d signal to compress and reconstruct.
    :param n_keep: number of points to keep. If ``n_keep`` is a fraction in (0, 1) it
        will be treated as a percentage of points to retain. If ``n_keep`` is an
        ``int`` >=2 it will be treated as the number of points to retain. Can also offer
        the string "all" here for a reconstruction using the full persistence diagram (plus endpoints)
    :param pers_diag: previously computed persistence diagram corresponding to
        the argument provided to parameter ``signal``.
        Default ``None`` computes persistence diagram for ``signal`` in the method call.
    :return: 1D array of compressed and reconstructed ``signal`` array.
    :rtype: ``np.ndarray``.
    """
    if n_keep != "all":
        if n_keep >= signal.shape[0]:
            return signal

    n = signal.shape[0]
    compression = compress_tsc(np.c_[np.arange(n), signal], pers_diag=pers_diag,
                               num_indices_to_keep=n_keep)
    reconstruction = reconstruct_tsc(compression)
    return reconstruction[:, 1]
