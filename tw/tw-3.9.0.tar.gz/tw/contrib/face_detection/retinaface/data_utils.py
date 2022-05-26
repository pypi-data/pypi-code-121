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
import os
import torch
from .nets import RetinaFace

cfg_mnet = {
    'name': 'mobilenet0.25',
    'min_sizes': [[16, 32], [64, 128], [256, 512]],
    'steps': [8, 16, 32],
    'variance': [0.1, 0.2],
    'clip': False,
    'loc_weight': 2.0,
    'gpu_train': True,
    'batch_size': 32,
    'ngpu': 1,
    'epoch': 250,
    'decay1': 190,
    'decay2': 220,
    'image_size': 640,
    'pretrain': False,
    'return_layers': {'stage1': 1, 'stage2': 2, 'stage3': 3},
    'in_channel': 32,
    'out_channel': 64
}

cfg_re50 = {
    'name': 'Resnet50',
    'min_sizes': [[16, 32], [64, 128], [256, 512]],
    'steps': [8, 16, 32],
    'variance': [0.1, 0.2],
    'clip': False,
    'loc_weight': 2.0,
    'gpu_train': True,
    'batch_size': 24,
    'ngpu': 4,
    'epoch': 100,
    'decay1': 70,
    'decay2': 90,
    'image_size': 840,
    'pretrain': False,
    'return_layers': {'layer2': 1, 'layer3': 2, 'layer4': 3},
    'in_channel': 256,
    'out_channel': 256
}


def check_keys(model, pretrained_state_dict):
  ckpt_keys = set(pretrained_state_dict.keys())
  model_keys = set(model.state_dict().keys())
  used_pretrained_keys = model_keys & ckpt_keys
  unused_pretrained_keys = ckpt_keys - model_keys
  missing_keys = model_keys - ckpt_keys
  # print('Missing keys:{}'.format(len(missing_keys)))
  # print('Unused checkpoint keys:{}'.format(len(unused_pretrained_keys)))
  # print('Used keys:{}'.format(len(used_pretrained_keys)))
  assert len(used_pretrained_keys) > 0, 'load NONE from pretrained checkpoint'
  return True


def remove_prefix(state_dict, prefix):
  ''' Old style model is stored with all names of parameters sharing common prefix 'module.' '''
  # print('remove prefix \'{}\''.format(prefix))
  def f(x): return x.split(prefix, 1)[-1] if x.startswith(prefix) else x
  return {f(key): value for key, value in state_dict.items()}


def load_model(net='mnet', pretrain=None):
  if net == 'mnet':
    model = RetinaFace(cfg=cfg_mnet, phase='test')
  else:
    model = RetinaFace(cfg=cfg_re50, phase='test')

  pretrained_dict = torch.load(pretrain, map_location='cpu')
  if "state_dict" in pretrained_dict.keys():
    pretrained_dict = remove_prefix(pretrained_dict['state_dict'], 'module.')
  else:
    pretrained_dict = remove_prefix(pretrained_dict, 'module.')
  check_keys(model, pretrained_dict)
  model.load_state_dict(pretrained_dict, strict=False)
  # print('Finished loading model!')
  return model
