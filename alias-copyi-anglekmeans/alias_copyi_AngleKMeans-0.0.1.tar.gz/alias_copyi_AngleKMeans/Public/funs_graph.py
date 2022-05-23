import time
import random
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances as EuDist2
from scipy import signal

from . import funs as Ifuns


def get_anchor(X, m, way="random"):
    """
    X: n x d,
    m: the number of anchor
    way: [k-means, k-means2, k-means++, k-means++2, random]
    """
    if way == "k-means":
        A = KMeans(m, init='random').fit(X).cluster_centers_
    elif way == "k-means2":
        A = KMeans(m, init='random').fit(X).cluster_centers_
        D = EuDist2(A, X)
        ind = np.argmin(D, axis=1)
        A = X[ind, :]
    elif way == "k-means++":
        A = KMeans(m, init='k-means++').fit(X).cluster_centers_
    elif way == "k-means++2":
        A = KMeans(m, init='k-means++').fit(X).cluster_centers_
        D = EuDist2(A, X)
        A = np.argmin(D, axis=1)
    elif way == "random":
        ids = random.sample(range(X.shape[0]), m)
        A = X[ids, :]
    else:
        raise SystemExit('no such options in "get_anchor"')
    return A


def knn_f(X, knn, squared=True, self_include=True):

    t_start = time.time()
    D_full = EuDist2(X, X, squared=squared)
    np.fill_diagonal(D_full, -1)
    NN_full = np.argsort(D_full, axis=1)
    np.fill_diagonal(D_full, 0)
    if self_include:
        NN = NN_full[:, :knn]
    else:
        NN = NN_full[:, 1:(knn+1)]

    NND = Ifuns.matrix_index_take(D_full, NN)
    t_end = time.time()
    t = t_end - t_start

    return NN, NND, t


def knn_graph_gaussian(X, knn, t_way="mean", self_include=False, isSym=True):
    """
    :param X: data matrix of n by d
    :param knn: the number of nearest neighbors
    :param t_way: the bandwidth parameter
    :param self_include: weather xi is among the knn of xi
    :param isSym: True or False, isSym = True by default
    :return: A, a matrix (graph) of n by n
    """
    N, dim = X.shape
    NN, NND, time1 = knn_f(X, knn, squared=True, self_include=self_include)
    if t_way == "mean":
        t = np.mean(NND)
    elif t_way == "median":
        t = np.median(NND)
    Val = np.exp(-NND / (2 * t ** 2))

    A = np.zeros((N, N))
    Ifuns.matrix_index_assign(A, NN, Val)
    np.fill_diagonal(A, 0)

    if isSym:
        A = (A + A.T) / 2

    return A

def knn_graph_tfree(X, knn, self_include=False, isSym=True):
    """
    :param X: data matrix of n by d
    :param knn: the number of nearest neighbors
    :param self_include: weather xi is among the knn of xi
    :param isSym: True or False, isSym = True by default
    :return: A, a matrix (graph) of n by n
    """
    t_start = time.time()

    N, dim = X.shape
    NN_K, NND_K, time1 = knn_f(X, knn + 1, squared=True, self_include=self_include)

    NN = NN_K[:, :knn]
    NND = NND_K[:, :knn]

    NND_k = NND_K[:, knn]
    Val = NND_k.reshape(-1, 1) - NND
    ind0 = np.where(Val[:, 0] == 0)[0]
    if len(ind0) > 0:
        Val[ind0, :] = 1/knn

    Val = Val / (np.sum(Val, axis=1).reshape(-1, 1))

    A = np.zeros((N, N))
    Ifuns.matrix_index_assign(A, NN, Val)
    np.fill_diagonal(A, 0)

    if isSym:
        A = (A + A.T) / 2
    
    t_end = time.time()
    t = t_end - t_start
    return A, t


def kng_anchor(X, Anchor: np.ndarray, knn=20, way="gaussian", t="mean", HSI=False, shape=None, alpha=0):
    """ see agci for more detail
    :param X: data matrix of n (a x b in HSI) by d
    :param Anchor: Anchor set, m by d
    :param knn: the number of nearest neighbors
    :param alpha:
    :param way: one of ["gaussian", "t_free"]
        "t_free" denote the method proposed in :
            "The constrained laplacian rank algorithm for graph-based clustering"
        "gaussian" denote the heat kernel
    :param t: only needed by gaussian, the bandwidth parameter
    :param HSI: compute similarity for HSI image
    :param shape: list, [a, b, c] image: a x b, c: channel
    :param alpha: parameter for HSI
    :return: A, a matrix (graph) of n by m
    """
    if shape is None:
        shape = list([1, 1, 1])
    N = X.shape[0]
    anchor_num = Anchor.shape[0]

    D = EuDist2(X, Anchor, squared=True)  # n x m
    if HSI:
        # MeanData
        conv = np.ones((3, 3))/9
        NData = X.reshape(shape)
        MeanData = np.zeros_like(NData)
        for i in range(shape[-1]):
            MeanData[:, :, i] = signal.convolve2d(NData[:, :, i], np.rot90(conv), mode='same')
        MeanData = MeanData.reshape(shape[0] * shape[1], shape[2])

        D += EuDist2(MeanData, Anchor, squared=True)*alpha  # n x m
    NN_full = np.argsort(D, axis=1)
    NN = NN_full[:, :knn]  # xi isn't among neighbors of xi
    NN_k = NN_full[:, knn]

    Val = get_similarity_by_dist(D=D, NN=NN, NN_k=NN_k, knn=knn, way=way, t=t)

    A = np.zeros((N, anchor_num))
    Ifuns.matrix_index_assign(A, NN, Val)
    return A


def get_similarity_by_dist(D, NN, NN_k, knn, way, t):
    """
    :param D: Distance matrix
    :param NN_k: k-th neighbor of each sample
    :param NN: k-nearest-neighbor of each sample
    :param knn: neighbors
    :param way: "gaussian" or "t_free"
    :param t: "mean" or "median" if way=="gaussian"
    :return: NN, val, val[i, j] denotes the similarity between xi and xj
    """
    eps = 2.2204e-16
    NND = Ifuns.matrix_index_take(D, NN)
    if way == "gaussian":
        if t == "mean":
            t = np.mean(D)   # Before March 2021, t = np.mean(NND), exp(-NND/t)
        elif t == "median":
            t = np.median(D)  # Before March 2021, t = np.median(NND), exp(-NND/t)
        Val = np.exp(-NND / (2 * t ** 2))
    elif way == "t_free":
        NND_k = Ifuns.matrix_index_take(D, NN_k.reshape(-1, 1))
        Val = NND_k - NND
        ind0 = np.where(Val[:, 0] == 0)[0]
        if len(ind0) > 0:
            Val[ind0, :] = 1/knn
        Val = Val / (np.sum(Val, axis=1).reshape(-1, 1))
    else:
        raise SystemExit('no such options in "kng_anchor"')

    return Val
