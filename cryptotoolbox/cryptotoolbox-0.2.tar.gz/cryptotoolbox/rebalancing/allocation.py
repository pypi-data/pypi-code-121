#!/usr/bin/env python3
# coding: utf-8

""" Algorithms of portfolio allocation. """

# Built-in packages

# Third party packages
import pandas as pd
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import squareform
from scipy.optimize import Bounds, LinearConstraint, minimize

# Local packages
from cryptotoolbox.utility import metrics

from cryptotoolbox.rebalancing import rolling

import numpy as np
#import fastcluster
from scipy.cluster import hierarchy
from scipy.cluster.hierarchy import fcluster

from numpy import fft

# TODO : cython

__all__ = ['minDrawdown','ERC', 'HRP', 'IVP', 'MDP', 'MVP', 'MVP_uc', 'rolling_allocation']


# =========================================================================== #
#                         Equal Risk Contribution                             #
# =========================================================================== #


def ERC(X, w0=None, up_bound=1., low_bound=0., transaction_costs = None):
    r""" Get weights of Equal Risk Contribution portfolio allocation.

    Notes
    -----
    Weights of Equal Risk Contribution, as described by S. Maillard, T.
    Roncalli and J. Teiletche [1]_, verify the following problem:

    .. math::
        w = \text{arg min } f(w) \\
        u.c. \begin{cases}w'e = 1 \\
                          0 \leq w_i \leq 1 \\
             \end{cases}

    With:

    .. math::
        f(w) = N \sum_{i=1}^{N}w_i^2 (\Omega w)_i^2
        - \sum_{i,j=1}^{N} w_i w_j (\Omega w)_i (\Omega w)_j

    Where :math:`\Omega` is the variance-covariance matrix of `X` and :math:`N`
    the number of assets.

    Parameters
    ----------
    X : array_like
        Each column is a series of price or return's asset.
    w0 : array_like, optional
        Initial weights to maximize.
    up_bound, low_bound : float, optional
        Respectively maximum and minimum values of weights, such that low_bound
        :math:`\leq w_i \leq` up_bound :math:`\forall i`. Default is 0 and 1.

    Returns
    -------
    array_like
        Weights that minimize the Equal Risk Contribution portfolio.

    References
    ----------
    .. [1] http://thierry-roncalli.com/download/erc-slides.pdf

    """
    T, N = X.shape
    SIGMA = np.cov(X, rowvar=False)
    up_bound = max(up_bound, 1 / N)

    def f_ERC(w):
        w = w.reshape([N, 1])
        arg = N * np.sum(w ** 2 * (SIGMA @ w) ** 2)

        return arg - np.sum(w * (SIGMA @ w) * np.sum(w * (SIGMA @ w)))

    # Set inital weights
    if w0 is None:
        w0 = np.ones([N]) / N

    const_sum = LinearConstraint(np.ones([1, N]), [1], [1])
    const_ind = Bounds(low_bound * np.ones([N]), up_bound * np.ones([N]))
    result = minimize(
        f_ERC,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    )

    return result.x.reshape([N, 1])



#                     HRP developed by Marcos Lopez de Prado                  #
# =========================================================================== #

def _corr_dist(mat_corr):
    """ Compute a distance matrix based on correlation.

    Parameters
    ----------
    mat_corr: np.ndarray[ndim=2, dtype=float] or pd.DataFrame
        Matrix correlation.

    Returns
    -------
    mat_dist_corr: np.ndarray[ndim=2, dtype=float] or pd.DataFrame
        Matrix distance correlation.

    """
    return ((1 - mat_corr) / 2.) ** 0.5


def _get_quasi_diag(link):
    """ Compute quasi diagonal matrix.

    TODO : verify the efficiency

    Parameter
    ---------
    link: list of N lists
        Linkage matrix, N list (cluster) of 4-tuple such that the two first
        elements are the costituents, third report the distance between the two
        first, and fourth is the number of element (<= N) in this cluster.

    Returns
    -------
    sortIx: list
        Sorted list of items.

    """
    link = link.astype(int)
    sortIx = pd.Series([link[-1, 0], link[-1, 1]])
    numItems = link[-1, 3]  # number of original items

    while sortIx.max() >= numItems:
        sortIx.index = range(0, sortIx.shape[0] * 2, 2)  # make space
        df0 = sortIx[sortIx >= numItems]  # find clusters
        i, j = df0.index, df0.values - numItems
        sortIx[i] = link[j, 0]  # item 1
        df0 = pd.Series(link[j, 1], index=i + 1)
        sortIx = sortIx.append(df0)  # item 2
        sortIx = sortIx.sort_index()  # re-sort
        sortIx.index = range(sortIx.shape[0])  # re-index

    return sortIx.tolist()


def _get_rec_bisec(mat_cov, sortIx):
    """ Compute weights.

    TODO : verify the efficiency /! must be not efficient /!

    Parameters
    ----------
    mat_cov: pd.DataFrame
        Matrix variance-covariance
    sortIx: list
        Sorted list of items.

    Returns
    -------
    pd.DataFrame
       Weights.

    """
    w = pd.Series(1, index=sortIx)
    cItems = [sortIx]  # initialize all items in one cluster

    while len(cItems) > 0:
        cItems = [i[j: k] for i in cItems for j, k in (
            (0, int(len(i) / 2)),
            (int(len(i) / 2), len(i))
        ) if len(i) > 1]  # bi-section

        for i in range(0, len(cItems), 2):  # parse in pairs
            cItems0 = cItems[i]  # cluster 1
            cItems1 = cItems[i + 1]  # cluster 2
            cVar0 = _get_cluster(mat_cov, cItems0)
            cVar1 = _get_cluster(mat_cov, cItems1)
            alpha = 1 - cVar0 / (cVar0 + cVar1)
            w[cItems0] *= alpha  # weight 1
            w[cItems1] *= 1 - alpha  # weight 2

    return w


def _get_cluster(mat_cov, cItems):
    """ Compute cluster for variance.

    Parameters
    ----------
    mat_cov: pd.DataFrame
        Covariance matrix.
    cItems: list
        Cluster.

    Returns
    -------
    cVar: float
        Cluster variance

    """
    cov_ = mat_cov.loc[cItems, cItems]  # matrix slice
    w_ = _get_IVP(cov_).reshape(-1, 1)
    cVar = ((w_.T @ cov_) @ w_)  # [0, 0]

    return cVar.values[0, 0]


def _get_IVP(mat_cov):
    """ Compute the inverse-variance matrix.

    Parameters
    ----------
    mat_cov : array_like
        Variance-covariance matrix.

    Returns
    -------
    pd.DataFrame
        Matrix of inverse-variance.

    """
    ivp = 1. / np.diag(mat_cov)
    ivp /= np.sum(ivp)

    return ivp
################################

def HRC(X, low_bound=0., up_bound=1.0, nb_clusters = 5, transaction_costs = None):
    if not isinstance(X, pd.DataFrame):
        X = pd.DataFrame(X)

    up_bound = max(up_bound, 1 / X.shape[1])
    low_bound = min(low_bound, 1 / X.shape[1])

    # Compute covariance and correlation matrix
    correl_mat = X.corr().fillna(0).values

    dist = 1 - correl_mat
    dim = len(dist)
    tri_a, tri_b = np.triu_indices(dim, k=1)
    Z = np.linkage(dist[tri_a, tri_b], method='ward')

    permutation = hierarchy.leaves_list(
        hierarchy.optimal_leaf_ordering(Z, dist[tri_a, tri_b]))
    ordered_corr = correl_mat[permutation, :][:, permutation]

    clustering_inds = fcluster(Z, nb_clusters, criterion='maxclust')
    clusters = {i: [] for i in range(min(clustering_inds),
                                     max(clustering_inds) + 1)}
    for i, v in enumerate(clustering_inds):
        clusters[v].append(i)
    weights = _compute_hrc_allocation(correl_mat, clusters, dim, Z)
    return _normalize(weights, up_bound=up_bound, low_bound=low_bound)


def _seriation(Z, dim, cur_index):
    if cur_index < dim:
        return [cur_index]
    else:
        left = int(Z[cur_index - dim, 0])
        right = int(Z[cur_index - dim, 1])
        return _seriation(Z, dim, left) + _seriation(Z, dim, right)

def _intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

def _compute_hrc_allocation(covar, clusters, dim, Z):
    nb_clusters = len(clusters)
    assets_weights = np.array([1.] * len(covar))
    clusters_weights = np.array([1.] * nb_clusters)
    clusters_var = np.array([0.] * nb_clusters)

    for id_cluster, cluster in clusters.items():
        cluster_covar = covar[cluster, :][:, cluster]
        inv_diag = 1 / np.diag(cluster_covar)
        assets_weights[cluster] = inv_diag / np.sum(inv_diag)

    for id_cluster, cluster in clusters.items():
        weights = assets_weights[cluster]
        clusters_var[id_cluster - 1] = np.dot(
            weights, np.dot(covar[cluster, :][:, cluster], weights))

    for merge in range(nb_clusters - 1):
        left = int(Z[dim - 2 - merge, 0])
        right = int(Z[dim - 2 - merge, 1])
        left_cluster = _seriation(Z, dim, left)
        right_cluster = _seriation(Z, dim, right)

        ids_left_cluster = []
        ids_right_cluster = []
        for id_cluster, cluster in clusters.items():
            if sorted(_intersection(left_cluster, cluster)) == sorted(cluster):
                ids_left_cluster.append(id_cluster)
            if sorted(_intersection(right_cluster, cluster)) == sorted(cluster):
                ids_right_cluster.append(id_cluster)
        ids_left_cluster = np.array(ids_left_cluster) - 1
        ids_right_cluster = np.array(ids_right_cluster) - 1

        left_cluster_var = np.sum(clusters_var[ids_left_cluster])
        right_cluster_var = np.sum(clusters_var[ids_right_cluster])
        alpha = 1 - left_cluster_var / (left_cluster_var + right_cluster_var)

        clusters_weights[ids_left_cluster] = clusters_weights[
            ids_left_cluster] * alpha
        clusters_weights[ids_right_cluster] = clusters_weights[
            ids_right_cluster] * (1 - alpha)

    for id_cluster, cluster in clusters.items():
        assets_weights[cluster] = assets_weights[cluster] * clusters_weights[
            id_cluster - 1]

    return assets_weights


def HRP(X, method='single', metric='euclidean', low_bound=0., up_bound=1.0, transaction_costs = None):
    r""" Get weights of the Hierarchical Risk Parity allocation.

    Notes
    -----
    Hierarchical Risk Parity algorithm is developed by Marco Lopez de Prado
    [2]_. First step is clustering and second step is allocating weights.

    Parameters
    ----------
    X : array_like
        Each column is a price or return's asset series. Some errors will
        happen if one or more series are constant.
    method, metric: str
        Parameters for linkage algorithm, default ``method='single'`` and
        ``metric='euclidean'``.
    low_bound, up_bound : float
        Respectively minimum and maximum value of weights, such that low_bound
        :math:`\leq w_i \leq` up_bound :math:`\forall i`. Default is 0 and 1.

    Returns
    -------
    np.ndarray
        Vecotr of weights computed by HRP algorithm.

    References
    ----------
    .. [2] https://ssrn.com/abstract=2708678

    """
    if not isinstance(X, pd.DataFrame):
        X = pd.DataFrame(X)

    idx = X.columns
    up_bound = max(up_bound, 1 / X.shape[1])
    low_bound = min(low_bound, 1 / X.shape[1])

    # Compute covariance and correlation matrix
    mat_cov = X.cov()
    mat_corr = X.corr().fillna(0)
    # Compute distance matrix
    # print(mat_corr)
    mat_dist = _corr_dist(mat_corr).fillna(0)
    mat_dist_corr = squareform(mat_dist)

    link = sch.linkage(mat_dist_corr, method=method, metric=metric)
    # Sort linked matrix
    sortIx = _get_quasi_diag(link)
    sortIx = mat_corr.index[sortIx].tolist()
    w = _get_rec_bisec(mat_cov, sortIx)
    w = w.loc[idx].to_numpy(copy=True).reshape([w.size, 1])

    return _normalize(w, up_bound=up_bound, low_bound=low_bound)


def minSharpe(X, w0=None, normalize=False, low_bound=0., up_bound=1.0, transaction_costs = None):
    T, N = X.shape
    SIGMA = np.cov(X, rowvar=False)
    if N == 0:
        print('trouble in paradize')
    up_bound = max(up_bound, 1 / N)

    def f_sharpe(w):
        w = w.reshape([N, 1])
        return - metrics.sharpe(np.cumprod(np.prod(X @ w + 1, axis=1)))

    # Set inital weights
    if w0 is None:
        w0 = np.ones([N]) / N

    const_sum = LinearConstraint(np.ones([1, N]), [1], [1])
    const_ind = Bounds(low_bound * np.ones([N]), up_bound * np.ones([N]))
    result = minimize(
        f_sharpe,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    )

    return result.x.reshape([N, 1])


def maxPerf(X,  w0=None, normalize=False, low_bound=0., up_bound=1.0, transaction_costs = None):
    T, N = X.shape
    up_bound = max(up_bound, 1 / N)

    def f_performance(w, X, t):
        normalized_transactions = t/abs(sum(t))
        returns_over_time = X @ w + 1
        cumulated_perf = np.cumprod(returns_over_time)
        final_cumulated_perf = cumulated_perf[-1]
        return final_cumulated_perf

    toOptimize = lambda w : f_performance(w,X,transaction_costs)

    # Set inital weights
    if w0 is None:
        w0 = np.ones([N]) / N

    const_sum = LinearConstraint(np.ones([1, N]), [1], [1])
    const_ind = Bounds(low_bound * np.ones([N]), up_bound * np.ones([N]))
    result = minimize(
        toOptimize,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    )

    return result.x.reshape([N, 1])

def minDrawdown(X,  w0=None, normalize=False, low_bound=0., up_bound=1.0, transaction_costs = None):
    T, N = X.shape
    SIGMA = np.cov(X, rowvar=False)
    up_bound = max(up_bound, 1 / N)

    def f_drawdown(w, X):
        return metrics.drawdown(np.cumprod(X @ w + 1)).max()

    toOptimize = lambda w : f_drawdown(w,X)

    # Set inital weights
    if w0 is None:
        w0 = np.ones([N]) / N

    const_sum = LinearConstraint(np.ones([1, N]), [1], [1])
    const_ind = Bounds(low_bound * np.ones([N]), up_bound * np.ones([N]))
    result = minimize(
        toOptimize,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    )

    return result.x.reshape([N, 1])

# =========================================================================== #
#                        Inverse Variance Portfolio                           #
# =========================================================================== #

def IVP(X, normalize=False, low_bound=0., up_bound=1.0, transaction_costs = None):
    r""" Get weights of the Inverse Variance Portfolio allocation.

    Notes
    -----
    w are computed by the inverse of the asset's variance [3]_ such that:

    .. math::
        w_i = \frac{1}{\sigma_k^2} (\sum_{i} \frac{1}{\sigma_i^2})^{-1}

    With :math:`\sigma_i^2` is the variance of asset i.

    Parameters
    ----------
    X : array_like
        Each column is a price or return's asset series.
    normalize : bool, optional
        If True normalize the weights such that :math:`\sum_{i=1}^{N} w_i = 1`
        and :math:`0 \leq w_i \leq 1`. Default is False.
    low_bound, up_bound : float, optional
        Respectively minimum and maximum values of weights, such that low_bound
        :math:`\leq w_i \leq` up_bound :math:`\forall i`. Default is 0 and 1.

    Returns
    -------
    np.ndarray
        Vector of weights computed by the IVP algorithm.

    References
    ----------
    .. [3] https://en.wikipedia.org/wiki/Inverse-variance_weighting

    """
    mat_cov = np.cov(X, rowvar=False)
    w = _get_IVP(mat_cov)
    up_bound = max(up_bound, 1 / X.shape[1])
    low_bound = min(low_bound, 1 / X.shape[1])

    if normalize:
        w = w - np.min(w)
        w = w / np.sum(w)

    #    return w.reshape([mat_cov.shape[0], 1])
    w = _normalize(w, up_bound=up_bound, low_bound=low_bound)
    # w = w * (up_bound - low_bound) + low_bound

    return w.reshape([mat_cov.shape[0], 1])


# =========================================================================== #
#                         Minimum Variance Portfolio                          #
# =========================================================================== #


def MVP(X, normalize=False, transaction_costs = None):
    r""" Get weights of the Minimum Variance Portfolio allocation.

    Notes
    -----
    The vector of weights noted :math:`w` that minimize the portfolio variance
    [4]_ is define as below:

    .. math:: w = \frac{\Omega^{-1} e}{e' \Omega^{-1} e} \\
    .. math:: \text{With } \sum_{i=1}^{N} w_i = 1

    Where :math:`\Omega` is the asset's variance-covariance matrix and
    :math:`e` is a vector of ones.

    Parameters
    ----------
    X : array_like
        Each column is a time-series of price or return's asset.
    normalize : boolean, optional
        If True normalize the weigths such that :math:`0 \leq w_i \leq 1` and
        :math:`\sum_{i=1}^{N} w_i = 1`, :math:`\forall i`. Default is False.

    Returns
    -------
    array_like
        Vector of weights to apply to the assets.

    References
    ----------
    .. [4] https://breakingdownfinance.com/finance-topics/modern-portfolio-theory/minimum-variance-portfolio/

    See Also
    --------
    HRP

    """
    mat_cov = np.cov(X, rowvar=False)
    # Inverse variance matrix
    try:
        iv = np.linalg.inv(mat_cov)

    except np.linalg.LinAlgError:
        try:
            iv = np.linalg.pinv(mat_cov)
        except np.linalg.LinAlgError:
            raise np.linalg.LinAlgError

    e = np.ones([iv.shape[0], 1])
    w = (iv @ e) / (e.T @ iv @ e)

    if normalize:
        w = w - np.min(w)

        return w / np.sum(w)

    return w

def MVP_uc_lasso(X, w0=None, up_bound=1., low_bound=0., transaction_costs = None):
    r""" Get weights of the Minimum Variance Portfolio under constraints.

    Notes
    -----
    Weights of Minimum Variance Portfolio verify the following problem:

    .. math::
        w = \text{arg min } w' \Omega w \\
        u.c. \begin{cases}w'e = 1 \\
                          0 \leq w_i \leq 1 \\
             \end{cases}

    Where :math:`\Omega` is the variance-covariance matrix of `X` and :math:`e`
    a vector of ones.

    Parameters
    ----------
    X : array_like
        Each column is a series of price or return's asset.
    w0 : array_like, optional
        Initial weights to maximize.
    up_bound, low_bound : float, optional
        Respectively maximum and minimum values of weights, such that low_bound
        :math:`\leq w_i \leq` up_bound :math:`\forall i`. Default is 0 and 1.

    Returns
    -------
    array_like
        Weights that minimize the variance of the portfolio.

    """
    mat_cov = np.cov(X, rowvar=False)
    N = X.shape[1]
    up_bound = max(up_bound, 1 / N)

    def f_MVP_lasso(w):
        w = w.reshape([N, 1])
        return w.T @ mat_cov @ w + np.sum(abs(w))

    # Set inital weights
    if w0 is None:
        w0 = np.ones([N]) / N

    # Set constraints and minimze
    const_sum = LinearConstraint(np.ones([1, N]), [1], [1])
    const_ind = Bounds(low_bound * np.ones([N]), up_bound * np.ones([N]))
    result = minimize(
        f_MVP_lasso,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    )

    return result.x.reshape([N, 1])


def MVP_uc(X, w0=None, up_bound=1., low_bound=0., transaction_costs = None):
    r""" Get weights of the Minimum Variance Portfolio under constraints.

    Notes
    -----
    Weights of Minimum Variance Portfolio verify the following problem:

    .. math::
        w = \text{arg min } w' \Omega w \\
        u.c. \begin{cases}w'e = 1 \\
                          0 \leq w_i \leq 1 \\
             \end{cases}

    Where :math:`\Omega` is the variance-covariance matrix of `X` and :math:`e`
    a vector of ones.

    Parameters
    ----------
    X : array_like
        Each column is a series of price or return's asset.
    w0 : array_like, optional
        Initial weights to maximize.
    up_bound, low_bound : float, optional
        Respectively maximum and minimum values of weights, such that low_bound
        :math:`\leq w_i \leq` up_bound :math:`\forall i`. Default is 0 and 1.

    Returns
    -------
    array_like
        Weights that minimize the variance of the portfolio.

    """
    mat_cov = np.cov(X, rowvar=False)
    N = X.shape[1]
    up_bound = max(up_bound, 1 / N)

    def f_MVP(w):
        w = w.reshape([N, 1])
        return w.T @ mat_cov @ w

    # Set inital weights
    if w0 is None:
        w0 = np.ones([N]) / N

    # Set constraints and minimze
    const_sum = LinearConstraint(np.ones([1, N]), [1], [1])
    const_ind = Bounds(low_bound * np.ones([N]), up_bound * np.ones([N]))
    result = minimize(
        f_MVP,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    )

    return result.x.reshape([N, 1])


# =========================================================================== #
#    Maximum Diversification Portfolio developed by Choueifaty and Coignard   #
# =========================================================================== #


def MDP(X, w0=None, up_bound=1., low_bound=0., transaction_costs = None):
    r""" Get weights of Maximum Diversified Portfolio allocation.

    Notes
    -----
    Weights of Maximum Diversification Portfolio, as described by Y. Choueifaty
    and Y. Coignard [5]_, verify the following problem:

    .. math::

        w = \text{arg max } D(w) \\
        u.c. \begin{cases}w'e = 1 \\
                          0 \leq w_i \leq 1 \\
             \end{cases}

    Where :math:`D(w)` is the diversified ratio of portfolio weighted by `w`.

    Parameters
    ----------
    X : array_like
        Each column is a series of price or return's asset.
    w0 : array_like, optional
        Initial weights to maximize.
    up_bound, low_bound : float, optional
        Respectively maximum and minimum values of weights, such that low_bound
        :math:`\leq w_i \leq` up_bound :math:`\forall i`. Default is 0 and 1.

    Returns
    -------
    array_like
        Weights that maximize the diversified ratio of the portfolio.

    See Also
    --------
    diversified_ratio

    References
    ----------
    .. [5] tobam.fr/wp-content/uploads/2014/12/TOBAM-JoPM-Maximum-Div-2008.pdf

    """
    T, N = X.shape
    up_bound = max(up_bound, 1 / N)

    # Set function to minimze
    def f_max_divers_weights(w):
        return - metrics.diversified_ratio(X, w=w).flatten()

    # Set inital weights
    if w0 is None:
        w0 = np.ones([N]) / N

    # Set constraints and minimze
    const_sum = LinearConstraint(np.ones([1, N]), [1], [1])
    const_ind = Bounds(low_bound * np.ones([N]), up_bound * np.ones([N]))
    result = minimize(
        f_max_divers_weights,
        w0,
        method='SLSQP',
        constraints=[const_sum],
        bounds=const_ind
    )

    return result.x.reshape([N, 1])




# =========================================================================== #
#                             Rolling allocation                              #
# =========================================================================== #
def rolling_forward_looking_allocation(f, X, n=252, s=63, ret=True, drift=True, **kwargs):
    X = pd.DataFrame(X).fillna(method='ffill')
    idx = X.index
    w_mat = pd.DataFrame(index=idx, columns=X.columns)
    portfolio = pd.Series(100., index=idx, name='portfolio')

    if ret:
        X_ = X.pct_change()

    else:
        X_ = X

    roll = rolling._RollingMechanism(idx, n=n, s=s)

    def forward_process(series):
        # True if less than 50% of obs. are constant
        return series.value_counts(dropna=False).max() < 0.9 * s

    for slice_n, slice_s in roll():
        # Select X
        # the allocation is perfect cause we see the future
        sub_X = X_.loc[slice_s].copy()
        assets = list(X.columns[sub_X.apply(forward_process)])
        sub_X = sub_X.fillna(method='bfill')
        # Compute weights
        if len(assets) == 1:
            w = np.array([[1.]])

        else:
            w = f(sub_X.loc[:, assets].values, **kwargs)

        # print("forward looking")
        # print(w.flatten().sum())
        w_mat.loc[roll.d, assets] = w.flatten()
        w_mat.loc[roll.d, :] = w_mat.loc[roll.d, :].fillna(0.)
        # Compute portfolio performance
        perf = _perf_alloc(
            X.loc[slice_s, assets].fillna(method='bfill').values,
            w=w,
            drift=drift
        )
        portfolio.loc[slice_s] = portfolio.loc[roll.d] * perf.flatten()

    w_mat = w_mat.fillna(method='ffill').fillna(0.)

    return portfolio, w_mat

def fourierExtrapolation(x, n_predict, n_harm=5, detrending=True):
    n = x.size
    # number of harmonics in model
    t = np.arange(0, n)
    if detrending:
        p = np.polyfit(t, x, 1)
        # find linear trend in x
        pente = p[0]
    else:
        pente = 0

    x_notrend = x - pente * t  # detrended x
    x_freqdom = fft.fft(x_notrend)  # detrended x in frequency domain
    f = fft.fftfreq(n)  # frequencies
    indexes = list(range(n))
    # sort indexes by frequency, lower -> higher
    indexes.sort(key=lambda i: np.absolute(f[i]))

    t = np.arange(0, n + n_predict)
    restored_sig = np.zeros(t.size)
    for i in indexes[:1 + n_harm * 2]:
        ampli = np.absolute(x_freqdom[i]) / n  # amplitude
        phase = np.angle(x_freqdom[i])  # phase
        restored_sig += ampli * np.cos(2 * np.pi * f[i] * t + phase)
    return restored_sig + pente * t

def fourierFrequency(x):
    n = x.size
    # number of harmonics in model
    x_freqdom = fft.fft(x)  # detrended x in frequency domain
    f = fft.fftfreq(n)  # frequencies
    indexes = list(range(n))
    # sort indexes by frequency, lower -> higher
    indexes.sort(key=lambda i: np.absolute(f[i]))
    return f, np.abs(x_freqdom)

def rolling_fourier( close, n=252, s=63, nb_split=3, threshold1=0.15, threshold2=0.15,ls=True ):
    X = pd.DataFrame(close)#.fillna(method='ffill')
    idx = X.index
    portfolio = pd.Series(0., index=idx, name='portfolio')
    X_ = X
    roll = rolling._RollingMechanism(idx, n=n, s=s)

    for slice_n, slice_s, slice_s_eval in roll():
        # Select X
        sub_X = X_.loc[slice_n].copy()
        f, module = fourierFrequency(np.asarray(sub_X))
        specter = {"freq_{:.2f}".format(f[i]): module[i] for i in range(len(f)) if f[i] >= 0}
        sorted_f = sorted(f)
        specter_df = pd.DataFrame.from_records(specter)
        freq_df = specter_df.filter(regex='freq*').copy()
        freq_columns = list(freq_df.columns)
        low_freq_columns = freq_columns[:nb_split]
        high_freq_columns = freq_columns[-nb_split:]

        low_score = freq_df[low_freq_columns].mean(axis=1)[0]
        high_score = freq_df[high_freq_columns].mean(axis=1)[0]
        if low_score >= threshold1 or high_score >= threshold2:
            portfolio.loc[slice_s] = 1.
        else :
            if ls:
                portfolio.loc[slice_s] = -1.
            else:
                portfolio.loc[slice_s] = 0.

    return portfolio

def rolling_fourier_extrapolation_simple(close, n=252, s=63, n_harm = 5 , detrending = False):
    X = pd.DataFrame(close)#.fillna(method='ffill')
    idx = X.index
    portfolio = pd.Series(0., index=idx, name='portfolio')
    X_ = X
    roll = rolling._RollingMechanism(idx, n=n, s=s)
    for slice_n, slice_s, slice_s_eval in roll():
        sub_X = X_.loc[slice_n].copy()
        prediction = fourierExtrapolation(np.asarray(sub_X).reshape(len(np.asarray(sub_X))),s, n_harm = n_harm, detrending=detrending)
        final_prediction = prediction[-s:]
        me_len = slice_s.stop - slice_s.start + 1
        portfolio.loc[slice_s] = final_prediction[-me_len:]
    return portfolio

def rolling_fourier_extrapolation( close, n=252, s=63, n_harm = 5 , detrending = False, short = True, quantile_low = 0.05, quantile_high = 0.95):
    X = pd.DataFrame(close)#.fillna(method='ffill')
    idx = X.index
    portfolio = pd.Series(0., index=idx, name='portfolio')
    portfolio_continuous = pd.Series(0., index=idx, name='portfolio_continuous')
    X_ = X
    roll = rolling._RollingMechanism(idx, n=n, s=s)
    for slice_n, slice_s, slice_s_eval in roll():
        # Select X
        #print(slice_n)
        #print(slice_s)
        sub_X = X_.loc[slice_n].copy()
        prediction = fourierExtrapolation(np.asarray(sub_X).reshape(len(np.asarray(sub_X))),s, n_harm = n_harm, detrending=detrending)
        final_prediction = prediction[-s:]
        if short:
            final_prediction_discrete = final_prediction >= 0.
            pred = 2*final_prediction_discrete.astype(float) - 1
            me_len = slice_s.stop - slice_s.start+1
            portfolio.loc[slice_s] = pred[-me_len:]
            portfolio_continuous.loc[slice_s] = final_prediction[-me_len:]
        else :
            final_prediction_discrete = final_prediction >= 0.
            pred = final_prediction_discrete.astype(float)
            me_len = slice_s.stop - slice_s.start+1
            portfolio.loc[slice_s] = pred[-me_len:]
            portfolio_continuous.loc[slice_s] = final_prediction[-me_len:]

    low_pred = np.quantile(portfolio_continuous, quantile_low)
    high_pred = np.quantile(portfolio_continuous, quantile_high)
    if short:
        def compute_ls_level(low_threshold, high_threshold, row):
            if row <= low_threshold:
                return -1.
            if row >= high_threshold:
                return 1.
            return 0.
        import functools
        go = functools.partial(compute_ls_level,low_pred,high_pred)
        portfolio_threshold = portfolio_continuous.apply(go)
    else:
        def compute_lo_level(high_threshold, row):
            if row >= high_threshold:
                return 1.
            return 0.
        import functools
        go = functools.partial(compute_lo_level, high_pred)
        portfolio_threshold = portfolio_continuous.apply(go)

    return portfolio_threshold

def rolling_allocation(f, X, n=252, s=63, ret=True, drift=True, filtering_threshold = 0.7, transaction_costs = None, **kwargs):
    r""" Roll an algorithm of portfolio allocation.

    Notes
    -----
    Weights are computed on the past data from ``t - n`` to ``t`` and are
    applied to backtest on data from ``t`` to ``t + s``.

    .. math::
        \forall t \in [n, T], w_{t:t+s} = f(X_{t-n:t})

    Parameters
    ----------
    f : callable
        Allocation algorithm that take as parameters a subarray of ``X``
        and ``**kwargs``, and return a vector (as ``np.ndarray``) of weights.
    X : array_like
        Data matrix, each columns is a series of prices, indexes or
        performances, each row is a observation at time ``t``.
    n, s : int
        Respectively the number of observations to compute weights and the
        number of observations to roll. Default is ``n=252`` and ``s=63``.
    ret : bool, optional
        If True (default) pass to ``f`` the returns of ``X``. Otherwise pass
        ``X`` to ``f``.
    drift : bool, optional
        If False performance of the portfolio is computed as if we rebalance
        the weights of asset at each timeframe. Otherwise we let to drift the
        weights. Default is True.
    **kwargs
        Any keyword arguments to pass to ``f``.

    Returns
    -------
    pd.Series
        Performance of the portfolio allocated following ``f`` algorithm.
    pd.DataFrame
        Weights of the portfolio allocated following ``f`` algorithm.

    """
    X = pd.DataFrame(X).fillna(method='ffill')
    idx = X.index
    w_mat = pd.DataFrame(index=idx, columns=X.columns)
    portfolio = pd.Series(100., index=idx, name='portfolio')

    if ret:
        X_ = X.pct_change()

    else:
        X_ = X

    roll = rolling._RollingMechanism(idx, n=n, s=s)

    def allocation_process(series):
        # True if less than 50% of obs. are constant
        return series.value_counts(dropna=False).max() < filtering_threshold * n

    for slice_n, slice_s, slice_s_eval in roll():
        # Select X
        sub_X = X_.loc[slice_n].copy()
        assets = list(X.columns[sub_X.apply(allocation_process)])
        sub_X = sub_X.fillna(method='bfill')

        assets_iloc = [sub_X.columns.get_loc(ass) for ass in assets]

        # Compute weights
        if len(assets) == 1:
            w = np.array([[1.]])
        else:
            w = f(sub_X.loc[:, assets].values, transaction_costs = transaction_costs[assets_iloc], **kwargs)

        if w.flatten().sum(axis = 0 )>1:
            w=w/w.sum(axis=0)
        w_mat.loc[roll.d, assets] = w.flatten()
        w_mat.loc[roll.d, :] = w_mat.loc[roll.d, :].fillna(0.)
        # Compute portfolio performance
        perf = _perf_alloc(
            X.loc[slice_s, assets].fillna(method='bfill').values,
            w=w,
            drift=drift
        )
        portfolio.loc[slice_s] = portfolio.loc[roll.d] * perf.flatten()

    w_mat = w_mat.fillna(method='ffill').fillna(0.)

    return portfolio, w_mat


def rolling_ensembling(X, w_mat_predictors_list, w_mat_target=None, n=252, s=63,ret=True, ensembling_model = 'other', period = 252, display_slice = True, **kwargs):
    ## w_mat_target is there only for supervised learning
    assert len(w_mat_predictors_list) > 1
    X = pd.DataFrame(X).fillna(method='ffill')
    if ret:
        X_ = X.pct_change()
    else:
        X_ = X
    if ensembling_model == 'det_max_sharpe':
        to_apply = lambda my_df : pd.DataFrame(my_df).fillna(0)
        w_mat_predictors_list = list(map(to_apply, w_mat_predictors_list))
        idx = w_mat_predictors_list[0].index
        cols = w_mat_predictors_list[0].columns
        w_mat = pd.DataFrame(index=idx, columns=cols)
        #w_mat = pd.DataFrame(index=idx, columns=w_mat_target.columns)
        portfolio = pd.Series(100., index=idx, name='portfolio')
        roll = rolling._EnsemblingRollingMechanism(idx, n=n, s=s)
        for slice_n, slice_s, _ in roll():
            train_ret = X_.loc[slice_n].copy()
            #train_forward_looking = w_mat_target.loc[slice_n].copy()
            #test_forward_looking = w_mat_target.loc[slice_s].copy()

            to_train = lambda my_df: my_df.loc[slice_n].copy()
            to_test = lambda my_df: my_df.loc[slice_s].copy()

            train_weights = list(map(to_train, w_mat_predictors_list))
            test_weights = list(map(to_test, w_mat_predictors_list))

            x = metrics.find_best_sharpe(train_weights, train_ret)
            pred_y = metrics.compute_average_prediction(x, test_weights)
            pred_y = pred_y.fillna(0)
            w_mat.loc[slice_s] = pred_y.values
            #w_mat.loc[ensembled_weights_df_bis.index, assets] = ensembled_weights_df_bis.values
            w = w_mat.loc[roll.d, :].fillna(0.)
            # Compute portfolio performance
            perf = _perf_alloc(
                X.loc[slice_s, :].fillna(method='bfill').fillna(0.00000000001).values,
                w=w,
                drift=True
            )
            portfolio.loc[slice_s] = portfolio.loc[roll.d] * perf.flatten()
        w_mat = w_mat.fillna(method='ffill').fillna(0.)
        return portfolio, w_mat
    elif ensembling_model == 'det_min_dd':
        to_apply = lambda my_df : pd.DataFrame(my_df).fillna(0)
        w_mat_predictors_list = list(map(to_apply, w_mat_predictors_list))
        idx = w_mat_predictors_list[0].index
        cols = w_mat_predictors_list[0].columns
        w_mat = pd.DataFrame(index=idx, columns=cols)
        #w_mat = pd.DataFrame(index=idx, columns=w_mat_target.columns)
        portfolio = pd.Series(100., index=idx, name='portfolio')
        print('rolling with past calibration size '+str(n))
        print('rolling with rebalancing size '+str(s))

        roll = rolling._EnsemblingRollingMechanism(idx, n=n, s=s)
        for slice_n, slice_s, _ in roll():

            if display_slice:
                print('training slice '+str(slice_n))
                print('testing slice '+str(slice_s))

            train_ret = X_.loc[slice_n].copy()
            #train_forward_looking = w_mat_target.loc[slice_n].copy()
            #test_forward_looking = w_mat_target.loc[slice_s].copy()

            to_train = lambda my_df: my_df.loc[slice_n].copy()
            to_test = lambda my_df: my_df.loc[slice_s].copy()

            train_weights = list(map(to_train, w_mat_predictors_list))
            test_weights = list(map(to_test, w_mat_predictors_list))

            #x = metrics.find_best_sharpe(train_weights, train_ret)
            x = metrics.find_best_dd_weights(train_weights, train_ret)

            if display_slice:
                print('optimal weights found')
                print(x)

            pred_y = metrics.compute_average_prediction(x, test_weights)
            pred_y = pred_y.fillna(0)
            w_mat.loc[slice_s] = pred_y.values
            #w_mat.loc[ensembled_weights_df_bis.index, assets] = ensembled_weights_df_bis.values
            w = w_mat.loc[roll.d, :].fillna(0.)
            # Compute portfolio performance
            perf = _perf_alloc(
                X.loc[slice_s, :].fillna(method='bfill').fillna(0.00000000001).values,
                w=w,
                drift=True
            )
            portfolio.loc[slice_s] = portfolio.loc[roll.d] * perf.flatten()
        w_mat = w_mat.fillna(method='ffill').fillna(0.)
        return portfolio, w_mat
    elif ensembling_model == 'det_max_perf':
        to_apply = lambda my_df : pd.DataFrame(my_df).fillna(0)
        w_mat_predictors_list = list(map(to_apply, w_mat_predictors_list))
        idx = w_mat_predictors_list[0].index
        cols = w_mat_predictors_list[0].columns
        w_mat = pd.DataFrame(index=idx, columns=cols)
        #w_mat = pd.DataFrame(index=idx, columns=w_mat_target.columns)
        portfolio = pd.Series(100., index=idx, name='portfolio')
        print('rolling with past calibration size '+str(n))
        print('rolling with rebalancing size '+str(s))

        roll = rolling._EnsemblingRollingMechanism(idx, n=n, s=s)
        for slice_n, slice_s, _ in roll():

            if display_slice:
                print('training slice '+str(slice_n))
                print('testing slice '+str(slice_s))

            train_ret = X_.loc[slice_n].copy()
            #train_forward_looking = w_mat_target.loc[slice_n].copy()
            #test_forward_looking = w_mat_target.loc[slice_s].copy()

            to_train = lambda my_df: my_df.loc[slice_n].copy()
            to_test = lambda my_df: my_df.loc[slice_s].copy()

            train_weights = list(map(to_train, w_mat_predictors_list))
            test_weights = list(map(to_test, w_mat_predictors_list))

            #x = metrics.find_best_sharpe(train_weights, train_ret)
            x = metrics.find_best_perf_weights(train_weights, train_ret)

            if display_slice:
                print('optimal weights found')
                print(x)

            pred_y = metrics.compute_average_prediction(x, test_weights)
            pred_y = pred_y.fillna(0)
            w_mat.loc[slice_s] = pred_y.values
            #w_mat.loc[ensembled_weights_df_bis.index, assets] = ensembled_weights_df_bis.values
            w = w_mat.loc[roll.d, :].fillna(0.)
            # Compute portfolio performance
            perf = _perf_alloc(
                X.loc[slice_s, :].fillna(method='bfill').fillna(0.00000000001).values,
                w=w,
                drift=True
            )
            portfolio.loc[slice_s] = portfolio.loc[roll.d] * perf.flatten()
        w_mat = w_mat.fillna(method='ffill').fillna(0.)
        return portfolio, w_mat
    elif ensembling_model == 'period_max_perf':
        starting_date = kwargs['starting_date']
        ending_date = kwargs['ending_date']
        index_tmp = w_mat_predictors_list[0].index
        print('length before filtering '+ str(len(index_tmp)))
        print('min before filtering '+ str(min(index_tmp)))
        print('max before filtering '+ str(max(index_tmp)))
        to_time_filter_df = lambda my_df : my_df.iloc[my_df.index >= starting_date].copy()
        filtered_w_mat_predictors_list = list(map(to_time_filter_df, w_mat_predictors_list))
        up_time_filter_df = lambda my_df: my_df.iloc[my_df.index <= ending_date].copy()
        filtered_w_mat_predictors_list = list(map(up_time_filter_df, filtered_w_mat_predictors_list))
        filtered_index_tmp = filtered_w_mat_predictors_list[0].index
        print('length after filtering '+ str(len(filtered_index_tmp)))
        print('min after filtering '+ str(min(filtered_index_tmp)))
        print('max after filtering '+ str(max(filtered_index_tmp)))

        X_filtered = X_.iloc[X_.index >= starting_date].copy()
        X_filtered = X_filtered.iloc[X_filtered.index <= ending_date].copy()
        print('return shape')
        print(X_filtered.shape)
        print('number of weights configuration')
        print(len(w_mat_predictors_list))
        print('optimizing')
        optimal_weights = metrics.find_best_perf_weights(filtered_w_mat_predictors_list,X_filtered)


        print('optimal weights found')

        print(optimal_weights)

        columns_tmp = w_mat_predictors_list[0].columns
        to_np = lambda my_df : my_df.values
        w_mat_predictors_list = list(map(to_np, w_mat_predictors_list))
        np_mean_weights = None
        counter = 0
        for np_weights in w_mat_predictors_list:
            if np_mean_weights is None :
                np_mean_weights = optimal_weights[counter]*np_weights
            else :
                np_mean_weights = np_mean_weights + optimal_weights[counter]*np_weights
            counter = counter+1

        print(np_mean_weights.sum(axis=1))
        #np_mean_weights = np_mean_weights/len(w_mat_predictors_list)
        w_mat = pd.DataFrame(data = np_mean_weights,index=index_tmp, columns=columns_tmp)
        portfolio = np.cumprod(np.prod(X_ * w_mat.values + 1, axis=1))
        return portfolio, w_mat
    else :
        print('defaulting to simple average')
        index_tmp = w_mat_predictors_list[0].index
        columns_tmp = w_mat_predictors_list[0].columns
        to_np = lambda my_df : my_df.values
        w_mat_predictors_list = list(map(to_np, w_mat_predictors_list))
        np_mean_weights = None
        for np_weights in w_mat_predictors_list:
            if np_mean_weights is None :
                np_mean_weights = np_weights
            else :
                np_mean_weights = np_mean_weights + np_weights
        np_mean_weights = np_mean_weights/len(w_mat_predictors_list)
        w_mat = pd.DataFrame(data = np_mean_weights,index=index_tmp, columns=columns_tmp)
        portfolio = np.cumprod(np.prod(X_ * w_mat.values + 1, axis=1))
        return portfolio, w_mat



# =========================================================================== #
#                                   Tools                                     #
# =========================================================================== #


def _perf_alloc(X, w, drift=True):
    # Compute portfolio performance following specified weights
    if w.ndim == 1 and not isinstance(w, pd.Series):
        w = w.reshape([w.size, 1])

    if drift:
        return (X / X[0, :]) @ w

    perf = np.zeros(X.shape)
    perf[1:] = (X[1:] / X[:-1] - 1)

    return np.cumprod(perf @ w + 1)


def _normalize(w, low_bound=0., up_bound=1., sum_w=1., max_iter=1000):
    # Iterative algorithm to set bounds
    if up_bound < sum_w / w.size or low_bound > sum_w / w.size:

        raise ValueError('Low or up bound exceeded sum weight constraint.')

    j = 0
    while (min(w) < low_bound or max(w) > up_bound) and j < max_iter:
        for i in range(w.size):
            w[i] = min(w[i], up_bound)
            w[i] = max(w[i], low_bound)

        w = sum_w * (w / sum(w))
        j += 1

    if j >= max_iter:
        print('Iterative normalize algorithm exceeded max iterations')

    return w
