# Copyright 2017 The KaiJIN Authors. All Rights Reserved.
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
import os
import torch
from torch.utils import data as td
import tw


#!<---------------------------------------------------------------
#!< COLLARTOR
#!<---------------------------------------------------------------


class SampleCollator():
  def __call__(self, wrapped_batch):
    return wrapped_batch

#!<---------------------------------------------------------------
#!< SAMPLER
#!<---------------------------------------------------------------

#!<---------------------------------------------------------------
#!< BATCH SAMPLER
#!<---------------------------------------------------------------


class BatchMultiSampler(td.Sampler):
  r"""Wraps a list of sampler to yield a mini-batch of indices.

  Note:
    the method will randomly select a sampler to sample a mini-batch of indeices,
    which is useful for keeping same input size among a mini-batch but with different
    samplers to sample different size of mini-batch.

  Args:
      sampler (list(Sampler)): a list of base sampler.
      batch_size (int): Size of mini-batch.
      drop_last (bool): If ``True``, the sampler will drop the last batch if
          its size would be less than ``batch_size``
  """

  def __init__(self, samplers, batch_size, drop_last):
    assert isinstance(samplers, (tuple, list))
    assert drop_last
    for sampler in samplers:
      if not isinstance(sampler, td.Sampler):
        raise ValueError("sampler should be an instance of torch.utils.data.Sampler, but got sampler={}" .format(sampler))  # nopep8
    if not isinstance(drop_last, bool):
      raise ValueError("drop_last should be a boolean value, but got drop_last={}".format(drop_last))  # nopep8

    self.samplers = samplers
    self.total_samples = sum([len(s) for s in self.samplers])
    self.batch_size = batch_size
    self.drop_last = drop_last
    self.sampler_indices = None
    self.step = 0

  def _get_rand_sampler(self):
    if self.step % len(self.samplers) == 0:
      self.sampler_indices = torch.randperm(len(self.samplers)).tolist()
    sampler = self.samplers[self.sampler_indices[self.step % len(self.samplers)]]  # nopep8
    self.step += 1
    return sampler

  def __iter__(self):
    batch = []
    for _ in range(len(self)):
      sampler = self._get_rand_sampler()
      for idx in sampler:
        batch.append(idx)
        if len(batch) == self.batch_size:
          break
      yield batch
      batch = []

  def __len__(self):
    if self.drop_last:
      return self.total_samples // self.batch_size
    else:
      return (self.total_samples + self.batch_size - 1) // self.batch_size
