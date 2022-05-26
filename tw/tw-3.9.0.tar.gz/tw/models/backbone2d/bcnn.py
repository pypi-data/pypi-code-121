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
"""Bilinear CNN"""
import torch
import torch.nn as nn
import tw
from .vgg import vgg16


class BilinearCNN(nn.Module):
  r"""B-CNN from paper:
    "Bilinear CNN models for fine-grained visual recognition"
  """

  def __init__(self, num_classes=1000):
    super(BilinearCNN, self).__init__()
    self.features = vgg16()
    self.classifier = nn.Linear(512 ** 2, num_classes)
    # reset params
    tw.nn.initialize.kaiming(self.classifier)

  def forward(self, inputs):
    x = self.features(inputs)
    x = x.view(-1, 512, 28 ** 2)
    x = torch.bmm(x, x.permute(0, 2, 1))
    x = torch.div(x, 28 ** 2)
    x = x.view(-1, 512 ** 2)
    x = torch.sign(x) * torch.sqrt(x + 1e-5)
    x = nn.functional.normalize(x, p=2, dim=1)
    x = self.classifier(x)
    return x


if __name__ == "__main__":
  model = BilinearCNN(30)
  model.forward(torch.random(1, 3, 224, 224))
