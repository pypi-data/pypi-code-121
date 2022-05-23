import os
import time
import random
import numpy as np
import pandas as pd
import scipy
import scipy.io as sio
from scipy import stats
from scipy import sparse
from sklearn.metrics.pairwise import euclidean_distances as EuDist2
from sklearn.cluster import KMeans as sk_KMeans
from sklearn.cluster import MiniBatchKMeans
from joblib import Parallel, delayed
from multiprocessing import Pool
from functools import partial
import pickle



def savepkl(data, full_path, make_dir=True):

    if make_dir:
        path = os.path.dirname(full_path)
        if not os.path.exists(path):
            os.makedirs(path)

    pickle.dump(data, open(full_path, "wb"))


def loadpkl(full_path):
    data = pickle.load(open(full_path, "rb"))
    return data


def loadmat(path, to_dense=True):
    data = sio.loadmat(path)
    X = data["X"]
    y_true = data["y_true"].astype(np.int32).reshape(-1)

    if sparse.isspmatrix(X) and to_dense:
        X = X.toarray()

    N, dim, c_true = X.shape[0], X.shape[1], len(np.unique(y_true))
    X = X.astype(np.float64)
    return X, y_true, N, dim, c_true


def savemat(name_full, xy):
    sio.savemat(name_full, xy)


def matrix_index_take(X, ind_M):
    """
    :param X: ndarray
    :param ind_M: ndarray
    :return: X[ind_M] copied
    """
    assert np.all(ind_M >= 0)

    n, k = ind_M.shape
    row = np.repeat(np.array(range(n), dtype=np.int32), k)
    col = ind_M.reshape(-1)
    ret = X[row, col].reshape((n, k))
    return ret


def matrix_index_assign(X, ind_M, Val):
    n, k = ind_M.shape
    row = np.repeat(np.array(range(n), dtype=np.int32), k)
    col = ind_M.reshape(-1)
    if isinstance(Val, (float, int)):
        X[row, col] = Val
    else:
        X[row, col] = Val.reshape(-1)


def EProjSimplex_new(v, k=1):
    v = v.reshape(-1)
    # min  || x- v ||^2
    # s.t. x>=0, sum(x)=k
    ft = 1
    n = len(v)
    v0 = v-np.mean(v) + k/n
    vmin = np.min(v0)

    if vmin < 0:
        f = 1
        lambda_m = 0
        while np.abs(f) > 1e-10:
            v1 = v0 - lambda_m
            posidx = v1 > 0
            npos = np.sum(posidx)
            g = -npos
            f = np.sum(v1[posidx]) - k
            lambda_m -= f/g
            ft += 1
            if ft > 100:
                break
        x = np.maximum(v1, 0)
    else:
        x = v0

    return x, ft


def EProjSimplexdiag(d, u):
    #  d = d.astype(np.float64)
    #  u = u.astype(np.float64)
    # min  1/2*x'*U*x - x'*d
    # s.t. x>=0, sum(x) = 1
    lam = np.min(u-d)
    #  print(lam)
    f = 1
    count = 1
    while np.abs(f) > 1e-8:
        v1 = (lam + d)/u
        posidx = v1 > 0
        #  print(v1)
        g = np.sum(1/u[posidx])
        f = np.sum(v1[posidx]) - 1
        #  print(f)
        lam -= f/g

        if count > 1000:
            break
        count += 1
    v1 = (lam+d)/u
    x = np.maximum(v1, 0)
    return x, f

def eig1(A, c, isMax=True, isSym=True):
    if isinstance(A, sparse.spmatrix):
        A = A.toarray()

    if isSym:
        A = np.maximum(A, A.T)

    if isSym:
        d, v = np.linalg.eigh(A)
    else:
        d, v = np.linalg.eig(A)

    if isMax:
        idx = np.argsort(-d)
    else:
        idx = np.argsort(d)

    idx1 = idx[:c]
    eigval = d[idx1]
    eigvec = v[:, idx1]

    eigval_full = d[idx]

    return eigvec, eigval, eigval_full


def KMeans(X, c, rep, init="random", algorithm="auto"):
    '''
    :param X: 2D-array with size of N x dim
    :param c: the number of clusters to construct
    :param rep: the number of runs
    :param init: the way of initialization: random (default), k-means++
    :return: Y, 2D-array with size of rep x N, each row is a assignment
    '''
    times = np.zeros(rep)
    Y = np.zeros((rep, X.shape[0]), dtype=np.int32)
    for i in range(rep):
        t_start = time.time()
        Y[i] = sk_KMeans(n_clusters=c, n_init=1, init=init, algorithm=algorithm).fit(X).labels_
        t_end = time.time()
        times[i] = t_end - t_start

    return Y, times


def relabel(y, offset=0):
    y_df = pd.DataFrame(data=y, columns=["label"])
    ind_dict = y_df.groupby("label").indices

    for yi, ind in ind_dict.items():
        y[ind] = offset
        offset += 1


def normalize_fea(fea, row):
    '''
    if row == 1, normalize each row of fea to have unit norm;
    if row == 0, normalize each column of fea to have unit norm;
    '''

    if 'row' not in locals():
        row = 1

    if row == 1:
        feaNorm = np.maximum(1e-14, np.sum(fea ** 2, 1).reshape(-1, 1))
        fea = fea / np.sqrt(feaNorm)
    else:
        feaNorm = np.maximum(1e-14, np.sum(fea ** 2, 0))
        fea = fea / np.sqrt(feaNorm)

    return fea




def initialY(X, c_true, rep, way="random"):
    num, dim = X.shape
    if way == "random":
        Y = np.zeros((rep, num), dtype=np.int32)
        for i in range(rep):
            y1 = np.arange(c_true)
            y2 = np.random.randint(0, c_true, num-c_true)
            y3 = np.concatenate((y1, y2), axis=0)
            np.random.shuffle(y3)
            Y[i, :] = y3

    elif way == "k-means":
        Y, t = KMeans(X=X, c=c_true, rep=rep, init="random")
    elif way == "k-means++":
        Y, t = KMeans(X=X, c=c_true, rep=rep, init="k-means++")
    else:
        raise SystemExit('no such options in "initialY"')

    return Y



def WHH(W, c, beta=0.5, ITER=100):
    val, vec = np.linalg.eigh(W)
    H = vec[:, -c:]
    #  H = sparse.linalg.eigsh(W, which='LA', k=c)[1]
    #  print(np.mean(H))
    H = np.maximum(W @ H, 0.00001)

    obj = np.zeros(ITER)
    obj[0] = np.linalg.norm(W - H@H.T, ord="fro")

    for i in range(1, ITER):
        H_old = H.copy()

        WH = W@H
        HHH = H@(H.T@H)
        H = H*(1 - beta + beta*WH/HHH)

        obj[i] = np.linalg.norm(W - H@H.T, ord="fro")

        if np.abs(obj[i] - obj[i-1])/obj[i] < 1e-6:
            break

    return H, obj


def norm_W(A):
    d = np.sum(A, 1)
    d[d == 0] = 1e-6
    d_inv = 1 / np.sqrt(d)
    tmp = A * np.outer(d_inv, d_inv)
    A2 = np.maximum(tmp, tmp.T)
    return A2



def y2Cen(X, y, c_true):
    eye_c = np.eye(c_true, dtype=np.int32)
    Y = eye_c[y]
    nc_neg = np.diag( 1 / np.diag(Y.T @ Y) )
    Cen = nc_neg @ (Y.T @ X)
    return Cen

def Y2Cens(X, Y, c_true):
    rep = Y.shape[0]
    dim = X.shape[1]
    Cen = np.zeros((rep, c_true, dim), dtype=np.float64)
    for i, y in enumerate(Y):
        Cen[i] = y2Cen(X, y, c_true)
    
    return Cen


def y2Y(y, c_true):
    eye_c = np.eye(c_true)
    Y = eye_c[y]
    return Y