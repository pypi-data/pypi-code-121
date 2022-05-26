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
"""Raw Image Reader and Writer

    .CR2, .CR2

"""
import os
import numpy as np
import rawpy
import exifread
import cv2


def read_meta_info(rawpath):
  with open(rawpath, 'rb') as f:
    tags = exifread.process_file(f)
    _, suffix = os.path.splitext(os.path.basename(rawpath))

    if suffix == '.dng':
      expo = eval(str(tags['Image ExposureTime']))
      iso = eval(str(tags['Image ISOSpeedRatings']))
    else:
      expo = eval(str(tags['EXIF ExposureTime']))
      iso = eval(str(tags['EXIF ISOSpeedRatings']))

  return iso, expo


def pack_raw_bayer(raw):
  """pack raw data by bayer filter (CFA) into 4 channels (RGBG)

  Args:
      raw ([raw file]): pyraw.read
  """
  im = raw.raw_image_visible.astype(np.float32)
  raw_pattern = raw.raw_pattern
  R = np.where(raw_pattern == 0)
  G1 = np.where(raw_pattern == 1)
  B = np.where(raw_pattern == 2)
  G2 = np.where(raw_pattern == 3)

  white_point = 16383
  img_shape = im.shape
  H = img_shape[0]
  W = img_shape[1]

  out = np.stack((im[R[0][0]:H:2, R[1][0]:W:2],  # RGBG
                  im[G1[0][0]:H:2, G1[1][0]:W:2],
                  im[B[0][0]:H:2, B[1][0]:W:2],
                  im[G2[0][0]:H:2, G2[1][0]:W:2]), axis=0).astype(np.float32)

  black_level = np.array(raw.black_level_per_channel)[:, None, None].astype(np.float32)

  # if max(raw.black_level_per_channel) != min(raw.black_level_per_channel):
  #     black_level = 2**round(np.log2(np.max(black_level)))
  # print(black_level)

  out = (out - black_level) / (white_point - black_level)
  out = np.clip(out, 0, 1)

  return out


def pack_raw_xtrans(raw):
  """pack raw data by xtrans filter (CFA) into 4 channels (RGBRB)

  Args:
      raw ([raw file]): pyraw.read
  """
  # pack X-Trans image to 9 channels
  im = raw.raw_image_visible.astype(np.float32)
  im = (im - 1024) / (16383 - 1024)  # subtract the black level
  im = np.clip(im, 0, 1)

  img_shape = im.shape
  H = (img_shape[0] // 6) * 6
  W = (img_shape[1] // 6) * 6

  out = np.zeros((9, H // 3, W // 3), dtype=np.float32)

  # 0 R
  out[0, 0::2, 0::2] = im[0:H:6, 0:W:6]
  out[0, 0::2, 1::2] = im[0:H:6, 4:W:6]
  out[0, 1::2, 0::2] = im[3:H:6, 1:W:6]
  out[0, 1::2, 1::2] = im[3:H:6, 3:W:6]

  # 1 G
  out[1, 0::2, 0::2] = im[0:H:6, 2:W:6]
  out[1, 0::2, 1::2] = im[0:H:6, 5:W:6]
  out[1, 1::2, 0::2] = im[3:H:6, 2:W:6]
  out[1, 1::2, 1::2] = im[3:H:6, 5:W:6]

  # 1 B
  out[2, 0::2, 0::2] = im[0:H:6, 1:W:6]
  out[2, 0::2, 1::2] = im[0:H:6, 3:W:6]
  out[2, 1::2, 0::2] = im[3:H:6, 0:W:6]
  out[2, 1::2, 1::2] = im[3:H:6, 4:W:6]

  # 4 R
  out[3, 0::2, 0::2] = im[1:H:6, 2:W:6]
  out[3, 0::2, 1::2] = im[2:H:6, 5:W:6]
  out[3, 1::2, 0::2] = im[5:H:6, 2:W:6]
  out[3, 1::2, 1::2] = im[4:H:6, 5:W:6]

  # 5 B
  out[4, 0::2, 0::2] = im[2:H:6, 2:W:6]
  out[4, 0::2, 1::2] = im[1:H:6, 5:W:6]
  out[4, 1::2, 0::2] = im[4:H:6, 2:W:6]
  out[4, 1::2, 1::2] = im[5:H:6, 5:W:6]

  out[5, :, :] = im[1:H:3, 0:W:3]
  out[6, :, :] = im[1:H:3, 1:W:3]
  out[7, :, :] = im[2:H:3, 0:W:3]
  out[8, :, :] = im[2:H:3, 1:W:3]

  return out


def read_raw(rawpath, cfa='bayer'):
  """read raw file with rawpath

  Args:
      rawpath ([str]): file path

  Returns:
      [np.ndarray]: [4, H, W] for bayer, [9, H, W] for xtrans
  """
  with rawpy.imread(rawpath) as raw:
    if cfa == 'bayer':
      input = pack_raw_bayer(raw)
    elif cfa == 'xtrans':
      input = pack_raw_xtrans(raw)
    else:
      raise NotImplementedError(cfa)
    input = np.maximum(np.minimum(input, 1.0), 0)
    input = np.ascontiguousarray(input)
  return input


# read_raw('/data/jk/tw/research/denoise/_datasets/denoising/ELD/CanonEOS70D/scene-1/IMG_6958.CR2')
