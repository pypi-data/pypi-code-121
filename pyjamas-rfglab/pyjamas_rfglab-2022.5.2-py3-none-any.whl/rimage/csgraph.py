"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# This code was taken straight from scipy.sparse.csgraph._tools.pyx. It corresponds
# to three functions that I merged into a single one for optimization purposes.
# Author: Jake Vanderplas  -- <vanderplas@astro.washington.edu>

import numpy as np
from scipy.sparse import csr_matrix

DTYPE = np.float64
ITYPE = np.int32


def csgraph_from_dense(graph):
    """
    csgraph_from_dense(graph, null_value=0, nan_null=True, infinity_null=True)
    Construct a CSR-format sparse graph from a dense matrix.
    .. versionadded:: 0.11.0
    Parameters
    ----------
    graph : array_like
        Input graph.  Shape should be (n_nodes, n_nodes).
    null_value : float or None (optional)
        Value that denotes non-edges in the graph.  Default is zero.
    infinity_null : bool
        If True (default), then infinite entries (both positive and negative)
        are treated as null edges.
    nan_null : bool
        If True (default), then NaN entries are treated as non-edges
    Returns
    -------
    csgraph : csr_matrix
        Compressed sparse representation of graph,
    Examples
    --------
    >>> from scipy.sparse.csgraph import csgraph_from_dense
    >>> graph = [
    ... [0, 1 , 2, 0],
    ... [0, 0, 0, 1],
    ... [0, 0, 0, 3],
    ... [0, 0, 0, 0]
    ... ]
    >>> csgraph_from_dense(graph)
    <4x4 sparse matrix of type '<class 'numpy.float64'>'
        with 4 stored elements in Compressed Sparse Row format>
    """

    # check that graph is a square matrix
    if graph.ndim != 2:
        raise ValueError("graph should have two dimensions")
    N = graph.shape[0]
    if graph.shape[1] != N:
        raise ValueError("graph should be a square array")

    # flag all the null edges
    graph = np.ma.masked_invalid(graph, copy=False)

    # check that graph is a square matrix
    graph = np.ma.asarray(graph)

    # construct the csr matrix using graph and mask
    data = graph.compressed()
    mask = ~graph.mask

    data = np.asarray(data, dtype=DTYPE, order='c')

    idx_grid = np.empty((N, N), dtype=ITYPE)
    idx_grid[:] = np.arange(N, dtype=ITYPE)
    indices = np.asarray(idx_grid[mask], dtype=ITYPE, order='c')

    indptr = np.zeros(N + 1, dtype=ITYPE)
    indptr[1:] = mask.sum(1).cumsum()

    return csr_matrix((data, indices, indptr), (N, N))

