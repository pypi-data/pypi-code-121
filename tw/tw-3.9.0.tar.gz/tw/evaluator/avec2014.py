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
"""avec2014 dataset evaluator"""
import math
import re
import numpy as np
from .base import Evaluator


class RegressionEvaluator(Evaluator):
  def __init__(self, root=None):
    super(RegressionEvaluator, self).__init__(root=root)

  def accumulate(self):
    r"""unzip each tuple. compute mae and rmse.
      metric layout: [preds, targets, (paths)]
    """
    total = []
    for batch in self.metrics:
      for content in zip(*batch):
        total.append(content)

    preds = []
    targets = []
    if self.root is not None:
      path = self.root + '/result.txt'
      with open(path, 'w') as fw:
        for res in total:
          pred = res[0].cpu().item()
          target = res[1].cpu().item()
          preds.append(pred)
          targets.append(target)
          fw.write('{} {} {}\n'.format(res[2], target, pred))

    preds = np.array(preds)
    targets = np.array(targets)
    error = preds - targets
    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error * error))

    return {'mae': mae, 'rmse': rmse}


class Avec2014Evaluator(Evaluator):

  def __init__(self):
    super(Avec2014Evaluator, self).__init__(root='./')

  def scatter_idd_pred(self, gt_pred_path):
    pps = []
    with open(gt_pred_path) as fp:
      for line in fp:
        pp, gt, pred = line.split(' ')[:3]
        pps.append((float(gt), float(pred), pp[:3]))

    pps = sorted(pps, key=lambda x: x[0])
    num = float(len(pps))

    mae, rmse, it0, it1 = 0.0, 0.0, 0.0, 0.0
    for it in pps:
      error = it[0] - it[1]
      mae += abs(error)
      rmse += (error) ** 2
      it0 += it[0]
      it1 += it[1]

    # * compute ccc
    it0, it1, sx2, sy2, sxy = it0 / 50, it1 / 50, 0.0, 0.0, 0.0
    for it in pps:
      sx2 += (it[0] - it0) ** 2
      sy2 += (it[1] - it1) ** 2
      sxy += (it[0] - it0) * (it[1] - it1)
    ccc = 2.0 * (sxy / num) / (sx2 / num + sy2 / num + (it0 - it1)**2)

    # * compute pcc
    sxy, sx, sy, sx2, sy2 = 0.0, 0.0, 0.0, 0.0, 0.0
    for it in pps:
      sx += it[0]
      sy += it[1]
      sxy += it[0] * it[1]
      sx2 += it[0] * it[0]
      sy2 += it[1] * it[1]
    pcc = (sxy - sx * sy / num) / math.sqrt((sx2 - sx * sx / num) * (sy2 - sy * sy / num))

    # * return
    mae, rmse = mae / num, math.sqrt(rmse / num)
    return mae, rmse, ccc, pcc

  def get_list(self, path):
    """ For image input
        class1 2 3.56
        class1 2 4.32
        class1 2 1.23
        ...
        class2 3 2.11
        ...
    Return:
        Note: the logit will be mean of the value,
          because the label is same value in same class
        {'class1':[label, logit], ...}
    """
    res_fp = open(path, 'r')
    res_label = {}
    res_logit = {}
    res_weight = {}
    for line in res_fp:
      line = line.replace('/', '\\')
      r1 = re.findall('frames_flow\\\\(.*?)_video', line)
      r2 = re.findall('frames\\\\(.*?)_video', line)

      idd = r1[0] if len(r1) else r2[0]

      res = line.split(' ')
      label, logit = float(res[1]), float(res[2])

      if idd not in res_label:
        res_label[idd] = []
      res_label[idd].append(label)

      if idd not in res_logit:
        res_logit[idd] = []
      res_logit[idd].append(logit)

      if len(res) == 4:
        if idd not in res_weight:
          res_weight[idd] = []
        weight = float(res[3])
        res_weight[idd].append(weight)

    # normalize
    # if len(res_weight):
    #   for idd in res_weight:
    #     res_weight[idd] = np.array(res_weight[idd])
    #     res_weight[idd] = (res_weight[idd] - np.min(res_weight[idd])) / \
    #         (np.max(res_weight[idd]) - np.min(res_weight[idd]))

    # acquire mean
    result = {}
    for pp in res_label:
      label = np.mean(np.array(res_label[pp]))
      logit = np.mean(np.array(res_logit[pp]))

      if len(res_weight):
        #!< fashion-1 select max/min item
        # ind = np.argsort(res_weight[pp])
        # size = len(ind) if int(len(ind) * 0.1) == 0 else int(len(ind) * 0.1)
        # logit = 0.0
        # for i in range(size):
        #   print(i, ind[0], res_weight[pp][ind[0]], res_logit[pp][ind[0]], label)
        #   logit += res_logit[pp][ind[0]]
        # logit /= size

        #!< fashion-2 directly weight
        # logit = np.mean(np.array(res_weight[pp])*res_logit[pp])

        #!< fashion-3 partion weight
        # weight = np.mean(res_weight[pp])
        # logit = np.sum(weight*res_logit[pp])

        result[pp] = [label, logit, np.mean(res_weight[pp])]

      else:
        result[pp] = [label, logit]

    return result

  def get_mae_rmse(self, res):
    """Input: a dict
      { 'class1':[label value], 'class2':[label value] }
    """
    mae = 0.0
    rmse = 0.0
    for idx in res:
      mae += abs(res[idx][0] - res[idx][1])
      rmse += math.pow(res[idx][0] - res[idx][1], 2)
    mae = mae / len(res)
    rmse = math.sqrt(rmse / len(res))
    return mae, rmse, len(res)

  def measure(self, path):
    r"""pred_metrics format:
      [(path1, label, logits), (path2, label, logits),]
    """
    # get list
    res_dict = self.get_list(path)
    # compute each identity
    dst_path = path.split('.txt')[0] + '_pp.txt'
    with open(dst_path, 'w') as fw:
      for k, v in res_dict.items():
        if len(v) == 2:
          fw.write('{} {} {}\n'.format(k, v[0], v[1]))
        if len(v) == 3:
          fw.write('{} {} {} {}\n'.format(k, v[0], v[1], v[2]))
    # mae, rmse, ccc, pcc
    return self.scatter_idd_pred(dst_path)

  def accumulate(self):
    r"""accumulate total results"""
    # collect
    total = []
    for batch in self.metrics:
      for content in zip(*batch):
        total.append(content)

    # writing items
    path = self.root + '/avec2014.txt'
    with open(path, 'w') as fw:
      if len(total[0]) == 3:
        for pred in total:
          fw.write('%s %d %.8f\n' % (pred[0], pred[1], pred[2]))
      elif len(total[0]) == 4:
        for pred in total:
          fw.write('%s %d %.8f %.8f\n' % (pred[0], pred[1], pred[2], pred[3]))

    mae, rmse, ccc, pcc = self.measure(path)
    return {'video_mae': mae, 'video_rmse': rmse, 'video_ccc': ccc, 'video_pcc': pcc}  # nopep8
