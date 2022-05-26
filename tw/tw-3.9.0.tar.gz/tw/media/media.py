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
r"""Stream Media
"""
import os
import cv2
import tqdm
import functools
import subprocess
import numpy as np

import torch

from tw.utils.parser import parse_from_text
from tw.utils.logger import logger


#!<-----------------------------------------------------------------------------
#!< file
#!<-----------------------------------------------------------------------------

def is_image(filepath: str):
  if not os.path.exists(filepath):
    return False
  if not os.path.isfile(filepath):
    return False
  for ext in ['png', 'jpg', 'jpeg', 'bmp', 'cr2', 'nef', 'arw']:
    if filepath.lower().endswith(ext):
      return True
  return False


def is_video(filepath: str):
  if not os.path.exists(filepath):
    return False
  if not os.path.isfile(filepath):
    return False
  for ext in ['mp4', 'avi', '.qt', '.bin']:
    if filepath.lower().endswith(ext):
      return True
  return False


def collect(path: str, salience=False):
  r"""Collect all images/videos:
    1. from .txt file
    2. traverse all folder

  Args:
    path: a txt filepath or a folder path

  Returns:
    list (image_files, video_files)

  """
  image_files = []
  video_files = []

  if not os.path.exists(path):
    raise FileNotFoundError(path)

  if path.endswith('.txt') and os.path.isfile(path):
    res, _ = parse_from_text(path, [str, ], [True, ])
    for lq in res[0]:
      if is_image(lq):
        image_files.append(lq)
      elif is_video(lq):
        video_files.append(lq)

  elif os.path.isfile(path):
    if is_image(path):
      image_files.append(path)
    elif is_video(path):
      video_files.append(path)

  elif os.path.isdir(path):
    for root, _, fnames in os.walk(path):
      for name in fnames:
        filepath = os.path.join(root, name)
        if is_video(filepath):
          video_files.append(filepath)
        elif is_image(filepath):
          image_files.append(filepath)

  else:
    raise "Unknown input path attribution %s." % path

  if not salience:
    logger.info('Total loading %d image.' % len(image_files))
    logger.info('Total loading %d video.' % len(video_files))

  return image_files, video_files


#!<-----------------------------------------------------------------------------
#!< video <-> image
#!<-----------------------------------------------------------------------------

def video_to_image(filepath, transform=None):
  r"""Video to images

  Args:
    filepath: file path
    transform(optional): transform for every image

  """
  if not os.path.exists(filepath):
    raise FileNotFoundError(filepath)

  def _to_images(video_path, transform=None):
    vidcap = cv2.VideoCapture(video_path)
    total = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    success, frame = vidcap.read()

    img_root = os.path.join(os.path.splitext(video_path)[0])
    if not os.path.exists(img_root):
      os.makedirs(img_root)

    count = 0
    for _ in tqdm.tqdm(range(total)):
      img_path = os.path.join(img_root, '%08d.png' % count)
      if transform:
        frame = transform(frame)
      cv2.imwrite(img_path, frame)
      success, frame = vidcap.read()
      count += 1

  if os.path.isfile(filepath):
    _to_images(filepath, transform)
  else:
    for name in tqdm.tqdm(sorted(os.listdir(filepath))):
      video_path = os.path.join(filepath, name)
      if is_video(video_path):
        _to_images(video_path, transform)


def image_to_video(image_folder, video_path, fps=30):
  r"""Image to video
  """
  fourcc = cv2.VideoWriter_fourcc(*'XVID')
  for idx, name in enumerate(sorted(os.listdir(image_folder))):
    img_path = os.path.join(image_folder, name)
    assert os.path.exists(img_path)
    frame = cv2.imread(img_path)
    if idx == 0:
      h, w, c = frame.shape
      out = cv2.VideoWriter(video_path, fourcc, fps, (w, h))
    else:
      nh, nw, nc = frame.shape
      assert nh == h and nw == w and nc == c
    out.write(frame)
  out.release()


#!<-----------------------------------------------------------------------------
#!< video transcode
#!<-----------------------------------------------------------------------------

def video_transcode(video_path: str, codec='libx264', crf=24, output_path=None):
  r"""Video transcode (ffmpeg)
  """
  if output_path:
    dst_path = output_path
  else:
    dst_path = '%s.%s.%d.mp4' % (os.path.splitext(video_path)[0], codec, crf)

  # -vsync parameter
  # Video sync method. For compatibility reasons old values can be specified
  # as numbers. Newly added values will have to be specified as strings
  # always.

  # 0, passthrough
  # Each frame is passed with its timestamp from the demuxer to the muxer.

  # 1, cfr
  # Frames will be duplicated and dropped to achieve exactly the requested constant frame rate.

  # 2, vfr
  # Frames are passed through with their timestamp or dropped so as to prevent 2 frames from having the same timestamp.

  # drop
  # As passthrough but destroys all timestamps, making the muxer generate fresh timestamps based on frame-rate.

  # -1, auto
  # Chooses between 1 and 2 depending on muxer capabilities. This is the default method.

  # The presence of -an disables audio stream selection for video.

  cmd = 'ffmpeg -y -i {} -threads 16 -vsync 0 -c:v {} -pix_fmt yuvj420p -an -crf {} {}'.format(video_path, codec, crf, dst_path)  # nopep8
  logger.info(cmd)
  return subprocess.call(cmd, shell=True)


def video_resize(video_path: str, target_h, target_w, output_path):
  cmd = 'ffmpeg -y -i {} -vsync 0 -threads 16 -vf scale={}:{} -pix_fmt yuvj420p -strict -2 {}'.format(
      video_path, target_w, target_h, output_path)
  logger.info(cmd)
  return subprocess.call(cmd, shell=True)


class YuvReader():
  def __init__(self, path: str, height: int, width: int, separate=False):
    assert os.path.exists(path)
    self.size = height * width + height * width // 2
    self.handle = open(path, 'rb')
    self.count = os.path.getsize(path) // self.size

    assert height > 0 and height % 2 == 0
    assert width > 0 and width % 2 == 0
    self.height = height
    self.width = width
    self.separate = separate

    # preload first
    h, w = height, width
    s = width * height
    uPlanePos = s
    vPlanePos = s + (width // 2) * (height // 2)

    self.frames = []
    for i in range(self.count):
      arr = np.array([i for i in self.handle.read(self.size)]).astype('uint8')
      y = arr[:uPlanePos]
      u = arr[uPlanePos: vPlanePos]
      v = arr[vPlanePos:]
      y = np.reshape(y, [h, w])
      u = u.reshape(h // 2, w // 2)
      v = v.reshape(h // 2, w // 2)
      if self.separate:
        self.frames.append([y, u, v])
      else:
        u = cv2.resize(u, dsize=(w, h))
        v = cv2.resize(v, dsize=(w, h))
        yuv = np.stack([y, u, v], axis=2)
        self.frames.append(yuv)

  def __len__(self):
    return len(self.frames)

  def __getitem__(self, idx):
    return self.frames[idx]

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.handle.close()


class YuvWriter():
  def __init__(self, path: str, height: int, width: int):
    assert height > 0 and height % 2 == 0
    assert width > 0 and width % 2 == 0
    self.height = height
    self.width = width
    self.handle = open(path, 'wb')

  def __len__(self):
    return len(self.frames)

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.handle.close()

  def write(self, y: np.ndarray, u: np.ndarray, v: np.ndarray):
    assert y.shape[0] == self.height and y.shape[1] == self.width
    assert u.shape[0] == self.height // 2 and u.shape[1] == self.width // 2
    assert v.shape[0] == self.height // 2 and v.shape[1] == self.width // 2

    self.handle.write(y.astype('uint8').tobytes())
    self.handle.write(u.astype('uint8').tobytes())
    self.handle.write(v.astype('uint8').tobytes())


class VideoReader():

  def __init__(self, path: str, to_rgb=False, to_tensor=False):
    self.cap = cv2.VideoCapture(path)
    self.frame = None
    self.to_rgb = to_rgb
    self.to_tensor = to_tensor

    if not self.cap.isOpened():
      logger.warn('Failed to open {}'.format(path))
      self.valid = False
      self.fps = -1
      self.width = -1
      self.height = -1
      self.count = 0

    else:
      self.valid = True
      self.fps = self.cap.get(cv2.CAP_PROP_FPS)
      self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
      self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
      self.count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

  def __len__(self):
    return int(self.count)

  def __getitem__(self, idx):
    # return a clip
    if isinstance(idx, slice):
      return [self[i] for i in range(*idx.indices(len(self)))]

    if self.cap.get(cv2.CAP_PROP_POS_FRAMES) != idx:
      self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)

    ret, img = self.cap.read()
    if not ret:
      raise IndexError

    if self.to_rgb:
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if self.to_tensor:
      img = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0

    return img

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.cap.release()


class VideoWriter():

  def __init__(self, path: str, width: int, height: int, fps: float):
    self.cap = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (int(width), int(height)))

  def write_tensor(self, tensor, is_rgb=True):
    r"""Assume tensor is [0~1] [N, C, H, W] float32 format.
    """
    frames = tensor.mul(255).byte().cpu().permute(0, 2, 3, 1).numpy()
    for i in range(frames.shape[0]):
      if is_rgb:
        self.cap.write(cv2.cvtColor(frames[i], cv2.COLOR_RGB2BGR))
      else:
        self.cap.write(frames[i])

  def write(self, array: np.array):
    if array.ndim == 3:
      self.cap.write(array)
    elif array.ndim == 4:
      for i in range(array.shape[0]):
        self.cap.write(array[i])

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.cap.release()
