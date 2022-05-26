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
""" References
----------
[1] Tran, Du, et al. "Learning spatiotemporal features with 3d convolutional networks."
Proceedings of the IEEE international conference on computer vision. 2015.
"""

import torch.nn as nn


class C3D(nn.Module):
  def __init__(self, num_classes=487):
    super(C3D, self).__init__()

    self.conv1 = nn.Conv3d(3, 64, (3, 3, 3), padding=(1, 1, 1))
    self.pool1 = nn.MaxPool3d((1, 2, 2), stride=(1, 2, 2))

    self.conv2 = nn.Conv3d(64, 128, (3, 3, 3), padding=(1, 1, 1))
    self.pool2 = nn.MaxPool3d((2, 2, 2), stride=(2, 2, 2))

    self.conv3a = nn.Conv3d(128, 256, (3, 3, 3), padding=(1, 1, 1))
    self.conv3b = nn.Conv3d(256, 256, (3, 3, 3), padding=(1, 1, 1))
    self.pool3 = nn.MaxPool3d((2, 2, 2), stride=(2, 2, 2))

    self.conv4a = nn.Conv3d(256, 512, (3, 3, 3), padding=(1, 1, 1))
    self.conv4b = nn.Conv3d(512, 512, (3, 3, 3), padding=(1, 1, 1))
    self.pool4 = nn.MaxPool3d((2, 2, 2), stride=(2, 2, 2))

    self.conv5a = nn.Conv3d(512, 512, (3, 3, 3), padding=(1, 1, 1))
    self.conv5b = nn.Conv3d(512, 512, (3, 3, 3), padding=(1, 1, 1))
    self.pool5 = nn.MaxPool3d((2, 2, 2), stride=(2, 2, 2), padding=(0, 1, 1))

    # [NOTE] we add a global average pooling.
    self.gap = nn.AdaptiveAvgPool3d((1, 1, 1))

    self.fc6 = nn.Linear(512, 512)
    self.fc7 = nn.Linear(512, 512)
    self.fc8 = nn.Linear(512, num_classes)

    self.dropout = nn.Dropout(p=0.5)
    self.relu = nn.ReLU()
    self.endpoints = {}

  def forward(self, x):
    """x is a 5-d tensor: a batch (n, ch, fr, h, w).
    """
    h = self.relu(self.conv1(x))
    h = self.pool1(h)

    h = self.relu(self.conv2(h))
    h = self.pool2(h)

    h = self.relu(self.conv3a(h))
    h = self.relu(self.conv3b(h))
    h = self.pool3(h)

    h = self.relu(self.conv4a(h))
    h = self.relu(self.conv4b(h))
    h = self.pool4(h)

    h = self.relu(self.conv5a(h))
    h = self.relu(self.conv5b(h))
    h = self.pool5(h)
    h = self.gap(h)
    self.endpoints['gap'] = h
    h = h.view(-1, 512)

    h = self.relu(self.fc6(h))
    self.endpoints['fc6'] = h
    h = self.dropout(h)

    h = self.relu(self.fc7(h))
    self.endpoints['fc7'] = h
    h = self.dropout(h)

    logits = self.fc8(h)
    # [NOTE] where we remove out the softmax layer to construct a l2 loss

    return logits
