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
"""interpolation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


def pixel_unshuffle(input, downscale_factor):
  '''
  input: batchSize * c * k*w * k*h
  kdownscale_factor: k
  batchSize * c * k*w * k*h -> batchSize * k*k*c * w * h
  '''
  c = input.shape[1]

  kernel = torch.zeros(size=[downscale_factor * downscale_factor * c,
                             1, downscale_factor, downscale_factor],
                       device=input.device)
  for y in range(downscale_factor):
    for x in range(downscale_factor):
      kernel[x + y * downscale_factor::downscale_factor * downscale_factor, 0, y, x] = 1
  return F.conv2d(input, kernel, stride=downscale_factor, groups=c)


class PixelUnshuffle(nn.Module):
  """https://github.com/fedral/PixelUnshuffle-pytorch
  """

  def __init__(self, downscale_factor):
    super(PixelUnshuffle, self).__init__()
    self.downscale_factor = downscale_factor

  def forward(self, input):
    '''
    input: batchSize * c * k*w * k*h
    kdownscale_factor: k
    batchSize * c * k*w * k*h -> batchSize * k*k*c * w * h
    '''

    return pixel_unshuffle(input, self.downscale_factor)
