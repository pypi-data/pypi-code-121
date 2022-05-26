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
"""Optical flow evaluator by using EPE metric
"""
import torch
import numpy as np
from typing import Dict, Sequence, Union
from .base import Evaluator


def end_point_error_map(flow_pred: np.ndarray,
                        flow_gt: np.ndarray) -> np.ndarray:
  """Calculate end point error map.

  Args:
      flow_pred (ndarray): The predicted optical flow with the
          shape (H, W, 2).
      flow_gt (ndarray): The ground truth of optical flow with the shape
          (H, W, 2).

  Returns:
      ndarray: End point error map with the shape (H , W).
  """
  return np.sqrt(np.sum((flow_pred - flow_gt)**2, axis=-1))


def end_point_error(flow_pred: Sequence[np.ndarray],
                    flow_gt: Sequence[np.ndarray],
                    valid_gt: Sequence[np.ndarray]) -> float:
  """Calculate end point errors between prediction and ground truth.

  Args:
      flow_pred (list): output list of flow map from flow_estimator
          shape(H, W, 2).
      flow_gt (list): ground truth list of flow map shape(H, W, 2).
      valid_gt (list): the list of valid mask for ground truth with the
          shape (H, W).

  Returns:
      float: end point error for output.
  """
  epe_list = []
  assert len(flow_pred) == len(flow_gt)
  for _flow_pred, _flow_gt, _valid_gt in zip(flow_pred, flow_gt, valid_gt):
    epe_map = end_point_error_map(_flow_pred, _flow_gt)
    val = _valid_gt.reshape(-1) >= 0.5
    epe_list.append(epe_map.reshape(-1)[val])

  epe_all = np.concatenate(epe_list)
  epe = np.mean(epe_all)

  return epe


def optical_flow_outliers(flow_pred: Sequence[np.ndarray],
                          flow_gt: Sequence[np.ndarray],
                          valid_gt: Sequence[np.ndarray]) -> float:
  """Calculate percentage of optical flow outliers for KITTI dataset.

  Args:
      flow_pred (list): output list of flow map from flow_estimator
          shape(H, W, 2).
      flow_gt (list): ground truth list of flow map shape(H, W, 2).
      valid_gt (list): the list of valid mask for ground truth with the
          shape (H, W).

  Returns:
      float: optical flow outliers for output.
  """
  out_list = []
  assert len(flow_pred) == len(flow_gt) == len(valid_gt)
  for _flow_pred, _flow_gt, _valid_gt in zip(flow_pred, flow_gt, valid_gt):
    epe_map = end_point_error_map(_flow_pred, _flow_gt)
    epe = epe_map.reshape(-1)
    mag_map = np.sqrt(np.sum(_flow_gt**2, axis=-1))
    mag = mag_map.reshape(-1) + 1e-6
    val = _valid_gt.reshape(-1) >= 0.5
    # 3.0 and 0.05 is tooken from KITTI devkit
    # Inliers are defined as EPE < 3 pixels or < 5%
    out = ((epe > 3.0) & ((epe / mag) > 0.05)).astype(float)
    out_list.append(out[val])
  out_list = np.concatenate(out_list)
  fl = 100 * np.mean(out_list)

  return fl


def eval_metrics(results: Sequence[np.ndarray],
                 flow_gt: Sequence[np.ndarray],
                 valid_gt: Sequence[np.ndarray],
                 metrics: Union[Sequence[str], str] = ['EPE']) -> Dict[str, np.ndarray]:
  """Calculate evaluation metrics.

  Args:
      results (list): list of predictedflow maps.
      flow_gt (list): list of ground truth flow maps
      metrics (list, str): metrics to be evaluated.
          Defaults to ['EPE'], end-point error.

  Returns:
      dict: metrics and their values.
  """
  if isinstance(metrics, str):
    metrics = [metrics]
  allowed_metrics = ['EPE', 'Fl']
  if not set(metrics).issubset(set(allowed_metrics)):
    raise KeyError('metrics {} is not supported'.format(metrics))
  ret_metrics = dict()
  if 'EPE' in metrics:
    ret_metrics['EPE'] = end_point_error(results, flow_gt, valid_gt)
  if 'Fl' in metrics:
    ret_metrics['Fl'] = optical_flow_outliers(results, flow_gt, valid_gt)
  return ret_metrics


class OpticalFlowEvaluator(Evaluator):
  def __init__(self, root=None):
    super(OpticalFlowEvaluator, self).__init__(root=root)

  def compute(self, inputs, targets, valids=None):
    """compute optical flow

    Args:
        inputs (torch.Tensor): [N, 2, H, W]
        targets (torch.Tensor): [N, 2, H, W]
        valids (torch.Tensor, optional): [H, W]

    Returns:
        (inputs, targets, valids):
    """
    assert inputs.size(0) == targets.size(0) == 1

    if valids is None:
      valids = torch.ones(inputs.shape[-2:]).float().numpy() # [H, W]

    inputs = inputs[0].permute(1, 2, 0).cpu().numpy()
    targets = targets[0].permute(1, 2, 0).cpu().numpy()
    results = eval_metrics([inputs,], [targets,], [valids,], metrics=['EPE', 'Fl'])

    return results['EPE'], results['Fl']

  def accumulate(self):
    """unzip each tuple. compute mae and rmse.
      metric layout: [preds, targets, (paths)]
    """
    err_epe, err_fl = [], []
    for batch in self.metrics:
      err_epe.append(batch[0])
      err_fl.append(batch[1])

    return {'EPE': np.mean(err_epe), 'Fl': np.mean(err_fl)}
