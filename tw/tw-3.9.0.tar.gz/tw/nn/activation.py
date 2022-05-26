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
"""activation
"""
import torch
from torch import nn
from torch.nn import functional as F


class SwishImplementation(torch.autograd.Function):

  @staticmethod
  def forward(ctx, i):
    result = i * torch.sigmoid(i)
    ctx.save_for_backward(i)
    return result

  @staticmethod
  def backward(ctx, grad_output):
    i = ctx.saved_variables[0]
    sigmoid_i = torch.sigmoid(i)
    return grad_output * (sigmoid_i * (1 + i * (1 - sigmoid_i)))


class MemoryEfficientSwish(nn.Module):

  def forward(self, x):
    return SwishImplementation.apply(x)


Swish = MemoryEfficientSwish


def mish(x, inplace: bool = False):
  """Mish: A Self Regularized Non-Monotonic Neural Activation Function
    - https://arxiv.org/abs/1908.08681
  """
  return x.mul(F.softplus(x).tanh())


class Mish(nn.Module):
  """Mish: A Self Regularized Non-Monotonic Neural Activation Function
    - https://arxiv.org/abs/1908.08681
  """

  def __init__(self, inplace: bool = False):
    super(Mish, self).__init__()

  def forward(self, x):
    return mish(x)


def sigmoid(x, inplace: bool = False):
  return x.sigmoid_() if inplace else x.sigmoid()
