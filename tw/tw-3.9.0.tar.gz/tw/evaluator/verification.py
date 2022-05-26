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

from .base import Evaluator


class VerificationEvaluator(Evaluator):
  r"""For verification task: one by one.
  """

  def __init__(self, dist='cosine', threshold='median', root=None):
    super(VerificationEvaluator, self).__init__(root=root)

    assert dist in ['cosine', 'binary'], "the dist of prediction."
    if dist == 'cosine':
      assert threshold in ['median']

    self.dist = dist
    self.threshold = threshold
    self.metrics = []

  def append(self, values):
    r"""append values"""
    for tup in zip(*values):
      if len(tup) == 2:
        # pred, target
        self.metrics.append((tup[0], tup[1]))
      elif len(tup) == 3:
        # pred, target, path
        self.metrics.append((tup[0], tup[1], tup[2]))
      else:
        raise NotImplementedError

  def accumulate(self):
    r"""accumulate total results"""
    acc = 0.0

    # cosine metric: [-1, 1] the larger value stands for more similar.
    if self.dist == 'cosine':
      pairs = sorted(self.metrics, key=lambda x: x[0], reverse=True)
      for i, pair in enumerate(pairs):
        if i < len(pairs) // 2 and pair[1] == 1:
          acc += 1
        elif i >= len(pairs) // 2 and pair[1] == 0:
          acc += 1
      acc /= len(pairs)

    elif self.dist == 'binary':
      for i, pair in enumerate(self.metrics):
        if pair[0] > self.threshold and pair[1] == 1:
          acc += 1
        elif pair[0] <= self.threshold and pair[1] == 0:
          acc += 1
      acc /= len(self.metrics)

    else:
      raise NotImplementedError

    # write to file
    if self.root is not None and len(self.metrics[0]) == 3:
      with open('{}/result.txt'.format(self.root), 'w') as fw:
        text = ''
        for pair in self.metrics:
          text += '{} {} {} {}\n'.format(pair[2][0], pair[2][1], pair[1], pair[0])  # nopep8
        fw.write(text)

    return {'acc': acc}
