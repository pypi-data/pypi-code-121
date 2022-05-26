# Copyright 2020 The KaiJIN Authors. All Rights Reserved.
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
import os  # nopep8
import warnings  # nopep8
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # nopep8
warnings.simplefilter("ignore", UserWarning)  # nopep8
warnings.simplefilter("ignore", FutureWarning)  # nopep8

import re
import argparse
import sys
import glob
import shutil
import pickle
import subprocess
import psutil
import xml.etree.ElementTree as ET
import time

import numpy as np

import torch
import torchvision
import tw

from tensorboard.backend.event_processing import event_accumulator

import matplotlib.pyplot as plt
import matplotlib.pylab as plb


class TFEventAccumulator():
  def __init__(self, root):
    # root
    if not os.path.exists(root):
      raise FileExistsError(root)
    self._root = root

    # store all info
    self._kv = {
        'images': [],
        'audio': [],
        'histograms': [],
        'scalars': {},
        'distributions': [],
        'tensors': [],
        'graph': False,
        'meta_graph': False,
        'run_metadata': []
    }

  def dump(self):
    with open('%s.pkl' % self._root, 'wb') as fw:
      pickle.dump(self._kv, fw)

  def load_scalars(self):
    # parse all info at root dir
    files = glob.glob('%s/*/events.out.tfevents.*' % self._root)
    for path in files:
      tag = path.split('/')[-2]
      ea = event_accumulator.EventAccumulator(path)
      ea.Reload()
      for key in ea.Tags()['scalars']:
        vals = [(int(scalar.step), scalar.value) for scalar in ea.Scalars(key)]
        self._kv['scalars'][tag + '/' + key] = [v for v in zip(*vals)]

  @property
  def epoch(self):
    models = glob.glob('%s/model.epoch-*' % self._root)
    epoches = [int(re.findall('model.epoch-(.*?).step', model)[0]) for model in models]
    return max(epoches) if len(epoches) else 0

  @property
  def kv(self):
    return self._kv

  @property
  def root(self):
    return self._root


def count(root):
  training_dirs = sorted(glob.glob('%s/**' % root, recursive=True))
  paths = {}

  for folder in training_dirs:
    if os.path.isdir(folder):
      event = TFEventAccumulator(folder)
      key = event.root.replace(root, '').split('/')[0]
      # skip out root node
      if not os.path.exists(key):
        continue
      # create a node with default epoch 0
      if key not in paths:
        paths[key] = 0
      # update to maximum epoch for sub-folders
      if event.epoch > paths[key]:
        paths[key] = event.epoch

  for path, epoch in paths.items():
    print(f'MODEL: {path}, EPOCH: {epoch}')

  return paths


def clear(root):
  # collect paths and epoch
  paths = count(root)
  for path, epoch in paths.items():
    if epoch == 0:
      shutil.rmtree(path)
      print('REMOVE EMPTY FOLDER:', path)


def dump(root):
  training_dirs = glob.glob('%s/*' % root)
  for folder in training_dirs:
    if os.path.isdir(folder):
      event = TFEventAccumulator(folder)
      if event.epoch != 0:
        print('MODEL:', event.root, 'EPOCH:', event.epoch)
        event.load_scalars()
        event.dump()


def compare(root):
  training_dirs = sorted(glob.glob('%s/*' % root))

  # * accumulate information to events
  events, labels = [], []
  for folder in training_dirs:
    if not os.path.isdir(folder):
      continue
    event = TFEventAccumulator(folder)
    print('MODEL:', event.root, 'EPOCH:', event.epoch)
    event.load_scalars()
    events.append(event)
    labels.append(os.path.basename(folder))

  # * filter time and throughtput items
  kvs = {}
  for event, label in zip(events, labels):
    for k, v in event.kv['scalars'].items():
      if '_time' in k or '_throughtput' in k or '_lr' in k:
        continue
      if k not in kvs:
        kvs[k] = {}

      # * sorted v(iters, values)
      iter_and_values = sorted([a for a in zip(*v)])
      v = [[], []]
      for it, val in iter_and_values:
        v[0].append(it)
        v[1].append(val)
      kvs[k][label] = v
  if not kvs:
    return

  # * select common
  rows, cols = len(kvs), 1
  plt.figure(figsize=(16, 4 * rows))
  plb.gcf().suptitle(labels, fontsize=14)

  # * plot each key
  for idx, (k, v) in enumerate(kvs.items()):

    ax = plt.subplot(rows, cols, idx + 1)
    print('[INFO] Render {}:'.format(k))

    # * sk=label, sv=value of key
    for sk, sv in v.items():
      print('[INFO]  => process {}'.format(sk))
      ax.plot(sv[0], sv[1], label=sk, alpha=0.7)

    ax.grid()
    ax.legend(list(v.keys()), fontsize=5)
    ax.set_title(k)

  plt.savefig(root + '/output.png', dpi=300)


def plot(root):
  training_dirs = [*sorted(glob.glob('%s/*' % root)), root]
  for folder in training_dirs:
    if not os.path.isdir(folder):
      continue
    event = TFEventAccumulator(folder)
    print('MODEL:', event.root, 'EPOCH:', event.epoch)
    if event.epoch == 0:
      continue
    event.load_scalars()

    # * filter time and throughtput items
    kvs = {}
    for k, v in event.kv['scalars'].items():
      if '_time' in k or '_throughtput' in k or '_lr' in k:
        continue
      kvs[k] = v
    if not kvs:
      return

    # plot size
    rows, cols = len(kvs), 1
    plt.figure(figsize=(16, 4 * rows))
    plb.gcf().suptitle(event.root, fontsize=14)

    # * plot each key
    for idx, (k, v) in enumerate(kvs.items()):
      ax = plt.subplot(rows, cols, idx + 1)
      print(' [INFO] Render {}, max: {} in epoch: {}, min: {} in epoch: {}'.format(
        k, np.max(v[1]), v[0][np.argmax(v[1])], np.min(v[1]), v[0][np.argmin(v[1])]))
      if 'train' in k:
        ax.plot(v[0][100:], v[1][100:], label=k)
      else:
        ax.plot(v[0], v[1], label=k)
      ax.grid()
      ax.legend()
      ax.set_title(k)

    plt.savefig('%s.png' % event.root, dpi=300)


if __name__ == "__main__":

  # parser
  parser = argparse.ArgumentParser()

  parser.add_argument('--task', type=str, choices=['plot', 'count', 'clear', 'dump', 'compare'])
  parser.add_argument('--src', type=str, default=None)
  parser.add_argument('--dst', type=str, default=None)
  args, _ = parser.parse_known_args()

  if args.task == 'count':
    count(args.src)

  elif args.task == 'clear':
    clear(args.src)

  elif args.task == 'dump':
    dump(args.src)

  elif args.task == 'plot':
    plot(args.src)

  elif args.task == 'compare':
    compare(args.src)
