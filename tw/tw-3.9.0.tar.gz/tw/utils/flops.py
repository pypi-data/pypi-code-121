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
r"""Model Insight for counting:
  1. FLOPs
  2. Memory Elapsed
  3. Storage Space (Parameters)
  4. Access Cost
"""
import torch
import torch.nn as nn
import numpy as np
import time
import tw


#!<---------------------------------------------------------------------------
#!< op collect
#!<---------------------------------------------------------------------------

def _pixelshuffle_counter_hook(m, inputs, outputs):
  m.__insight__.FLOPs += int(0)
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs[0].shape)
  m.__insight__.OutputShape = list(outputs.shape)


def _upsample_counter_hook(m, inputs, outputs):
  output_size = outputs[0]
  batch_size = output_size.shape[0]
  output_elements_count = batch_size
  for val in output_size.shape[1:]:
    output_elements_count *= val
  m.__insight__.FLOPs += int(output_elements_count)
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs[0].shape)
  m.__insight__.OutputShape = list(outputs.shape)
  # m.__insight__.KernelShape = list(m.weight.shape)


def _relu_counter_hook(m, inputs, outputs):
  active_elements_count = outputs.numel()
  m.__insight__.FLOPs += int(active_elements_count)
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs[0].shape)
  m.__insight__.OutputShape = list(outputs.shape)
  # m.__insight__.KernelShape = list(m.weight.shape)


def _sigmoid_counter_hook(m, inputs, outputs):
  active_elements_count = outputs.numel() * 4
  m.__insight__.FLOPs += int(active_elements_count)
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs[0].shape)
  m.__insight__.OutputShape = list(outputs.shape)
  # m.__insight__.KernelShape = list(m.weight.shape)


def _softmax_counter_hook(m, inputs, outputs):
  active_elements_count = outputs.numel() * 3
  m.__insight__.FLOPs += int(active_elements_count)
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs[0].shape)
  m.__insight__.OutputShape = list(outputs.shape)
  # m.__insight__.KernelShape = list(m.weight.shape)


def _swish_counter_hook(m, inputs, outputs):
  active_elements_count = outputs.numel() * (4 + 1)
  m.__insight__.FLOPs += int(active_elements_count)
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs[0].shape)
  m.__insight__.OutputShape = list(outputs.shape)
  # m.__insight__.KernelShape = list(m.weight.shape)


def _gradient_intensity_counter_hook(m, inputs, outputs):
  # fetch basic info
  inputs = inputs[0]
  batch_size = inputs.shape[0]
  output_dims = list(outputs.shape[2:])

  # compute weight flops
  conv_per_position_flops = 9 * inputs.shape[1] * outputs.shape[1]
  active_elements_count = batch_size * np.prod(output_dims)

  m.__insight__.FLOPs += conv_per_position_flops * active_elements_count
  m.__insight__.Params = m.weight_h.numel() + m.weight_v.numel()
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs[0].shape)
  m.__insight__.OutputShape = list(outputs.shape)


def _dropout_counter_hook(m, inputs, outputs):
  m.__insight__.FLOPs += int(0)
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs[0].shape)
  m.__insight__.OutputShape = list(outputs.shape)
  # m.__insight__.KernelShape = list(m.weight.shape)


def _linear_counter_hook(m, inputs, outputs):
  inputs = inputs[0]
  batch_size = inputs.shape[0]
  m.__insight__.FLOPs += int(batch_size * inputs.shape[1] * outputs.shape[1])
  m.__insight__.Params = m.in_features * m.out_features
  if m.bias is not None:
    m.__insight__.Params += m.out_features
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs.shape)
  m.__insight__.OutputShape = list(outputs.shape)
  # m.__insight__.KernelShape = list(m.weight.shape)


def _pool_counter_hook(m, inputs, outputs):
  inputs = inputs[0]
  m.__insight__.FLOPs += int(np.prod(inputs.shape))
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs.shape)
  m.__insight__.OutputShape = list(outputs.shape)
  # m.__insight__.KernelShape = list(m.weight.shape)


def _bn_counter_hook(m, inputs, outputs):
  inputs = inputs[0]
  batch_flops = np.prod(inputs.shape)
  if m.affine:
    batch_flops *= 2
  m.__insight__.FLOPs += int(batch_flops)
  m.__insight__.Params = 2 * m.num_features
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs.shape)
  m.__insight__.OutputShape = list(outputs.shape)
  m.__insight__.KernelShape = list(m.weight.shape)


def _frozen_bn_counter_hook(m, inputs, outputs):
  inputs = inputs[0]
  channels = inputs.shape[1]
  batch_flops = np.prod(inputs.shape)
  m.__insight__.FLOPs += 2 * int(batch_flops)
  m.__insight__.Params = 4 * channels
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs.shape)
  m.__insight__.OutputShape = list(outputs.shape)
  m.__insight__.KernelShape = list(m.weight.shape)


def _deconv_counter_hook(m, inputs, outputs):
  inputs = inputs[0]
  batch_size = inputs.shape[0]
  input_height, input_width = inputs.shape[2:]
  kernel_height, kernel_width = m.kernel_size
  in_channels = m.in_channels
  out_channels = m.out_channels
  groups = m.groups

  filters_per_channel = out_channels // groups
  conv_per_position_flops = kernel_height * kernel_width * in_channels * filters_per_channel
  active_elements_count = batch_size * input_height * input_width
  m.__insight__.FLOPs += conv_per_position_flops * active_elements_count
  m.__insight__.Params = filters_per_channel * in_channels * kernel_height * kernel_width

  if m.bias is not None:
    output_height, output_width = outputs.shape[2:]
    m.__insight__.FLOPs += out_channels * batch_size * output_height * output_height
    m.__insight__.Params += out_channels

  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs.shape)
  m.__insight__.OutputShape = list(outputs.shape)
  m.__insight__.KernelShape = list(m.kernel_size)


def _conv_counter_hook(m, inputs, outputs):
  # fetch basic info
  inputs = inputs[0]
  batch_size = inputs.shape[0]
  output_dims = list(outputs.shape[2:])
  kernel_dims = list(m.kernel_size)
  in_channels = m.in_channels
  out_channels = m.out_channels
  groups = m.groups

  # compute weight flops
  filters_per_channel = out_channels // groups
  conv_per_position_flops = np.prod(kernel_dims) * in_channels * filters_per_channel
  active_elements_count = batch_size * np.prod(output_dims)
  m.__insight__.FLOPs += conv_per_position_flops * active_elements_count
  m.__insight__.Params = filters_per_channel * in_channels * np.prod(kernel_dims)

  # compute bias flops
  if m.bias is not None:
    bias_flops = out_channels * active_elements_count
    m.__insight__.FLOPs += bias_flops
    m.__insight__.Params += out_channels

  # specific info
  m.__insight__.Type = m.__module__
  m.__insight__.InputShape = list(inputs.shape)
  m.__insight__.OutputShape = list(outputs.shape)
  m.__insight__.KernelShape = list(m.kernel_size)

#!<---------------------------------------------------------------------------
#!< op claim
#!<---------------------------------------------------------------------------


HOOK_MAPS = {
    # convolutions
    nn.Conv1d: _conv_counter_hook,
    nn.Conv2d: _conv_counter_hook,
    nn.Conv3d: _conv_counter_hook,
    # activations
    nn.ReLU: _relu_counter_hook,
    nn.PReLU: _relu_counter_hook,
    nn.ELU: _relu_counter_hook,
    nn.LeakyReLU: _relu_counter_hook,
    nn.ReLU6: _relu_counter_hook,
    nn.Sigmoid: _sigmoid_counter_hook,
    nn.Softmax: _softmax_counter_hook,
    # poolings
    nn.MaxPool1d: _pool_counter_hook,
    nn.AvgPool1d: _pool_counter_hook,
    nn.AvgPool2d: _pool_counter_hook,
    nn.MaxPool2d: _pool_counter_hook,
    nn.MaxPool3d: _pool_counter_hook,
    nn.AvgPool3d: _pool_counter_hook,
    nn.AdaptiveMaxPool1d: _pool_counter_hook,
    nn.AdaptiveAvgPool1d: _pool_counter_hook,
    nn.AdaptiveMaxPool2d: _pool_counter_hook,
    nn.AdaptiveAvgPool2d: _pool_counter_hook,
    nn.AdaptiveMaxPool3d: _pool_counter_hook,
    nn.AdaptiveAvgPool3d: _pool_counter_hook,
    # BNs
    nn.BatchNorm1d: _bn_counter_hook,
    nn.BatchNorm2d: _bn_counter_hook,
    nn.BatchNorm3d: _bn_counter_hook,
    nn.SyncBatchNorm: _bn_counter_hook,
    tw.nn.FrozenBatchNorm2d: _frozen_bn_counter_hook,
    # Dropout
    nn.Dropout: _dropout_counter_hook,
    nn.Dropout2d: _dropout_counter_hook,
    # FC
    nn.Linear: _linear_counter_hook,
    # Upscale
    nn.Upsample: _upsample_counter_hook,
    nn.PixelShuffle: _pixelshuffle_counter_hook,
    # Deconvolution
    nn.ConvTranspose2d: _deconv_counter_hook,
    # padding
    nn.ZeroPad2d: _pool_counter_hook,
    # tw
    tw.nn.Swish: _swish_counter_hook,
    tw.nn.GradientIntensity: _gradient_intensity_counter_hook,
    # tw.nn.Conv2dDynamicSamePadding: _conv_counter_hook,
    # tw.nn.Conv2dStaticSamePadding: _conv_counter_hook,
}


#!<---------------------------------------------------------------------------
#!< hooks
#!<---------------------------------------------------------------------------

class ModuleStat():
  def __init__(self, handle=None):
    self.Handle = handle
    self.FLOPs = 0.0
    self.MACs = 0.0
    self.Params = 0.0
    self.Memory = 0.0
    # specific info
    self.Type = ''
    self.KernelShape = []
    self.InputShape = []
    self.OutputShape = []

  def remove(self):
    if self.Handle is not None:
      self.Handle.remove()

  def reset(self):
    self.FLOPs = 0.0
    self.MACs = 0.0
    self.Params = 0.0
    self.Memory = 0.0
    self.Type = ''
    self.KernelShape = []
    self.InputShape = []
    self.OutputShape = []

  def __add__(self, other):
    self.FLOPs += other.FLOPs
    self.MACs += other.MACs
    self.Params += other.Params
    self.Memory += other.Memory
    return self

  def __str__(self):
    s = 'GFLOPs:{}, GMACs:{}, Params(MB):{}, Memory(MB):{}'.format(
        self.FLOPs / 10.**9, self.MACs / 10.**9, self.Params / 10.**6, self.Memory / 10.**6)
    return s


def register(model: nn.Module):
  r"""regist counter for every module"""
  assert isinstance(model, torch.nn.Module)
  for m in model.modules():
    if len([c for c in m.children()]) == 0:
      try:
        m.__insight__ = ModuleStat(m.register_forward_hook(HOOK_MAPS[type(m)]))
      except BaseException:
        print('[WARN] Failed to matched module type: {}'.format(type(m)))


def unregister(model: nn.Module):
  r"""remove all handle"""
  for m in model.modules():
    if hasattr(m, '__insight__'):
      m.__insight__.remove()
      del m.__insight__


def reset(model: nn.Module):
  r"""clear counter for every module"""
  for m in model.modules():
    if hasattr(m, '__insight__'):
      m.__insight__.reset()


def accumulate(model: nn.Module, unit='M'):
  r"""accumulate counter info"""
  overvall = []

  if unit == 'M':
    coeff = 10.**6
  elif unit == 'K':
    coeff = 10.**3
  elif unit == 'G':
    coeff = 10.**9
  else:
    raise NotImplementedError(unit)

  s = '\n' + '-' * 231 + '\n'
  s = s + '|{:^49}|{:^19}|{:^19}|{:^29}|{:^29}|{:^19}|{:^19}|{:^19}|{:^19}|\n'.format(
      'NAME', 'TYPE', 'KERNEL', 'INPUT', 'OUTPUT', 'FLOPs(%s)' % unit, 'MACs(%s)' % unit, 'PARAMs(%s)' % unit, 'Memory(%s)' % unit)
  s = s + '-' * 231 + '\n'
  for name, m in model.named_modules():
    if len([c for c in m.children()]) == 0:
      try:
        overvall.append(m.__insight__)
        s = s + '|{:^49}|{:^19}|{:^19}|{:^29}|{:^29}|{:^19}|{:^19}|{:^19}|{:^19}|\n'.format(
            name,
            m.__insight__.Type.split('.')[-1],
            str(m.__insight__.KernelShape),
            str(m.__insight__.InputShape),
            str(m.__insight__.OutputShape),
            m.__insight__.FLOPs / coeff,
            m.__insight__.MACs / coeff,
            m.__insight__.Params / coeff,
            m.__insight__.Memory / coeff)
      except BaseException:
        print('[WARN] Failed to matched module type: {}'.format(type(m)))
  s = s + '-' * 231 + '\n'

  stat = ModuleStat(None)
  for ms in overvall:
    stat = stat + ms

  s = s + '|{:^49}|{:^19}|{:^19}|{:^29}|{:^29}|{:^19}|{:^19}|{:^19}|{:^19}|\n'.format(
      'SUM',
      stat.Type.replace('torch.nn.modules.', ''),
      str(stat.KernelShape),
      str(stat.InputShape),
      str(stat.OutputShape),
      stat.FLOPs / coeff,
      stat.MACs / coeff,
      stat.Params / coeff,
      stat.Memory / coeff)
  s = s + '-' * 231 + '\n'

  return s


#!<---------------------------------------------------------------------------
#!< time profiler
#!<---------------------------------------------------------------------------

def register_forward_pre_hook_timer(module, inputs):
  module.start_time = time.time()


def register_forward_hook(module, inputs, outputs):
  if isinstance(outputs, (list, tuple)):
    module.input_shape = inputs[0][0].shape
  else:
    module.input_shape = inputs[0].shape

  if isinstance(outputs, (list, tuple)):
    module.output_shape = outputs[0].shape
  else:
    module.output_shape = outputs.shape

  module.end_time = time.time()
  module.duration += (module.end_time - module.start_time) * 1000.0
  module.count += 1


def profiler(module: nn.Module, total=0.0):
  r"""display registered timer hook.
  """
  size = 49 + 19 + 29 + 29 + 19 + 19 + 7
  s = '\n' + '-' * size + '\n'
  s = s + '|{:^49}|{:^19}|{:^29}|{:^29}|{:^19}|{:^19}|\n'.format(
      'NAME', 'TYPE', 'INPUT SIZE', 'OUTPUT SIZE', 'ELAPSED', 'RATIO')
  s = s + '-' * size + '\n'

  # summarize all elapsed
  total = 0.0
  for name, m in module.named_modules():
    if hasattr(m, 'duration') and len([c for c in m.children()]) == 0:
      total += m.duration

  sum_duration, sum_ratio = 0, 0
  for name, m in module.named_modules():
    if hasattr(m, 'duration') and len([c for c in m.children()]) == 0:
      s = s + '|{:^49}|{:^19}|{:^29}|{:^29}|{:^19.4f}|{:^19.4f}|\n'.format(
          name,
          type(m).__name__,
          str(list(m.input_shape)),
          str(list(m.output_shape)),
          m.duration / m.count,
          m.duration * 100.0 / total)

      sum_duration += m.duration / m.count
      sum_ratio += m.duration * 100.0 / total

  s = s + '-' * size + '\n'

  s = s + '|{:^49}|{:^19}|{:^29}|{:^29}|{:^19.4f}|{:^19.4f}|\n'.format(
          'SUM', '', '[]', '[]', sum_duration, sum_ratio)

  s = s + '-' * size + '\n'

  return s
