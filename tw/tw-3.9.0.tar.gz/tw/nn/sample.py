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
"""Sample
"""

import math
import torch
import torch.nn as nn
import numpy as np

try:
  from .csrc.grid_subsampling import grid_subsampling
except ImportError:
  pass

#!<-----------------------------------------------------------------------------
#!< GMM Sampler
#!<-----------------------------------------------------------------------------


class GMMSampler():

  def __init__(self, stds):
    r"""Sample from GMM distribution.

    Args:
      stds: [feature_dim, num_components]

    """

    # set [1, feature_dim, num_components]
    self.stds = torch.from_numpy(np.array(stds)).float().unsqueeze(dim=0)
    self.num_components = self.stds.shape[-1]
    self.num_features = self.stds.shape[-2]
    assert len(self.stds.shape) == 3

  @classmethod
  def gauss_density_centered(self, x, std):
    r"""single gaussian distribution."""
    return torch.exp(-0.5 * (x / std)**2) / (math.sqrt(2 * math.pi) * std)

  @classmethod
  def gmm_density_centered(self, x, std):
    if x.dim() == std.dim() - 1:
      x = x.unsqueeze(-1)
    elif not (x.dim() == std.dim() and x.shape[-1] == 1):
      raise ValueError('Last dimension must be the gmm stds.')
    prob = self.gauss_density_centered(x, std)
    return prob.prod(-2).mean(-1)

  def __call__(self, num_samples):
    r"""Sample from GMM dist

      Args:
        center: [k, 1] sampled values
        prob: [k, ] value via probablity
    """
    # sample component ids
    k = torch.randint(self.num_components, (num_samples,)).long()
    std_samp = self.stds[0, :, k].t()
    center = std_samp * torch.randn(num_samples, self.num_features)
    prob = self.gmm_density_centered(center, self.stds)
    return center, prob


class GridSubSampling(nn.Module):

  def __init__(self, grid_size=0.1, verbose=0):
    """CPP wrapper for a grid sub_sampling (method = barycenter for points and features
    Args:
        grid_size: parameter defining the size of grid voxels
        verbose: 1 to display
    """
    super(GridSubSampling, self).__init__()
    self.grid_size = grid_size
    self.verbose = verbose

  def forward(self, points, features=None, labels=None):
    """inference

    Args:
        points: (N, 3) matrix of input points
        features: optional (N, d) matrix of features (floating number)
        labels: optional (N,) matrix of integer labels

    Returns:
        sub_sampled points, with features and/or labels depending of the input
    """
    assert isinstance(points, np.ndarray)
    if (features is None) and (labels is None):
      return grid_subsampling.compute(points, sampleDl=self.grid_size, verbose=self.verbose)
    elif labels is None:
      return grid_subsampling.compute(points, features=features, sampleDl=self.grid_size, verbose=self.verbose)
    elif features is None:
      return grid_subsampling.compute(points, classes=labels, sampleDl=self.grid_size, verbose=self.verbose)
    else:
      return grid_subsampling.compute(points, features=features, classes=labels,
                                      sampleDl=self.grid_size, verbose=self.verbose)
