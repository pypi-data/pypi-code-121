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
"""reference from https://github.com/NVIDIA/flownet2-pytorch
"""
import re
import os
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt

TAG_CHAR = np.array([202021.25], np.float32)

#!<---------------------------------------------------------------------------
#!< *.pfm
#!<---------------------------------------------------------------------------


def pfm_from_bytes(content: bytes):
  """Load the file with the suffix '.pfm'.

  Args:
      content (bytes): Optical flow bytes got from files or other streams.

  Returns:
      ndarray: The loaded data
  """

  file = BytesIO(content)

  color = None
  width = None
  height = None
  scale = None
  endian = None

  header = file.readline().rstrip()
  if header == b'PF':
    color = True
  elif header == b'Pf':
    color = False
  else:
    raise Exception('Not a PFM file.')

  dim_match = re.match(rb'^(\d+)\s(\d+)\s$', file.readline())
  if dim_match:
    width, height = list(map(int, dim_match.groups()))
  else:
    raise Exception('Malformed PFM header.')

  scale = float(file.readline().rstrip())
  if scale < 0:  # little-endian
    endian = '<'
    scale = -scale
  else:
    endian = '>'  # big-endian

  data = np.frombuffer(file.read(), endian + 'f')
  shape = (height, width, 3) if color else (height, width)

  data = np.reshape(data, shape)
  data = np.flipud(data)
  return data[:, :, :-1]


def read_pfm(file: str):
  """Load the file with the suffix '.pfm'.

  This function is modified from
  https://lmb.informatik.uni-freiburg.de/resources/datasets/IO.py
  Copyright (c) 2011, LMB, University of Freiburg.

  Args:
      file (str): The file name will be loaded

  Returns:
      ndarray: The loaded data
  """
  file = open(file, 'rb')

  color = None
  width = None
  height = None
  scale = None
  endian = None

  header = file.readline().rstrip()
  if header.decode('ascii') == 'PF':
    color = True
  elif header.decode('ascii') == 'Pf':
    color = False
  else:
    raise Exception('Not a PFM file.')

  dim_match = re.match(r'^(\d+)\s(\d+)\s$', file.readline().decode('ascii'))
  if dim_match:
    width, height = list(map(int, dim_match.groups()))
  else:
    raise Exception('Malformed PFM header.')

  scale = float(file.readline().decode('ascii').rstrip())
  if scale < 0:  # little-endian
    endian = '<'
    scale = -scale
  else:
    endian = '>'  # big-endian

  data = np.fromfile(file, endian + 'f')
  shape = (height, width, 3) if color else (height, width)

  data = np.reshape(data, shape)
  data = np.flipud(data)
  return data[:, :, :-1]


#!<---------------------------------------------------------------------------
#!< *.flo
#!<---------------------------------------------------------------------------

def read_flow(fn):
  """ Read .flo file in Middlebury format"""
  # Code adapted from:
  # http://stackoverflow.com/questions/28013200/reading-middlebury-flow-files-with-python-bytes-array-numpy

  # WARNING: this will work on little-endian architectures (eg Intel x86) only!
  # print 'fn = %s'%(fn)
  with open(fn, 'rb') as f:
    magic = np.fromfile(f, np.float32, count=1)
    if 202021.25 != magic:
      print('Magic number incorrect. Invalid .flo file')
      return None
    else:
      w = np.fromfile(f, np.int32, count=1)
      h = np.fromfile(f, np.int32, count=1)
      # print 'Reading %d x %d flo file\n' % (w, h)
      data = np.fromfile(f, np.float32, count=2*int(w)*int(h))
      # Reshape data into 3D array (columns, rows, bands)
      # The reshape here is for visualization, the original code is (w,h,2)
      return np.resize(data, (int(h), int(w), 2))


def write_flow(filename, uv, v=None):
  """ Write optical flow to file.

  If v is None, uv is assumed to contain both u and v channels,
  stacked in depth.
  Original code by Deqing Sun, adapted from Daniel Scharstein.
  """
  nBands = 2

  if v is None:
    assert(uv.ndim == 3)
    assert(uv.shape[2] == 2)
    u = uv[:, :, 0]
    v = uv[:, :, 1]
  else:
    u = uv

  assert(u.shape == v.shape)
  height, width = u.shape
  f = open(filename, 'wb')
  # write the header
  f.write(TAG_CHAR)
  np.array(width).astype(np.int32).tofile(f)
  np.array(height).astype(np.int32).tofile(f)
  # arrange into matrix form
  tmp = np.zeros((height, width*nBands))
  tmp[:, np.arange(width)*2] = u
  tmp[:, np.arange(width)*2 + 1] = v
  tmp.astype(np.float32).tofile(f)
  f.close()


# ref: https://github.com/sampepose/flownet2-tf/
# blob/18f87081db44939414fc4a48834f9e0da3e69f4c/src/flowlib.py#L240
def visulize_flow_file(flow_filename, save_dir=None):
  flow_data = read_flow(flow_filename)
  img = flow2img(flow_data)
  # plt.imshow(img)
  # plt.show()
  if save_dir:
    idx = flow_filename.rfind("/") + 1
    plt.imsave(os.path.join(save_dir, "%s-vis.png" % flow_filename[idx:-4]), img)


def flow2img(flow_data):
  """
  convert optical flow into color image
  :param flow_data:
  :return: color image
  """
  # print(flow_data.shape)
  # print(type(flow_data))
  u = flow_data[:, :, 0]
  v = flow_data[:, :, 1]

  UNKNOW_FLOW_THRESHOLD = 1e7
  pr1 = abs(u) > UNKNOW_FLOW_THRESHOLD
  pr2 = abs(v) > UNKNOW_FLOW_THRESHOLD
  idx_unknown = (pr1 | pr2)
  u[idx_unknown] = v[idx_unknown] = 0

  # get max value in each direction
  maxu = -999.
  maxv = -999.
  minu = 999.
  minv = 999.
  maxu = max(maxu, np.max(u))
  maxv = max(maxv, np.max(v))
  minu = min(minu, np.min(u))
  minv = min(minv, np.min(v))

  rad = np.sqrt(u ** 2 + v ** 2)
  maxrad = max(-1, np.max(rad))
  u = u / maxrad + np.finfo(float).eps
  v = v / maxrad + np.finfo(float).eps

  img = compute_color(u, v)

  idx = np.repeat(idx_unknown[:, :, np.newaxis], 3, axis=2)
  img[idx] = 0

  return np.uint8(img)


def compute_color(u, v):
  """
  compute optical flow color map
  :param u: horizontal optical flow
  :param v: vertical optical flow
  :return:
  """

  height, width = u.shape
  img = np.zeros((height, width, 3))

  NAN_idx = np.isnan(u) | np.isnan(v)
  u[NAN_idx] = v[NAN_idx] = 0

  colorwheel = make_color_wheel()
  ncols = np.size(colorwheel, 0)

  rad = np.sqrt(u ** 2 + v ** 2)

  a = np.arctan2(-v, -u) / np.pi

  fk = (a + 1) / 2 * (ncols - 1) + 1

  k0 = np.floor(fk).astype(int)

  k1 = k0 + 1
  k1[k1 == ncols + 1] = 1
  f = fk - k0

  for i in range(0, np.size(colorwheel, 1)):
    tmp = colorwheel[:, i]
    col0 = tmp[k0 - 1] / 255
    col1 = tmp[k1 - 1] / 255
    col = (1 - f) * col0 + f * col1

    idx = rad <= 1
    col[idx] = 1 - rad[idx] * (1 - col[idx])
    notidx = np.logical_not(idx)

    col[notidx] *= 0.75
    img[:, :, i] = np.uint8(np.floor(255 * col * (1 - NAN_idx)))

  return img


def make_color_wheel():
  """
  Generate color wheel according Middlebury color code
  :return: Color wheel
  """
  RY = 15
  YG = 6
  GC = 4
  CB = 11
  BM = 13
  MR = 6

  ncols = RY + YG + GC + CB + BM + MR

  colorwheel = np.zeros([ncols, 3])

  col = 0

  # RY
  colorwheel[0:RY, 0] = 255
  colorwheel[0:RY, 1] = np.transpose(np.floor(255 * np.arange(0, RY) / RY))
  col += RY

  # YG
  colorwheel[col:col + YG, 0] = 255 - np.transpose(np.floor(255 * np.arange(0, YG) / YG))
  colorwheel[col:col + YG, 1] = 255
  col += YG

  # GC
  colorwheel[col:col + GC, 1] = 255
  colorwheel[col:col + GC, 2] = np.transpose(np.floor(255 * np.arange(0, GC) / GC))
  col += GC

  # CB
  colorwheel[col:col + CB, 1] = 255 - np.transpose(np.floor(255 * np.arange(0, CB) / CB))
  colorwheel[col:col + CB, 2] = 255
  col += CB

  # BM
  colorwheel[col:col + BM, 2] = 255
  colorwheel[col:col + BM, 0] = np.transpose(np.floor(255 * np.arange(0, BM) / BM))
  col += + BM

  # MR
  colorwheel[col:col + MR, 2] = 255 - np.transpose(np.floor(255 * np.arange(0, MR) / MR))
  colorwheel[col:col + MR, 0] = 255

  return colorwheel


# def flow2rgb(flow, color_wheel=None, unknown_thr=1e6):
#   """Convert flow map to RGB image.

#   Args:
#       flow (ndarray): Array of optical flow.
#       color_wheel (ndarray or None): Color wheel used to map flow field to
#           RGB colorspace. Default color wheel will be used if not specified.
#       unknown_thr (str): Values above this threshold will be marked as
#           unknown and thus ignored.

#   Returns:
#       ndarray: RGB image that can be visualized.
#   """
#   assert flow.ndim == 3 and flow.shape[-1] == 2
#   if color_wheel is None:
#     color_wheel = make_color_wheel()
#   assert color_wheel.ndim == 2 and color_wheel.shape[1] == 3
#   num_bins = color_wheel.shape[0]

#   dx = flow[:, :, 0].copy()
#   dy = flow[:, :, 1].copy()

#   ignore_inds = (
#       np.isnan(dx) | np.isnan(dy) | (np.abs(dx) > unknown_thr) |
#       (np.abs(dy) > unknown_thr))
#   dx[ignore_inds] = 0
#   dy[ignore_inds] = 0

#   rad = np.sqrt(dx**2 + dy**2)
#   if np.any(rad > np.finfo(float).eps):
#     max_rad = np.max(rad)
#     dx /= max_rad
#     dy /= max_rad

#   rad = np.sqrt(dx**2 + dy**2)
#   angle = np.arctan2(-dy, -dx) / np.pi

#   bin_real = (angle + 1) / 2 * (num_bins - 1)
#   bin_left = np.floor(bin_real).astype(int)
#   bin_right = (bin_left + 1) % num_bins
#   w = (bin_real - bin_left.astype(np.float32))[..., None]
#   flow_img = (1 -
#               w) * color_wheel[bin_left, :] + w * color_wheel[bin_right, :]
#   small_ind = rad <= 1
#   flow_img[small_ind] = 1 - rad[small_ind, None] * (1 - flow_img[small_ind])
#   flow_img[np.logical_not(small_ind)] *= 0.75

#   flow_img[ignore_inds, :] = 0

#   return flow_img


# def make_color_wheel(bins=None):
#   """Build a color wheel.

#   Args:
#       bins(list or tuple, optional): Specify the number of bins for each
#           color range, corresponding to six ranges: red -> yellow,
#           yellow -> green, green -> cyan, cyan -> blue, blue -> magenta,
#           magenta -> red. [15, 6, 4, 11, 13, 6] is used for default
#           (see Middlebury).

#   Returns:
#       ndarray: Color wheel of shape (total_bins, 3).
#   """
#   if bins is None:
#     bins = [15, 6, 4, 11, 13, 6]
#   assert len(bins) == 6

#   RY, YG, GC, CB, BM, MR = tuple(bins)

#   ry = [1, np.arange(RY) / RY, 0]
#   yg = [1 - np.arange(YG) / YG, 1, 0]
#   gc = [0, 1, np.arange(GC) / GC]
#   cb = [0, 1 - np.arange(CB) / CB, 1]
#   bm = [np.arange(BM) / BM, 0, 1]
#   mr = [1, 0, 1 - np.arange(MR) / MR]

#   num_bins = RY + YG + GC + CB + BM + MR

#   color_wheel = np.zeros((3, num_bins), dtype=np.float32)

#   col = 0
#   for i, color in enumerate([ry, yg, gc, cb, bm, mr]):
#     for j in range(3):
#       color_wheel[j, col:col + bins[i]] = color[j]
#     col += bins[i]

#   return color_wheel.T
