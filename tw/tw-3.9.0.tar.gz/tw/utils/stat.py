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
import sys
import torch


class AverMeter:

  def __init__(self, name=None):
    """Computes and stores the average and current value"""
    self.name = name
    self.val = 0
    self.avg = 0
    self.sum = 0
    self.count = 0
    self.max = sys.float_info.min
    self.min = sys.float_info.max
    self.reset()

  def reset(self):
    self.val = 0
    self.avg = 0
    self.sum = 0
    self.count = 0
    self.max = sys.float_info.min
    self.min = sys.float_info.max

  def update(self, val):
    self.max = self.max if self.max > val else val
    self.min = self.min if self.min < val else val
    self.val = val
    self.sum += val
    self.count += 1
    self.avg = self.sum / self.count

  def __str__(self):
    return "(name:{}, val:{}, max:{}, min:{}. avg:{}, sum:{}, count:{})".format(
        self.name, self.val, self.max, self.min, self.avg, self.sum, self.count)


class AverSet:
  def __init__(self):
    """Collect network training stats info"""
    self._db = {}

  def reset(self, key=None):
    if key is None:
      for each_key in self._db:
        self._db[each_key].reset()
    else:
      self._db[key].reset()

  def update(self, keys, vals=None):
    """if keys is a dict represents {'key': val, 'key': vale}"""
    if isinstance(keys, dict):
      return self.update(list(keys.keys()), list(keys.values()))
    # normal method
    for tup in zip(keys, vals):
      if tup[0] not in self._db:
        self._db[tup[0]] = AverMeter(name=tup[0])
      if isinstance(tup[1], torch.Tensor):
        val = tup[1].item()
      else:
        val = tup[1]
      self._db[tup[0]].update(val)

  def keys(self):
    return list(self._db.keys())

  def values(self):
    return [self._db[key].avg for key in self._db]

  def __str__(self):
    rets = ""
    for idx, key in enumerate(self._db):
      if idx == 0:
        rets = "{0}:{1:.3f}".format(key, self._db[key].avg)
      elif key == "lr":
        rets += ", {0}:{1:.6f}".format(key, self._db[key].avg)
      else:
        rets += ", {0}:{1:.3f}".format(key, self._db[key].avg)
    return rets

  def __getitem__(self, key):
    return self._db[key]
