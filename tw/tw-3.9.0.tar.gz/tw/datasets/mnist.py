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
import tw
import tw.transform as T


class Mnist(torch.utils.data.Dataset):

  def __init__(self, path, transform, **kwargs):
    tw.fs.raise_path_not_exist(path)
    res, _ = tw.parser.parse_from_text(path, [str, int], [True, False])
    self.targets = []
    for path, label in zip(res[0], res[1]):
      self.targets.append((path, label))
    self.transform = transform

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.GRAY)
    img_meta.label = self.targets[idx][1]
    return self.transform([img_meta.load().numpy()])
