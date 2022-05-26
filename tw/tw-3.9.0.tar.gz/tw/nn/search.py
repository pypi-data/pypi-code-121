# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Search
"""

from torch import nn
import numpy as np

try:
  from .csrc.nearest_neighbors.lib.python import nearest_neighbors
except ImportError:
  pass


class KnnSearch(nn.Module):

  def __init__(self, k):
    """[summary]

    Args:
        k: Number of neighbours in knn search
    """
    super(KnnSearch, self).__init__()
    self.k = k
    self.omp = True

  def forward(self, support_pts, query_pts):
    """[summary]

    Args:
        support_pts: points you have, B*N1*3
        query_pts: points you want to know the neighbour index, B*N2*3

    Returns:
        neighbor_idx: neighboring points indexes, B*N2*k
    """
    assert isinstance(support_pts, np.ndarray) and isinstance(query_pts, np.ndarray)
    neighbor_idx = nearest_neighbors.knn_batch(support_pts, query_pts, self.k, omp=self.omp)
    return neighbor_idx.astype(np.int32)
