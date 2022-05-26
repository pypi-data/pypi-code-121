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
import shutil
import pickle
import torch


def dump(content, path, overwrite=False, backend='torch'):
  if not overwrite and os.path.exists(path):
    raise FileExistsError(path)
  if backend == 'torch':
    return torch.save(content, path)
  elif backend == 'pickle':
    with open(path, 'wb') as fw:
      return pickle.dump(content, fw)
  raise ValueError(backend)


def load(path, backend='torch'):
  if not os.path.exists(path):
    raise FileNotFoundError(path)
  if backend == 'torch':
    return torch.load(path, map_location='cpu')
  elif backend == 'pickle':
    with open(path, 'rb') as fp:
      return pickle.load(fp)
  raise ValueError(backend)


def copy(src, dst):
  return shutil.copy(src, dst)


def copytree(src, dst):
  return shutil.copytree(src, dst)


def _raise_path_not_exist_single(str_path):
  if not os.path.exists(str_path):
    raise FileNotFoundError(str_path)


def raise_path_not_exist(path):
  r"""r.t."""
  if isinstance(path, str):
    _raise_path_not_exist_single(path)
  elif isinstance(path, list):
    for _p in path:
      _raise_path_not_exist_single(_p)
  elif isinstance(path, dict):
    for _k, _v in path.items():
      _raise_path_not_exist_single(_v)
  else:
    raise NotImplementedError(type(path))


def exisit(path):
  return True if os.path.exists(path) else False


def root(path):
  return os.path.dirname(path)


def mkdir(path, raise_path_exits=False):
  r"""Path if mkdir or path has existed"""
  if not os.path.exists(path):
    os.mkdir(path)
  else:
    if raise_path_exits:
      raise ValueError('Path %s has existed.' % path)
  return path


def listdir(root, full_path=True):
  r"""Return a list with full path under root dir"""
  lists = os.listdir(root)
  for idx, path in enumerate(lists):
    if full_path:
      lists[idx] = os.path.join(root, path)
  return lists


def mkdirs(path, raise_path_exits=False):
  r"""Create a dir leaf"""
  if not os.path.exists(path):
    os.makedirs(path)
  else:
    if raise_path_exits:
      raise ValueError('Path %s has exitsted.' % path)
  return path


def join(*args):
  r"""Join multiple path - join('c:', 'pp', 'c.txt') -> 'c:\pp\c.txt'"""
  assert len(args) >= 2
  ret_arg = args[0]
  for arg in args[1:]:
    ret_arg = os.path.join(ret_arg, arg)
  return ret_arg


def join_name(dst, src):
  r"""Example: dst='/kj/tensorflow/', src='/kj/gate/test.txt'
    ret: '/kj/tensorflow/text.txt'

  """
  return os.path.join(dst, filename(src))


def traverse(root: str, files: list, pattern=''):
  r"""Recursively return files,

  Args:
    root: the folder path should be traversed.
    files: pass in a list
    pattern: cater the condition

  """
  for subfolder in os.listdir(root):
    path = os.path.join(root, subfolder)
    if os.path.isdir(path):
      traverse(path, files)
    else:
      if pattern in path:
        files.append(path)


def pwd():
  return os.getcwd()


def dirname(path):
  return os.path.dirname(path)


def filename(abspath):
  """Input: /p1/p2/f1.ext -> Return: f1.ext"""
  if not isinstance(abspath, str):
    return os.path.split(str(abspath, encoding="utf-8"))[1]
  return os.path.split(abspath)[1]
