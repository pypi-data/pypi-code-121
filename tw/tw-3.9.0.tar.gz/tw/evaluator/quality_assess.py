# Copyright 2018 The KaiJIN Authors. All Rights Reserved.
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
"""Quality Assessment
"""
import numpy as np
from scipy import stats
from .base import Evaluator


class QualityAssessEvaluator(Evaluator):
  """Generally, for quality assessment task, during testing, we randomly cropped
   num patches to inference.

      if repeat == 0, inference once dataset.
      else inference 'repeat' dataset and take average.

  Args:
      Evaluator ([type]): [description]
  """

  def __init__(self):
    super(QualityAssessEvaluator, self).__init__()
    self.predictions = []
    self.labels = []
    self.repeat = 0

  def reset(self):
    self.predictions = []
    self.labels = []

  def append(self, preds, labels):
    """quality assessment evalutor

    Args:
        preds ([torch.Tensor([N,])]): prediction score of video clip or image.
        labels ([torch.Tensor([N,])]): reference score of video clip of image/
    """
    for pred, label in zip(preds.cpu().numpy(), labels.cpu().numpy()):
      self.predictions.append(pred)
      self.labels.append(label)

  def accumulate(self):
    """compute index.
      - MAE
      - RMSE
      - PLCC
      - SRCC
      - KRCC
    """
    predictions = np.array(self.predictions)
    labels = np.array(self.labels)

    # if self.repeat > 0:
    #   predictions = np.mean(np.reshape(predictions, [self.repeat, -1]), axis=0)
    #   labels = np.mean(np.reshape(labels, [self.repeat, -1]), axis=0)

    # plcc = stats.pearsonr(labels, predictions)[0]
    srocc = np.abs(stats.spearmanr(labels, predictions)[0])
    krocc = np.abs(stats.stats.kendalltau(labels, predictions)[0])
    plcc = np.abs(stats.pearsonr(labels, predictions)[0])
    rmse = np.sqrt(((labels - predictions) ** 2).mean())
    mae = np.abs((labels - predictions)).mean()

    # fit_func = np.polyfit(predictions, labels, deg=3)
    # fit_pred = np.polyval(fit_func, predictions)
    # plcc_fit = np.abs(np.corrcoef(fit_pred, labels)[0, 1])

    return {'mae': mae, 'rmse': rmse, 'srocc': srocc, 'plcc': plcc, 'krocc': krocc}
