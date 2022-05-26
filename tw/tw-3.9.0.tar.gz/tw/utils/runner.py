# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
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
import socket
import shutil
import argparse
import random
from multiprocessing import Process

import numpy as np

import torch
from torch import multiprocessing as mp
from torch import distributed as dist
from torch.utils.collect_env import get_pretty_env_info

import tw


def seed_worker(worker_id):
  """assign different seed for each worker
  """
  worker_seed = torch.initial_seed() % 2 ** 32
  np.random.seed(worker_seed)
  random.seed(worker_seed)


def launch(parser: argparse.ArgumentParser, tasker, **kwargs):
  """launch a routine
  """

  # ---------------------------------------------
  #  USED BY CONTEXT
  # ---------------------------------------------
  parser.add_argument('--name', type=str, default='tw')
  parser.add_argument('--root', type=str, default=None, help="None for creating, otherwise specific root.")
  parser.add_argument('--device', type=str, default='cuda:0')
  parser.add_argument('--output_dir', type=str, default='_outputs', help="default output folder.")
  parser.add_argument('--pid', type=str, default=tw.timer.pid(), help="task pid.")

  # ---------------------------------------------
  #  USED BY DISTRIBUTED TRAINING
  # ---------------------------------------------
  parser.add_argument('--multiprocess', action='store_true', help="multiprocessing training.")
  parser.add_argument('--dist-rank', type=int, default=0, help="dist rank.")
  parser.add_argument('--dist-size', type=int, default=1, help="dist workspace size.")

  # generate config
  args, _ = parser.parse_known_args()

  # maybe result in deadlock
  env = os.environ.copy()
  env['OMP_NUM_THREADS'] = str(1)

  # multiprocess
  if args.multiprocess:
    num_gpus = torch.cuda.device_count()
    if num_gpus <= 0:
      raise EnvironmentError("Failed to find CUDA devices.")
    addr = 'localhost'
    port = str(random.choice(range(12300, 12400)))
    mp.spawn(dist_runner, nprocs=num_gpus, args=(args, tasker, addr, port), join=True)

  else:
    dist_runner(0, args, tasker)


def dist_runner(rank, config, tasker, addr='localhost', port=12300):
  """support distributed runner.
  """

  if config.multiprocess:
    # distributed step
    os.environ['MASTER_ADDR'] = addr
    os.environ['MASTER_PORT'] = port
    dist.init_process_group("nccl", rank=rank, world_size=torch.cuda.device_count())

    # assign config
    config.dist_rank = rank
    config.dist_size = torch.cuda.device_count()

    # make workspace
    if config.root is None:
      config.root = "%s/%s.%s" % (config.output_dir, config.name, config.pid)
    config.root += "/%s.p%d" % (socket.gethostname(), rank)
    tw.fs.mkdirs(config.root, False)

  else:
    # make workspace
    if config.root is None:
      config.root = "%s/%s.%s" % (config.output_dir, config.name, config.pid)
    tw.fs.mkdirs(config.root, False)

  # init logger
  tw.logger.init(name="%s.%s.log" % (config.name, config.pid), output_dir=config.root, stdout=(config.dist_rank == 0))
  tw.logger.info('Logger initialize successful.')
  tw.logger.sys('Running dir at %s, rank %d, size %d.' % (config.root, config.dist_rank, config.dist_size))
  tw.logger.sys(get_pretty_env_info())

  for k, v in config.__dict__.items():
    tw.logger.info('[CONFIG] {}: {}'.format(k, v))

  # ignore _outputs/_checkpoints/_datasets directory
  def _ignore(src, names):
    ignored_names = set()
    for name in names:
      if name in ['_datasets', '_outputs', '_checkpoints', '_models', '_deprecated', '_demo']:
        ignored_names.add(name)
    return ignored_names

  # copy current file to root
  # shutil.copytree('./', config.root + '/tw', symlinks=True, ignore=_ignore)

  # running runner
  tasker(config)()


def multitask(kernel, tasks, num_proc, *args):
  """split tasks(dict) into multiple process to running

  Args:
    kernel: kernel(tid, tasks[start: end], *args):
    tasks: a dictionary
    num_proc:

  """

  assert isinstance(tasks, list)
  total = len(tasks)
  part = int(total / num_proc)
  plist = []

  for tid in range(num_proc):
    start = part * tid
    end = min([part * (tid + 1), total])
    p = Process(target=kernel, args=(tid, tasks[start:end], *args))
    p.start()
    plist.append(p)
  for p in plist:
    p.join()


def log(keys, values, step, epoch, tag, **kwargs):
  """Display information during training in terms of interval.
  """

  if hasattr(tw.logger, tag):
    taglog = getattr(tw.logger, tag)
  else:
    taglog = tw.logger.info

  if 'iters_per_epoch' in kwargs:
    taglog(tw.logger.iters(step=step,
                           epoch=epoch,
                           iters_per_epoch=kwargs['iters_per_epoch'],
                           keys=keys,
                           values=values))
  else:
    taglog(tw.logger.iters(step=step,
                           epoch=epoch,
                           keys=keys,
                           values=values))

  if 'writer' in kwargs:
    kwargs['writer'].add_scalars(main_tag=tag,
                                 tag_scalar_dict=tw.tensorboard.make_dict(keys, values),
                                 global_step=step)


def reach(step, interval: int):
  if interval and interval > 0 and step % interval == 0:
    return True
  return False


class EmptyContext():

  def __init__(self):
    pass

  def __enter__(self):
    pass

  def __exit__(self, *args, **kwargs):
    pass
