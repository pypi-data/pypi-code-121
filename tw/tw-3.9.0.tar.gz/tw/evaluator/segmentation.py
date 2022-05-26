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
import functools
import numpy as np
from scipy.ndimage import gaussian_filter
from sklearn.metrics import confusion_matrix

import torch
from torch.nn import functional as F

from .base import Evaluator


def div(a, b):
  return np.divide(a, b, out=np.zeros_like(a).astype('float'), where=b != 0)


def display_confusion_matrix(conf_matrix: np.ndarray, names, column_width=10):

  cw = column_width
  num_row, num_col = conf_matrix.shape
  assert num_row == num_col, "confusion matrix should a square."

  names = [name[:cw - 2] for name in names]

  total = np.sum(conf_matrix)

  sep = '-' * (num_col + 2) * cw

  s = '\n'
  s += sep + '\n'
  s += '[Sample of Different Classification]\n'
  s += sep + '\n'
  title_style = '{:^%d}' % (cw) * (num_col + 2) + '\n'
  title = title_style.format(*['Category', *names, 'Sum Reals'])
  s += title
  s += sep + '\n'
  row_style = '{:^%d}' % (cw) * (num_col + 2) + '\n'
  for i, row in enumerate(conf_matrix):
    s += row_style.format(*[names[i], *row, np.sum(row)])
  s += row_style.format(*['Sum Preds', *np.sum(conf_matrix, axis=0), total])

  s += sep + '\n'
  s += '[Recall Matrix]\n'
  s += sep + '\n'
  s += title
  s += sep + '\n'
  row_style = '{:^%d}' % (cw) * (num_col + 2) + '\n'
  mean = []
  for i, row in enumerate(conf_matrix):
    recall = ['{:.2f}'.format(div(r * 100.0, np.sum(row))) for r in row]
    mean.append(div(row[i] * 100.0, np.sum(row)))
    s += row_style.format(*[names[i], *recall, '{:.2f}'.format(100 * np.sum(row) / total)])
  s += row_style.format(*['Sum Preds', *['{:.2f}'.format(v * 100 / total)
                        for v in np.sum(conf_matrix, axis=0)], '{:.2f}'.format(np.mean(mean))])

  s += sep + '\n'
  s += '[IoU Matrix]\n'
  s += sep + '\n'
  s += title
  s += sep + '\n'
  row_style = '{:^%d}' % (cw) * (num_col + 2) + '\n'
  mean = []
  for i, row in enumerate(conf_matrix):
    iou = ['{:.2f}'.format(div(r * 100.0, (np.sum(conf_matrix[:, i]) + np.sum(row) - r))) for r in row]
    mean.append(div(row[i] * 100.0, (np.sum(conf_matrix[:, i]) + np.sum(row) - row[i])))
    s += row_style.format(*[names[i], *iou, '{:.2f}'.format(100 * np.sum(row) / total)])
  s += row_style.format(*['Sum Preds', *['{:.2f}'.format(v * 100 / total)
                        for v in np.sum(conf_matrix, axis=0)], '{:.2f}'.format(np.mean(mean))])

  s += sep + '\n'
  s += '[Precision Matrix]\n'
  s += sep + '\n'
  s += title
  s += sep + '\n'
  row_style = '{:^%d}' % (cw) * (num_col + 2) + '\n'
  mean = []
  for i, row in enumerate(conf_matrix):
    precision = ['{:.2f}'.format(div(r * 100.0, np.sum(conf_matrix[:, i]))) for r in row]
    mean.append(div(row[i] * 100.0, np.sum(conf_matrix[:, i])))
    s += row_style.format(*[names[i], *precision, '{:.2f}'.format(100 * np.sum(row) / total)])
  s += row_style.format(*['Sum Preds', *['{:.2f}'.format(v * 100 / total)
                        for v in np.sum(conf_matrix, axis=0)], '{:.2f}'.format(np.mean(mean))])
  s += sep + '\n'

  return s

#!<-----------------------------------------------------------------------------
#!< Point Cloud Segmentation
#!<-----------------------------------------------------------------------------


class PointCloudSegmentEvaluator(Evaluator):

  def __init__(self, num_classes, names):
    self.num_classes = num_classes
    assert self.num_classes == len(names)
    self.names = names
    self.gt_classes = [0] * self.num_classes
    self.positive_classes = [0] * self.num_classes
    self.true_positive_classes = [0] * self.num_classes
    self.confusion_matrix = np.zeros([self.num_classes, self.num_classes], dtype='int64')

  def reset(self):
    self.gt_classes = [0] * self.num_classes
    self.positive_classes = [0] * self.num_classes
    self.true_positive_classes = [0] * self.num_classes
    self.confusion_matrix = np.zeros([self.num_classes, self.num_classes], dtype='int64')

  def append(self, values):
    """values should be a confusion_matrix"""
    self.confusion_matrix += values

  def compute(self, logits, labels):
    """compute confusion matrix"""
    pred = logits.max(dim=1)[1]
    pred_valid = pred.detach().cpu().numpy()
    labels_valid = labels.detach().cpu().numpy()
    return confusion_matrix(labels_valid, pred_valid, labels=np.arange(0, self.num_classes, 1))

  def accumulate(self):
    iou_list = []
    for i, row in enumerate(self.confusion_matrix):
      iou_list.append(div(row[i] * 100.0, (np.sum(self.confusion_matrix[:, i]) + np.sum(row) - row[i])))
    reports = {'mIoU': np.mean(iou_list)}
    for i, iou in enumerate(iou_list):
      reports[self.names[i]] = iou
    return reports

#!<-----------------------------------------------------------------------------
#!< Common Semantic Segmentation Task
#!<-----------------------------------------------------------------------------


class SegmentationEvaluator(Evaluator):

  def __init__(self, num_classes):
    super().__init__()
    self.num_classes = num_classes
    self.confusion_matrix = np.zeros((self.num_classes,) * 2)

  def reset(self):
    self.confusion_matrix = np.zeros((self.num_classes,) * 2)

  def append(self, values):
    r"""values should be a confusion_matrix"""
    self.confusion_matrix += values

  def compute(self, preds, targets):
    r"""compute confusion matrix

    Args:
      preds: [N, H, W] (np.ndarry(int))
      targets: [N, H, W] (np.ndarry(int))

    """
    assert preds.shape == targets.shape
    # compute confusion matrix
    mask = (targets >= 0) & (targets < self.num_classes)
    label = self.num_classes * targets[mask].astype('int') + preds[mask]
    count = np.bincount(label, minlength=self.num_classes**2)
    confusion_matrix = count.reshape(self.num_classes, self.num_classes)
    return confusion_matrix

  def PA(self):
    acc = np.diag(self.confusion_matrix).sum() / self.confusion_matrix.sum()
    return acc

  def mPA(self):
    acc = np.diag(self.confusion_matrix) / self.confusion_matrix.sum(axis=1)
    acc = np.nanmean(acc)
    return acc

  def mIoU(self):
    mIoU = np.diag(self.confusion_matrix) / (
        np.sum(self.confusion_matrix, axis=1) + np.sum(self.confusion_matrix, axis=0) -
        np.diag(self.confusion_matrix))
    mIoU = np.nanmean(mIoU)
    return mIoU

  def fwIoU(self):
    freq = np.sum(self.confusion_matrix, axis=1) / \
        np.sum(self.confusion_matrix)
    iu = np.diag(self.confusion_matrix) / (
        np.sum(self.confusion_matrix, axis=1) + np.sum(self.confusion_matrix, axis=0) -
        np.diag(self.confusion_matrix))
    fwIoU = (freq[freq > 0] * iu[freq > 0]).sum()
    return fwIoU

  def accumulate(self):
    return {
        'PA': self.PA(),
        'mPA': self.mPA(),
        'mIoU': self.mIoU(),
        'fwIoU': self.fwIoU(),
    }


#!<-----------------------------------------------------------------------------
#!< Common Salient Detection
#!<-----------------------------------------------------------------------------

class SaliencyEvaluator(Evaluator):

  def __init__(self):
    super().__init__()
    self._root = None
    self._epsilon = 1e-4
    self._thre = 256
    self._precisions = [0] * self._thre
    self._recalls = [0] * self._thre
    self._beta = 0.3
    self.reset()

  def reset(self):
    self.metrics = []
    self._precisions = [0] * self._thre
    self._recalls = [0] * self._thre

  def append(self, values):
    r"""append values"""
    self.metrics.append(*values)

  def _compute_precision_and_recall(self, pred, target):
    r"""compute precision and recall. pred and target should be 3-d.
      and value should be in [0, 255] with uint8.

     => for th in range(self._thre):
     =>   ind_a = pred > th
     =>   ind_b = target > (self._thre / 2)
     =>   ab = (ind_a & ind_b).sum()
     =>   a_sum = ind_a.sum()
     =>   b_sum = ind_b.sum()
     =>   precisions.append(float(ab + self._epsilon) / float(a_sum + self._epsilon))  # nopep8
     =>   recalls.append(float(ab + self._epsilon) / float(b_sum + self._epsilon))  # nopep8

    """
    assert pred.dim() == target.dim() == 3, "Input should be 3-d."
    pred_rep = pred.reshape(1, -1).repeat(self._thre, 1)
    target_rep = target.reshape(1, -1).repeat(self._thre, 1)
    ind_a = pred_rep > torch.arange(0, self._thre).unsqueeze(dim=1).to(pred.device)  # nopep8
    ind_b = target_rep > (self._thre / 2)
    ab = (ind_a & ind_b).sum(dim=1)
    a_sum = ind_a.sum(dim=1)
    b_sum = ind_b.sum(dim=1)
    prec = ((ab + self._epsilon) / (a_sum + self._epsilon)).cpu().numpy()
    recall = ((ab + self._epsilon) / (b_sum + self._epsilon)).cpu().numpy()
    return recall, prec

  def _compute_mae(self, pred, target):
    assert pred.dim() == target.dim() == 3, "Input should be 3-d."
    return (pred - target).abs().mean()

  def _compute_ppa(self, pred, target):
    r"""reference by F3Net, the border/hole gains more attention
      target and pred should be [0, 1]
    """
    weight = torch.abs(F.avg_pool2d(target, kernel_size=31, stride=1, padding=15) - target)  # nopep8
    return (pred - weight).abs().mean()

  def compute(self, preds, targets):
    r"""MAE and F-Measure

    Note:
      MAE for Saliency Detection, the value of preds and targets should be in [0, 1]
      F-Score: from roc.

    """
    assert preds.dim() == targets.dim() == 4, "Input should have 4-dim."
    results = []
    for i in range(preds.size(0)):
      recall, prec = self._compute_precision_and_recall(preds[i] * 255, targets[i] * 255)  # nopep8
      result = {
          'recall': recall,
          'prec': prec,
          'mae': self._compute_mae(preds[i], targets[i]),
          'ppa': self._compute_ppa(preds[i], targets[i]),
      }
      results.append(result)
    return results

  def accumulate(self):
    r"""accumulate total results"""

    # accumulate every sample
    accum = {
        'mae': 0,
        'recall': [0] * self._thre,
        'prec': [0] * self._thre,
        'f-measure': [0] * self._thre,
        'ppa': 0,
    }

    for metric in self.metrics:
      accum['mae'] += metric['mae']
      accum['ppa'] += metric['ppa']
      for th in range(self._thre):
        accum['recall'][th] += metric['recall'][th]
        accum['prec'][th] += metric['prec'][th]

    # average
    accum['mae'] /= len(self)
    accum['ppa'] /= len(self)
    for th in range(self._thre):
      accum['recall'][th] /= len(self)
      accum['prec'][th] /= len(self)
      accum['f-measure'][th] = ((1 + self._beta) * accum['prec'][th] * accum['recall'][th]) / (self._beta * accum['prec'][th] + accum['recall'][th])  # nopep8

    # fetch max f-measure as threshold
    ind = np.argmax(accum['f-measure'])
    return {
        'mae': accum['mae'],
        'precision': accum['prec'][ind],
        'recall': accum['recall'][ind],
        'f-measure': accum['f-measure'][ind],
        'ppa': accum['ppa'],
    }

#!<-----------------------------------------------------------------------------
#!< Common Matting Task
#!<-----------------------------------------------------------------------------


class MattingEvaluator(Evaluator):
  r"""Image Matting Evaluator for 5 attribution.

    For alpha: SAD, MSE, GRAD, CONN
    For foreground: MSE

  """

  def __init__(self):
    super(MattingEvaluator, self).__init__()

  def norm(self, t: torch.Tensor):
    # return ((t - t.min())) / (t.max() - t.min()) * 255.0
    return t * 255.0

  def SAD(self, pred, target, mask=None):
    diff = (self.norm(pred) - self.norm(target)).abs() / 255.0
    if mask is not None:
      return (diff * mask).sum() / 1000.0
    else:
      return diff.sum() / 1000.0

  def MSE(self, pred, target, mask=None):
    diff = (self.norm(pred) - self.norm(target)).pow(2) / 255.0
    if mask is not None:
      return (diff * mask).sum() / mask.sum()
    else:
      return diff.mean()

  def GRAD(self, pred, target, mask=None):
    pd = self.norm(pred)[0, 0].cpu().numpy()
    gt = self.norm(target)[0, 0].cpu().numpy()
    pd_x = gaussian_filter(pd, sigma=1.4, order=[1, 0], output=np.float32)
    pd_y = gaussian_filter(pd, sigma=1.4, order=[0, 1], output=np.float32)
    gt_x = gaussian_filter(gt, sigma=1.4, order=[1, 0], output=np.float32)
    gt_y = gaussian_filter(gt, sigma=1.4, order=[0, 1], output=np.float32)
    pd_mag = np.sqrt(pd_x**2 + pd_y**2)
    gt_mag = np.sqrt(gt_x**2 + gt_y**2)
    error_map = np.square(pd_mag - gt_mag)
    return np.sum(error_map * mask[0, 0].cpu().numpy()) / 1000

  def CONN(self, pred, target, mask=None):
    return 0.0

  def compute(self, alpha, alpha_gt, fgr, fgr_gt, mask=None):
    r"""compute alpha matte and foreground error.

    Args:
      alpha: [N, 1, H, W] (0~1)
      alpha_gt: [N, 1, H, W] (0~1)
      alpha_mask: []
      fgr: [N, 3, H, W] (0~1)
      fgr_gt: [N, 3, H, W] (0~1)
      mask: [N, 1, H, W] (0/1) unknown area

    """
    assert alpha.shape == alpha_gt.shape
    assert fgr.shape == fgr_gt.shape

    return {
        'SAD': self.SAD(alpha, alpha_gt, mask),
        'MSE': self.MSE(alpha, alpha_gt, mask),
        'Grad': self.GRAD(alpha, alpha_gt, mask),
        'Conn': self.CONN(alpha, alpha_gt, mask),
        'FgrMSE': self.MSE(fgr, fgr_gt, mask * (alpha > 0)),
    }

  def accumulate(self):
    # accumulate average
    summary = {'SAD': 0, 'MSE': 0, 'Grad': 0, 'Conn': 0, 'FgrMSE': 0}  # nopep8
    count = 0.0
    for m in self.metrics:
      count += 1
      for k, v in m.items():
        if math.isnan(v):
          count -= 1
          break
        summary[k] += v
    for k, v in summary.items():
      summary[k] /= count
    return summary
