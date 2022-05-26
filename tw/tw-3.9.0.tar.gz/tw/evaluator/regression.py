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
import torch
import numpy as np
from .base import Evaluator


class RegressionEvaluator(Evaluator):
  def __init__(self, root=None):
    super(RegressionEvaluator, self).__init__(root=root)

  def compute(self, inputs, targets):
    
    b = inputs.size(0)
    inputs = inputs.reshape(b, -1)
    targets = targets.reshape(b, -1)
    
    mae = (inputs - targets).abs().mean(dim=1).squeeze()
    mse = (inputs - targets).pow(2).mean(dim=1).sqrt().squeeze()
    
    return mae, mse

  def accumulate(self):
    """unzip each tuple. compute mae and rmse.
      metric layout: [preds, targets, (paths)]
    """
    mae, mse = [], []
    for batch in self.metrics:
      mae.append(batch[0])
      mse.append(batch[1])
    mae = torch.stack(mae, dim=0).mean().item()
    rmse = torch.stack(mse, dim=0).mean().item()

    return {'mae': mae, 'rmse': rmse}
