# Copyright (c) 2015-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD+Patents license found in the
# LICENSE file in the root directory of this source tree.

import numpy as np

try:
    from pyxtools.faiss_tools import faiss
except ImportError:
    from pyxtools.pyxtools.faiss_tools import faiss


def test_1():
    d = 64  # dimension
    nb = 100000  # database size
    nq = 10000  # nb of queries
    np.random.seed(1234)  # make reproducible
    xb = np.random.random((nb, d)).astype('float32')
    xb[:, 0] += np.arange(nb) / 1000.
    xq = np.random.random((nq, d)).astype('float32')
    xq[:, 0] += np.arange(nq) / 1000.

    nlist = 100
    m = 8
    k = 4
    quantizer = faiss.IndexFlatL2(d)  # this remains the same
    index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)
    # 8 specifies that each sub-vector is encoded as 8 bits
    index.train(xb)
    index.add(xb)
    distance_list, indices = index.search(xb[:5], k)  # sanity check
    print(indices)
    print(distance_list)

    index.nprobe = 10  # make comparable with experiment above
    distance_list, indices = index.search(xq, k)  # search
    print(indices[:5])
    print(distance_list[:5])


def test_2():
    d = 64  # dimension
    nb = 100000  # database size
    nq = 10000  # nb of queries
    np.random.seed(1234)  # make reproducible
    xb = np.random.random((nb, d)).astype('float32')
    xb[:, 0] += np.arange(nb) / 1000.
    xq = np.random.random((nq, d)).astype('float32')
    xq[:, 0] += np.arange(nq) / 1000.

    nlist = 100
    m = 8
    k = 4
    quantizer = faiss.IndexFlatL2(d)  # this remains the same
    index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)
    # 8 specifies that each sub-vector is encoded as 8 bits
    index.train(xb)
    index.add(xb)
    distance_list, indices = index.search(xb[:5], k)  # sanity check
    print(indices)
    print(distance_list)

    index.nprobe = 10  # make comparable with experiment above
    distance_list, indices = index.search(xq, k)  # search
    print(indices[:5])
    print(distance_list[:5])


if __name__ == '__main__':
    test_1()
    test_2()
