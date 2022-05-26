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
"""Drawer based on OpenCV.

  - bounding box
  - lane
  - keypoints
  - heatmap
  - ...

  Each drawer could support two kind of input: numpy and torch.

  - numpy format use [H, W, C] format

"""
import numpy as np
import cv2
import pylab
import matplotlib.pyplot as plt


def boundingbox(image, bboxes, labels=None, conf=0.0,
                bbox_thick=2,
                font_type=cv2.FONT_HERSHEY_SIMPLEX,
                font_thick=1,
                font_scale=0.4,
                **kwargs):
  """Render bounding box to image

  Args:
      image ([np.ndarray]): [H, W, C] uint8
      bboxes ([np.ndarray]): [N, 5(x1, y1, x2, y2, score(optional))] float
      labels (list[]]): [N, ]

  """
  assert isinstance(image, np.ndarray) and image.ndim == 3
  render = image.copy()

  # select score
  if bboxes.shape[1] == 5:
    scores = bboxes[:, 4]
  else:
    scores = None

  for i, bbox in enumerate(bboxes):

    # skip low confidence
    if scores is not None:
      if scores[i] < conf:
        continue

    # skip ignore labels

    # render bbox
    x1, y1, x2, y2 = bbox[:4]
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    cv2.rectangle(img=render,
                  pt1=(x1, y1),
                  pt2=(x2, y2),
                  color=(52, 213, 235),
                  thickness=bbox_thick)

    # render label
    if labels is not None:
      label = labels[i]
      if scores is not None:
        caption = '{}:{:.2f}'.format(label, scores[i])
      else:
        caption = '{}'.format(label)
      # get the width and height of the text box
      tw, th = cv2.getTextSize(text=caption,
                               fontFace=font_type,
                               fontScale=font_scale,
                               thickness=font_thick)[0]
      cv2.rectangle(render, (x1, y1), (x1 + tw + 2, y1 - th - 6), (52, 213, 235), cv2.FILLED)
      cv2.putText(render, caption, (x1, y1 - 4),
                  fontFace=font_type,
                  fontScale=font_scale,
                  color=[255, 255, 255],
                  thickness=font_thick)

  return render


def keypoints(image, points, **kwargs):
  """Draw points on image

  Args:
      image ([np.ndarray]): [H, W, C] uint8
      points ([np.ndarray]): [N, 2(x, y)] float

  """
  assert isinstance(image, np.ndarray) and image.ndim in [3, 2]
  assert isinstance(points, np.ndarray) and points.ndim == 2

  render = image.copy()
  radius = 5 if 'radius' not in kwargs else kwargs['radius']
  color = (0, 255, 0) if 'color' not in kwargs else kwargs['color']
  labels = None if 'labels' not in kwargs else kwargs['labels']
  scores = None if 'scores' not in kwargs else kwargs['scores']

  font_type = cv2.FONT_HERSHEY_SIMPLEX
  font_thick = 1
  font_scale = 0.4

  for i, (x, y) in enumerate(points):
    cv2.circle(render, (int(x), int(y)), radius=radius, color=color, thickness=cv2.FILLED)

    # render label
    if labels is not None:
      label = labels[i]
      if scores is not None:
        caption = '{}:{:.2f}'.format(label, scores[i])
      else:
        caption = '{}'.format(label)
      # get the width and height of the text box
      tw, th = cv2.getTextSize(text=caption, fontFace=font_type, fontScale=font_scale, thickness=font_thick)[0] # nopep8
      cv2.putText(render, caption, (int(x), int(y) - 4), fontFace=font_type, fontScale=font_scale, color=[255, 255, 255], thickness=font_thick) # nopep8

  return render


def binary_class_analysis(preds, label, legends=None, grid=100, dst=None):
  """binary class figure.

    1) ROC curve [AUC]
    2) P-R curve [F-score]

  Args:
      preds ([np.ndarray]): [description]
      label ([np.ndarray]): 1 for true, 0 for false
      legends (list[str]): e.g. ['line1', 'line2'] ,
      grid (int): threshold grid.
  """
  # check
  for p in preds:
    assert len(p) == len(label), "every pred result should be equal to label length."
  for v in label:
    assert v in [0, 1], "label value should be 0 or 1."
  assert grid > 0
  if dst is None:
    dst = 'binary_class_analysis.png'

  # compute TP, TN, FP, FN
  results = []
  for idx, pred in enumerate(preds):
    result = []
    for threshold in range(grid):
      threshold = threshold / grid
      tp, tn, fp, fn, pos, neg = 0, 0, 0, 0, 0, 0
      for i in range(len(pred)):
        if pred[i] >= threshold and label[i] == 1:
          tp += 1
          pos += 1
        elif pred[i] >= threshold and label[i] == 0:
          fp += 1
          neg += 1
        elif pred[i] < threshold and label[i] == 1:
          fn += 1
          pos += 1
        elif pred[i] < threshold and label[i] == 0:
          tn += 1
          neg += 1
        else:
          raise ValueError(label[i], pred[i])

      tpr = tp / (tp + fn)
      fpr = fp / (fp + tn)
      acc = (tp + tn) / (pos + neg)
      precision = 0 if tp + fp == 0 else tp / (tp + fp)
      recall = 0 if tp + fn == 0 else tp / (tp + fn)
      assert neg + pos == len(pred) == len(label)

      result.append((threshold, tp, tn, fp, fn, tpr, fpr, acc, precision, recall, pos, neg))
    results.append(sorted(result))

  plt.figure(figsize=(10, 5))

  # ROC
  plt.subplot(1, 2, 1)
  plt.title('ROC curve')
  for i, result in enumerate(results):
    xs = [res[6] for res in result]
    ys = [res[5] for res in result]
    legend = None if legends is None else legends[i]
    plt.plot(xs, ys, label=legend)
  plt.grid()
  plt.plot([0, 1], [0, 1], ':r')
  plt.xlabel('True Positive Rate')
  plt.ylabel('False Positive Rate')
  plt.legend()
  plt.xlim([0, 1])
  plt.ylim([0, 1])

  # P-R
  plt.subplot(1, 2, 2)
  plt.title('P-R curve')
  for i, result in enumerate(results):
    xs = [res[9] for res in result]
    ys = [res[8] for res in result]
    legend = None if legends is None else legends[i]
    plt.plot(xs, ys, label=legend)
  plt.grid()
  plt.plot([0, 1], [1, 0], ':r')
  plt.xlabel('Recall')
  plt.ylabel('Precision')
  plt.legend()
  plt.xlim([0, 1])
  plt.ylim([0, 1])

  plt.tight_layout()
  plt.savefig(dst)
  plt.close()

  return results
