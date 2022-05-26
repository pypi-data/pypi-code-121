# Copyright 2022 The KaiJIN Authors. All Rights Reserved.
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
"""Landmark Evaluator
"""
import numpy as np
from .base import Evaluator


class FaceLandmarkEvaluator(Evaluator):

  def __init__(self, dataset=None, root=None):
    super(FaceLandmarkEvaluator, self).__init__()
    self.dataset = dataset
    self.metrics = []
    self.root = root

    # compute for NME
    if self.dataset == '300W':
      self.norm_indices = [36, 45]
    elif self.dataset == 'COFW':
      self.norm_indices = [8, 9]
    elif self.dataset == 'WFLW':
      self.norm_indices = [60, 72]
    else:
      self.norm_indices = None

  def reset(self):
    """reset accumulate information"""
    self.metrics = []

  def compute(self, preds, targets, average=False):
    """compute distance

    Args:
        preds ([N, K, P]):
        targets ([N, K, P]):

    Return:

    """
    assert preds.ndim == targets.ndim == 3
    n, k, p = preds.shape

    preds = preds.cpu().numpy()
    targets = targets.cpu().numpy()

    if self.norm_indices is not None:
      norm = np.linalg.norm(targets[:, self.norm_indices[0]] - targets[:, self.norm_indices[1]], axis=1)
    else:
      norm = 1

    nme_all = np.linalg.norm(preds - targets, axis=2) / norm
    nme = np.mean(nme_all, axis=1)

    return nme, nme_all

  def append(self, values):
    """append values"""
    self.metrics.append(values)

  def accumulate(self):
    """accumulate total results"""
    nmes, nmes_all = [], []
    for m, m_all in self.metrics:
      nmes.append(m)
      nmes_all.append(m_all)
    nmes = np.concatenate(nmes, axis=0)
    nmes_all = np.concatenate(nmes_all, axis=0)

    from scipy.integrate import simps

    thres = 0.1
    step = 0.0001
    num_data = len(nmes)
    xs = np.arange(0, thres + step, step)
    ys = np.array([np.count_nonzero(nmes <= x) for x in xs]) / float(num_data)
    fr = 1.0 - ys[-1]
    auc = simps(ys, x=xs) / thres

    return {'nme': np.mean(nmes) * 100, 'fr': fr, 'auc': auc, 'nme_all': str((np.mean(nmes_all, axis=0) * 100).tolist())}

  def __len__(self):
    return len(self.metrics)
