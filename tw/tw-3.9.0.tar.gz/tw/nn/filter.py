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
r"""Filters

  - blur
  - filter
  - gaussian
  - laplacian
  - media
  - motion
  - sobel

"""

import torch
from torch import nn
from torch.nn import functional as F


class GradientIntensity(nn.Module):

  r"""Compute input gradient intensity considering sqrt(x^2 + y^2)
  """

  def __init__(self):
    super(GradientIntensity, self).__init__()
    kernel_v = [[0, -1, 0],
                [0, 0, 0],
                [0, 1, 0]]
    kernel_h = [[0, 0, 0],
                [-1, 0, 1],
                [0, 0, 0]]
    kernel_h = torch.FloatTensor(kernel_h).unsqueeze(0).unsqueeze(0)
    kernel_v = torch.FloatTensor(kernel_v).unsqueeze(0).unsqueeze(0)
    self.weight_h = nn.Parameter(data=kernel_h, requires_grad=False)
    self.weight_v = nn.Parameter(data=kernel_v, requires_grad=False)

  def forward(self, x):

    x_list = []
    for i in range(x.shape[1]):
      x_i = x[:, i]
      x_i_v = F.conv2d(x_i.unsqueeze(1), self.weight_v, padding=1)
      x_i_h = F.conv2d(x_i.unsqueeze(1), self.weight_h, padding=1)
      x_i = torch.sqrt(torch.pow(x_i_v, 2) + torch.pow(x_i_h, 2) + 1e-6)
      x_list.append(x_i)

    x = torch.cat(x_list, dim=1)
    return x
