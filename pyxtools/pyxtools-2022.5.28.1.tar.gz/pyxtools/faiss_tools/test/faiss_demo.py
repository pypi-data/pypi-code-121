# -*- coding:utf-8 -*-
from __future__ import absolute_import

import numpy as np

try:
    from pyxtools.faiss_tools import faiss
except ImportError:
    from pyxtools.pyxtools.faiss_tools import faiss


def test_faiss():
    d = 64  # dimension
    nb = 100000  # database size
    nq = 10000  # nb of queries
    np.random.seed(1234)  # make reproducible
    xb = np.random.random((nb, d)).astype('float32')
    xb[:, 0] += np.arange(nb) / 1000.
    xq = np.random.random((nq, d)).astype('float32')
    xq[:, 0] += np.arange(nq) / 1000.

    print("xq shape is {}, xb shape is {}".format(xq.shape, xb.shape))

    index = faiss.IndexFlatL2(d)  # build the index
    print(index.is_trained)
    index.add(xb)  # add vectors to the index
    print(index.ntotal)

    k = 4  # we want to see 4 nearest neighbors
    distance_list, indices = index.search(xb[:5], k)  # sanity check
    print(indices)
    print(distance_list)
    distance_list, indices = index.search(xq, k)  # actual search
    print(indices[:5])  # neighbors of the 5 first queries
    print(indices[-5:])  # neighbors of the 5 last queries


def faiss_learning():
    dimension = 2

    vec_data = np.random.random((9, dimension)).astype(np.float32)
    index = 0
    for x in [-1, 0, 1]:
        for y in [1, 0, -1]:
            vec_data[index, :] = np.array([x, y])
            index += 1

    vec_query = np.array([[0.1, 0], [0.0, 0.0], [1.0, 1.0], [2.0, 2.0], [3.0, 3.0]], dtype=np.float32)
    vec_query.reshape((5, dimension))

    print("vec_data shape is {}, vec_query shape is {}".format(vec_data.shape, vec_query.shape))

    index = faiss.IndexFlatL2(dimension)  # build the index
    print(index.is_trained)
    index.add(vec_data)  # add vectors to the index
    print(index.ntotal)

    k = 4  # we want to see 4 nearest neighbors
    distance_list, indices = index.search(vec_data[:5], k)  # sanity check
    print("distance_list is {}, indices is {}".format(distance_list, indices))

    distance_list, indices = index.search(vec_query, k)  # sanity check
    print("neighbors of the 5 first queries is {}, neighbors of the 5 last queries is {}"
          .format(indices[:5], indices[-5:]))


def faiss_kmeans():
    d = 3  # dimension
    nb = 100000  # database size
    np.random.seed(1234)  # make reproducible
    x = np.random.random((nb, d)).astype('float32')
    num_centroids = 1024
    niter = 20
    verbose = True
    d = x.shape[1]
    kmeans = faiss.Kmeans(d, num_centroids, niter, verbose)
    kmeans.train(x)

    index = faiss.IndexFlatL2(d)
    index.add(x)
    distance_list, indices = index.search(kmeans.centroids, 15)
    print("distance is {}".format(distance_list[:10]))
    print("distance is {}".format(distance_list[-10:]))


def faiss_pca():
    mt = np.random.rand(1000, 40).astype('float32')
    mat = faiss.PCAMatrix(40, 10)
    mat.train(mt)
    assert mat.is_trained
    tr = mat.apply_py(mt)
    print((tr ** 2).sum(0))


if __name__ == '__main__':
    faiss_pca()
