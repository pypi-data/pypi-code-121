# Copyright 2018 The KaiJIN Authors. All Rights Reserved.
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
""" The EfficientNet Family in PyTorch

An implementation of EfficienNet that covers variety of related models with efficient architectures:

* EfficientNet-V2
  - `EfficientNetV2: Smaller Models and Faster Training` - https://arxiv.org/abs/2104.00298

* EfficientNet (B0-B8, L2 + Tensorflow pretrained AutoAug/RandAug/AdvProp/NoisyStudent weight ports)
  - EfficientNet: Rethinking Model Scaling for CNNs - https://arxiv.org/abs/1905.11946
  - CondConv: Conditionally Parameterized Convolutions for Efficient Inference - https://arxiv.org/abs/1904.04971
  - Adversarial Examples Improve Image Recognition - https://arxiv.org/abs/1911.09665
  - Self-training with Noisy Student improves ImageNet classification - https://arxiv.org/abs/1911.04252

* MixNet (Small, Medium, and Large)
  - MixConv: Mixed Depthwise Convolutional Kernels - https://arxiv.org/abs/1907.09595

* MNasNet B1, A1 (SE), Small
  - MnasNet: Platform-Aware Neural Architecture Search for Mobile - https://arxiv.org/abs/1807.11626

* FBNet-C
  - FBNet: Hardware-Aware Efficient ConvNet Design via Differentiable NAS - https://arxiv.org/abs/1812.03443

* Single-Path NAS Pixel1
  - Single-Path NAS: Designing Hardware-Efficient ConvNets - https://arxiv.org/abs/1904.02877

* And likely more...

The majority of the above models (EfficientNet*, MixNet, MnasNet) and original weights were made available
by Mingxing Tan, Quoc Le, and other members of their Google Brain team. Thanks for consistently releasing
the models and weights open source!

Hacked together by / Copyright 2021 Ross Wightman
"""
from functools import partial
import math
import torch
from torch import nn
import tw
import os
import re
import math
from collections import OrderedDict
from copy import deepcopy
from typing import Any, Callable, Optional, Tuple
import torch
import torch.nn as nn
import tw
from tw.nn.conv import SameConv2d
from tw.nn import Swish
from tw.nn import Mish
from tw.nn.conv import _round_channels as round_channels
from tw.nn.conv import _create_conv2d as create_conv2d
from tw.nn import SqueezeExciteModule as SqueezeExcite


# Defaults used for Google/Tensorflow training of mobile networks /w RMSprop as per
# papers and TF reference implementations. PT momentum equiv for TF decay is (1 - TF decay)
# NOTE: momentum varies btw .99 and .9997 depending on source
# .99 in official TF TPU impl
# .9997 (/w .999 in search space) for paper
BN_MOMENTUM_TF_DEFAULT = 1 - 0.99
BN_EPS_TF_DEFAULT = 1e-3
_BN_ARGS_TF = dict(momentum=BN_MOMENTUM_TF_DEFAULT, eps=BN_EPS_TF_DEFAULT)

IMAGENET_INCEPTION_MEAN = (0.5, 0.5, 0.5)
IMAGENET_INCEPTION_STD = (0.5, 0.5, 0.5)
IMAGENET_DEFAULT_MEAN = (0.485, 0.456, 0.406)
IMAGENET_DEFAULT_STD = (0.229, 0.224, 0.225)


def _cfg(url='', **kwargs):
  return {
      'url': url, 'num_classes': 1000, 'input_size': (3, 224, 224), 'pool_size': (7, 7),
      'crop_pct': 0.875, 'interpolation': 'bicubic',
      'mean': IMAGENET_DEFAULT_MEAN, 'std': IMAGENET_DEFAULT_STD,
      'first_conv': 'conv_stem', 'classifier': 'classifier',
      **kwargs
  }


default_cfgs = {
    'mnasnet_050': _cfg(url=''),
    'mnasnet_075': _cfg(url=''),
    'mnasnet_100': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mnasnet_b1-74cb7081.pth'),
    'mnasnet_140': _cfg(url=''),

    'semnasnet_050': _cfg(url=''),
    'semnasnet_075': _cfg(url=''),
    'semnasnet_100': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mnasnet_a1-d9418771.pth'),
    'semnasnet_140': _cfg(url=''),
    'mnasnet_small': _cfg(url=''),

    'mobilenetv2_100': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mobilenetv2_100_ra-b33bc2c4.pth'),
    'mobilenetv2_110d': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mobilenetv2_110d_ra-77090ade.pth'),
    'mobilenetv2_120d': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mobilenetv2_120d_ra-5987e2ed.pth'),
    'mobilenetv2_140': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mobilenetv2_140_ra-21a4e913.pth'),

    'fbnetc_100': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/fbnetc_100-c345b898.pth',
        interpolation='bilinear'),
    'spnasnet_100': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/spnasnet_100-048bc3f4.pth',
        interpolation='bilinear'),

    # NOTE experimenting with alternate attention
    'eca_efficientnet_b0': _cfg(
        url=''),
    'gc_efficientnet_b0': _cfg(
        url=''),

    'efficientnet_b0': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_b0_ra-3dd342df.pth'),
    'efficientnet_b1': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_b1-533bc792.pth',
        test_input_size=(3, 256, 256), crop_pct=1.0),
    'efficientnet_b2': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_b2_ra-bcdf34b7.pth',
        input_size=(3, 256, 256), pool_size=(8, 8), test_input_size=(3, 288, 288), crop_pct=1.0),
    'efficientnet_b3': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_b3_ra2-cf984f9c.pth',
        input_size=(3, 288, 288), pool_size=(9, 9), test_input_size=(3, 320, 320), crop_pct=1.0),
    'efficientnet_b4': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_b4_ra2_320-7eb33cd5.pth',
        input_size=(3, 320, 320), pool_size=(10, 10), test_input_size=(3, 384, 384), crop_pct=1.0),
    'efficientnet_b5': _cfg(
        url='', input_size=(3, 456, 456), pool_size=(15, 15), crop_pct=0.934),
    'efficientnet_b6': _cfg(
        url='', input_size=(3, 528, 528), pool_size=(17, 17), crop_pct=0.942),
    'efficientnet_b7': _cfg(
        url='', input_size=(3, 600, 600), pool_size=(19, 19), crop_pct=0.949),
    'efficientnet_b8': _cfg(
        url='', input_size=(3, 672, 672), pool_size=(21, 21), crop_pct=0.954),
    'efficientnet_l2': _cfg(
        url='', input_size=(3, 800, 800), pool_size=(25, 25), crop_pct=0.961),

    'efficientnet_es': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_es_ra-f111e99c.pth'),
    'efficientnet_em': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_em_ra2-66250f76.pth',
        input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882),
    'efficientnet_el': _cfg(
        url='https://github.com/DeGirum/pruned-models/releases/download/efficientnet_v1.0/efficientnet_el.pth',
        input_size=(3, 300, 300), pool_size=(10, 10), crop_pct=0.904),

    'efficientnet_es_pruned': _cfg(
        url='https://github.com/DeGirum/pruned-models/releases/download/efficientnet_v1.0/efficientnet_es_pruned75.pth'),
    'efficientnet_el_pruned': _cfg(
        url='https://github.com/DeGirum/pruned-models/releases/download/efficientnet_v1.0/efficientnet_el_pruned70.pth',
        input_size=(3, 300, 300), pool_size=(10, 10), crop_pct=0.904),

    'efficientnet_cc_b0_4e': _cfg(url=''),
    'efficientnet_cc_b0_8e': _cfg(url=''),
    'efficientnet_cc_b1_8e': _cfg(url='', input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882),

    'efficientnet_lite0': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_lite0_ra-37913777.pth'),
    'efficientnet_lite1': _cfg(
        url='',
        input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882),
    'efficientnet_lite2': _cfg(
        url='',
        input_size=(3, 260, 260), pool_size=(9, 9), crop_pct=0.890),
    'efficientnet_lite3': _cfg(
        url='',
        input_size=(3, 300, 300), pool_size=(10, 10), crop_pct=0.904),
    'efficientnet_lite4': _cfg(
        url='', input_size=(3, 380, 380), pool_size=(12, 12), crop_pct=0.922),

    'efficientnet_b1_pruned': _cfg(
        url='https://imvl-automl-sh.oss-cn-shanghai.aliyuncs.com/darts/hyperml/hyperml/job_45403/outputs/effnetb1_pruned_9ebb3fe6.pth',
        input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882, mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD),
    'efficientnet_b2_pruned': _cfg(
        url='https://imvl-automl-sh.oss-cn-shanghai.aliyuncs.com/darts/hyperml/hyperml/job_45403/outputs/effnetb2_pruned_203f55bc.pth',
        input_size=(3, 260, 260), pool_size=(9, 9), crop_pct=0.890, mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD),
    'efficientnet_b3_pruned': _cfg(
        url='https://imvl-automl-sh.oss-cn-shanghai.aliyuncs.com/darts/hyperml/hyperml/job_45403/outputs/effnetb3_pruned_5abcc29f.pth',
        input_size=(3, 300, 300), pool_size=(10, 10), crop_pct=0.904, mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD),

    'efficientnetv2_rw_t': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnetv2_t_agc-3620981a.pth',
        input_size=(3, 224, 224), test_input_size=(3, 288, 288), pool_size=(7, 7), crop_pct=1.0),
    'gc_efficientnetv2_rw_t': _cfg(
        url='',
        input_size=(3, 224, 224), test_input_size=(3, 288, 288), pool_size=(7, 7), crop_pct=1.0),
    'efficientnetv2_rw_s': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_v2s_ra2_288-a6477665.pth',
        input_size=(3, 288, 288), test_input_size=(3, 384, 384), pool_size=(9, 9), crop_pct=1.0),
    'efficientnetv2_rw_m': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnetv2_rw_m_agc-3d90cb1e.pth',
        input_size=(3, 320, 320), test_input_size=(3, 416, 416), pool_size=(10, 10), crop_pct=1.0),

    'efficientnetv2_s': _cfg(
        url='',
        input_size=(3, 288, 288), test_input_size=(3, 384, 384), pool_size=(9, 9), crop_pct=1.0),
    'efficientnetv2_m': _cfg(
        url='',
        input_size=(3, 320, 320), test_input_size=(3, 416, 416), pool_size=(10, 10), crop_pct=1.0),
    'efficientnetv2_l': _cfg(
        url='',
        input_size=(3, 384, 384), test_input_size=(3, 480, 480), pool_size=(12, 12), crop_pct=1.0),

    'tf_efficientnet_b0': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b0_aa-827b6e33.pth',
        input_size=(3, 224, 224)),
    'tf_efficientnet_b1': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b1_aa-ea7a6ee0.pth',
        input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882),
    'tf_efficientnet_b2': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b2_aa-60c94f97.pth',
        input_size=(3, 260, 260), pool_size=(9, 9), crop_pct=0.890),
    'tf_efficientnet_b3': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b3_aa-84b4657e.pth',
        input_size=(3, 300, 300), pool_size=(10, 10), crop_pct=0.904),
    'tf_efficientnet_b4': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b4_aa-818f208c.pth',
        input_size=(3, 380, 380), pool_size=(12, 12), crop_pct=0.922),
    'tf_efficientnet_b5': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b5_ra-9a3e5369.pth',
        input_size=(3, 456, 456), pool_size=(15, 15), crop_pct=0.934),
    'tf_efficientnet_b6': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b6_aa-80ba17e4.pth',
        input_size=(3, 528, 528), pool_size=(17, 17), crop_pct=0.942),
    'tf_efficientnet_b7': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b7_ra-6c08e654.pth',
        input_size=(3, 600, 600), pool_size=(19, 19), crop_pct=0.949),
    'tf_efficientnet_b8': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b8_ra-572d5dd9.pth',
        input_size=(3, 672, 672), pool_size=(21, 21), crop_pct=0.954),

    'tf_efficientnet_b0_ap': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b0_ap-f262efe1.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD, input_size=(3, 224, 224)),
    'tf_efficientnet_b1_ap': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b1_ap-44ef0a3d.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD,
        input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882),
    'tf_efficientnet_b2_ap': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b2_ap-2f8e7636.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD,
        input_size=(3, 260, 260), pool_size=(9, 9), crop_pct=0.890),
    'tf_efficientnet_b3_ap': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b3_ap-aad25bdd.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD,
        input_size=(3, 300, 300), pool_size=(10, 10), crop_pct=0.904),
    'tf_efficientnet_b4_ap': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b4_ap-dedb23e6.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD,
        input_size=(3, 380, 380), pool_size=(12, 12), crop_pct=0.922),
    'tf_efficientnet_b5_ap': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b5_ap-9e82fae8.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD,
        input_size=(3, 456, 456), pool_size=(15, 15), crop_pct=0.934),
    'tf_efficientnet_b6_ap': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b6_ap-4ffb161f.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD,
        input_size=(3, 528, 528), pool_size=(17, 17), crop_pct=0.942),
    'tf_efficientnet_b7_ap': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b7_ap-ddb28fec.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD,
        input_size=(3, 600, 600), pool_size=(19, 19), crop_pct=0.949),
    'tf_efficientnet_b8_ap': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b8_ap-00e169fa.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD,
        input_size=(3, 672, 672), pool_size=(21, 21), crop_pct=0.954),

    'tf_efficientnet_b0_ns': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b0_ns-c0e6a31c.pth',
        input_size=(3, 224, 224)),
    'tf_efficientnet_b1_ns': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b1_ns-99dd0c41.pth',
        input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882),
    'tf_efficientnet_b2_ns': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b2_ns-00306e48.pth',
        input_size=(3, 260, 260), pool_size=(9, 9), crop_pct=0.890),
    'tf_efficientnet_b3_ns': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b3_ns-9d44bf68.pth',
        input_size=(3, 300, 300), pool_size=(10, 10), crop_pct=0.904),
    'tf_efficientnet_b4_ns': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b4_ns-d6313a46.pth',
        input_size=(3, 380, 380), pool_size=(12, 12), crop_pct=0.922),
    'tf_efficientnet_b5_ns': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b5_ns-6f26d0cf.pth',
        input_size=(3, 456, 456), pool_size=(15, 15), crop_pct=0.934),
    'tf_efficientnet_b6_ns': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b6_ns-51548356.pth',
        input_size=(3, 528, 528), pool_size=(17, 17), crop_pct=0.942),
    'tf_efficientnet_b7_ns': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b7_ns-1dbc32de.pth',
        input_size=(3, 600, 600), pool_size=(19, 19), crop_pct=0.949),
    'tf_efficientnet_l2_ns_475': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_l2_ns_475-bebbd00a.pth',
        input_size=(3, 475, 475), pool_size=(15, 15), crop_pct=0.936),
    'tf_efficientnet_l2_ns': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_l2_ns-df73bb44.pth',
        input_size=(3, 800, 800), pool_size=(25, 25), crop_pct=0.96),

    'tf_efficientnet_es': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_es-ca1afbfe.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 224, 224), ),
    'tf_efficientnet_em': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_em-e78cfe58.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882),
    'tf_efficientnet_el': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_el-5143854e.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 300, 300), pool_size=(10, 10), crop_pct=0.904),

    'tf_efficientnet_cc_b0_4e': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_cc_b0_4e-4362b6b2.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD),
    'tf_efficientnet_cc_b0_8e': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_cc_b0_8e-66184a25.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD),
    'tf_efficientnet_cc_b1_8e': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_cc_b1_8e-f7c79ae1.pth',
        mean=IMAGENET_INCEPTION_MEAN, std=IMAGENET_INCEPTION_STD,
        input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882),

    'tf_efficientnet_lite0': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_lite0-0aa007d2.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        interpolation='bicubic',  # should be bilinear but bicubic better match for TF bilinear at low res
    ),
    'tf_efficientnet_lite1': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_lite1-bde8b488.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 240, 240), pool_size=(8, 8), crop_pct=0.882,
        interpolation='bicubic',  # should be bilinear but bicubic better match for TF bilinear at low res
    ),
    'tf_efficientnet_lite2': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_lite2-dcccb7df.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 260, 260), pool_size=(9, 9), crop_pct=0.890,
        interpolation='bicubic',  # should be bilinear but bicubic better match for TF bilinear at low res
    ),
    'tf_efficientnet_lite3': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_lite3-b733e338.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 300, 300), pool_size=(10, 10), crop_pct=0.904, interpolation='bilinear'),
    'tf_efficientnet_lite4': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_lite4-741542c3.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 380, 380), pool_size=(12, 12), crop_pct=0.920, interpolation='bilinear'),

    'tf_efficientnetv2_s': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_s-eb54923e.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 300, 300), test_input_size=(3, 384, 384), pool_size=(10, 10), crop_pct=1.0),
    'tf_efficientnetv2_m': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_m-cc09e0cd.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 384, 384), test_input_size=(3, 480, 480), pool_size=(12, 12), crop_pct=1.0),
    'tf_efficientnetv2_l': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_l-d664b728.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 384, 384), test_input_size=(3, 480, 480), pool_size=(12, 12), crop_pct=1.0),

    'tf_efficientnetv2_s_in21ft1k': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_s_21ft1k-d7dafa41.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 300, 300), test_input_size=(3, 384, 384), pool_size=(10, 10), crop_pct=1.0),
    'tf_efficientnetv2_m_in21ft1k': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_m_21ft1k-bf41664a.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 384, 384), test_input_size=(3, 480, 480), pool_size=(12, 12), crop_pct=1.0),
    'tf_efficientnetv2_l_in21ft1k': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_l_21ft1k-60127a9d.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5),
        input_size=(3, 384, 384), test_input_size=(3, 480, 480), pool_size=(12, 12), crop_pct=1.0),

    'tf_efficientnetv2_s_in21k': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_s_21k-6337ad01.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5), num_classes=21843,
        input_size=(3, 300, 300), test_input_size=(3, 384, 384), pool_size=(10, 10), crop_pct=1.0),
    'tf_efficientnetv2_m_in21k': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_m_21k-361418a2.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5), num_classes=21843,
        input_size=(3, 384, 384), test_input_size=(3, 480, 480), pool_size=(12, 12), crop_pct=1.0),
    'tf_efficientnetv2_l_in21k': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_l_21k-91a19ec9.pth',
        mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5), num_classes=21843,
        input_size=(3, 384, 384), test_input_size=(3, 480, 480), pool_size=(12, 12), crop_pct=1.0),

    'tf_efficientnetv2_b0': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_b0-c7cc451f.pth',
        input_size=(3, 192, 192), test_input_size=(3, 224, 224), pool_size=(6, 6)),
    'tf_efficientnetv2_b1': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_b1-be6e41b0.pth',
        input_size=(3, 192, 192), test_input_size=(3, 240, 240), pool_size=(6, 6), crop_pct=0.882),
    'tf_efficientnetv2_b2': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_b2-847de54e.pth',
        input_size=(3, 208, 208), test_input_size=(3, 260, 260), pool_size=(7, 7), crop_pct=0.890),
    'tf_efficientnetv2_b3': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-effv2-weights/tf_efficientnetv2_b3-57773f13.pth',
        input_size=(3, 240, 240), test_input_size=(3, 300, 300), pool_size=(8, 8), crop_pct=0.904),

    'mixnet_s': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mixnet_s-a907afbc.pth'),
    'mixnet_m': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mixnet_m-4647fc68.pth'),
    'mixnet_l': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mixnet_l-5a9a2ed8.pth'),
    'mixnet_xl': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mixnet_xl_ra-aac3c00c.pth'),
    'mixnet_xxl': _cfg(),

    'tf_mixnet_s': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_mixnet_s-89d3354b.pth'),
    'tf_mixnet_m': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_mixnet_m-0f4d8805.pth'),
    'tf_mixnet_l': _cfg(
        url='https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_mixnet_l-6c92e0c8.pth'),
}


def _decode_ksize(ss: str):
  """str like 'a1.1'
  """
  return int(ss) if ss.isdigit() else [int(k) for k in ss.split('.')]


def _decode_block_def(block_def: str):
  """decode block def to args.

  Args:
      block_def (str): All args can exist in any order with the exception of the
        leading string which is assumed to indicate the block type.

        ir = InvertedResidual, ds = DepthwiseSep, dsa = DeptwhiseSep with pw act, cn = ConvBnAct)
        r - number of repeat blocks,
        k - kernel size,
        s - strides (1-9),
        e - expansion ratio,
        c - output channels,
        se - squeeze/excitation ratio
        n - activation fn ('re', 'r6', 'hs', or 'sw')

  Returns:
      A list of block args (dicts)
  """
  ops = block_def.split('_')
  block_type = ops[0]
  options = {}
  skip = None

  for op in ops[1:]:
    # force no skip connection
    if op == 'noskip':
      skip = False
    # force a skip connection
    elif op == 'skip':
      skip = True
    # activation function
    elif op.startswith('n'):
      key = op[0]
      name = op[1:]
      if name == 're':
        value = nn.ReLU
      elif name == 'r6':
        value = nn.ReLU6
      elif name == 'hs':
        value = nn.Hardswish
      elif name == 'sw':
        value = Swish
      elif name == 'mi':
        value = Mish
      else:
        continue
      options[key] = value
    # normal parameter
    else:
      splits = re.split(r'(\d.*)', op)
      if len(splits) >= 2:
        key, value = splits[:2]
        options[key] = value

  # if act_layer is None, the model default (passed to model init) will be used
  if 'n' in options:
    act_layer = options['n']
  else:
    act_layer = None

  # expansion kernel size
  if 'a' in options:
    exp_kernel_size = _decode_ksize(options['a'])
  else:
    exp_kernel_size = 1

  # point-wise kernel size
  if 'p' in options:
    pw_kernel_size = _decode_ksize(options['p'])
  else:
    pw_kernel_size = 1

  # in_channels
  if 'fc' in options:
    force_in_chs = options['fc']
  else:
    force_in_chs = 0

  # repeat
  num_repeat = int(options['r'])

  # each type of block has different valid arguments, fill accordingly
  if block_type == 'ir':
    block_args = dict(
        block_type=block_type,
        dw_kernel_size=_decode_ksize(options['k']),
        exp_kernel_size=exp_kernel_size,
        pw_kernel_size=pw_kernel_size,
        out_chs=int(options['c']),
        exp_ratio=float(options['e']),
        se_ratio=float(options['se']) if 'se' in options else 0.,
        stride=int(options['s']),
        act_layer=act_layer,
        noskip=skip is False)
    if 'cc' in options:
      block_args['num_experts'] = int(options['cc'])
  elif block_type == 'ds' or block_type == 'dsa':
    block_args = dict(
        block_type=block_type,
        dw_kernel_size=_decode_ksize(options['k']),
        pw_kernel_size=pw_kernel_size,
        out_chs=int(options['c']),
        se_ratio=float(options['se']) if 'se' in options else 0.,
        stride=int(options['s']),
        act_layer=act_layer,
        pw_act=block_type == 'dsa',
        noskip=block_type == 'dsa' or skip is False)
  elif block_type == 'er':
    block_args = dict(
        block_type=block_type,
        exp_kernel_size=_decode_ksize(options['k']),
        pw_kernel_size=pw_kernel_size,
        out_chs=int(options['c']),
        exp_ratio=float(options['e']),
        force_in_chs=force_in_chs,
        se_ratio=float(options['se']) if 'se' in options else 0.,
        stride=int(options['s']),
        act_layer=act_layer,
        noskip=skip is False)
  elif block_type == 'cn':
    block_args = dict(
        block_type=block_type,
        kernel_size=int(options['k']),
        out_chs=int(options['c']),
        stride=int(options['s']),
        act_layer=act_layer,
        skip=skip is True)
  else:
    assert False, 'Unknown block type (%s)' % block_type

  return block_args, num_repeat


def _scale_stage_depth(stack_args, repeats, depth_multiplier=1.0, depth_trunc='ceil'):
  """Per-stage depth scaling

    Scales the block repeats in each stage. This depth scaling impl maintains
    compatibility with the EfficientNet scaling method, while allowing sensible
    scaling for other models that may have multiple block arg definitions in each stage.

  Args:
      stack_args ([type]): [description]
      repeats ([type]): [description]
      depth_multiplier (float, optional): [description]. Defaults to 1.0.
      depth_trunc (str, optional): [description]. Defaults to 'ceil'.

  """
  # We scale the total repeat count for each stage, there may be multiple
  # block arg defs per stage so we need to sum.
  num_repeat = sum(repeats)
  if depth_trunc == 'round':
      # Truncating to int by rounding allows stages with few repeats to remain
      # proportionally smaller for longer. This is a good choice when stage definitions
      # include single repeat stages that we'd prefer to keep that way as long as possible
    num_repeat_scaled = max(1, round(num_repeat * depth_multiplier))
  else:
    # The default for EfficientNet truncates repeats to int via 'ceil'.
    # Any multiplier > 1.0 will result in an increased depth for every stage.
    num_repeat_scaled = int(math.ceil(num_repeat * depth_multiplier))

  # Proportionally distribute repeat count scaling to each block definition in the stage.
  # Allocation is done in reverse as it results in the first block being less likely to be scaled.
  # The first block makes less sense to repeat in most of the arch definitions.
  repeats_scaled = []
  for r in repeats[::-1]:
    rs = max(1, round((r / num_repeat * num_repeat_scaled)))
    repeats_scaled.append(rs)
    num_repeat -= r
    num_repeat_scaled -= rs
  repeats_scaled = repeats_scaled[::-1]

  # Apply the calculated scaling to each block arg in the stage
  sa_scaled = []
  for args, repeat in zip(stack_args, repeats_scaled):
    sa_scaled.extend([deepcopy(args) for _ in range(repeat)])
  return sa_scaled


def decode_arch_def(arch_def, depth_multiplier=1.0, depth_trunc='ceil',
                    experts_multiplier=1, fix_first_last=False):
  """decode a list of string as arch def.

  Usage:
    arch_def = [
      # stage 0, 112x112 in
      ['ds_r1_k3_s2_e1_c16'],
      # stage 1, 56x56 in
      ['ir_r1_k3_s2_e4.5_c24', 'ir_r1_k3_s1_e3.67_c24'],
      # stage 2, 28x28 in
      ['ir_r1_k3_s2_e4_c40', 'ir_r2_k3_s1_e6_c40'],
      # stage 3, 14x14 in
      ['ir_r2_k3_s1_e3_c48'],
      # stage 4, 14x14in
      ['ir_r3_k3_s2_e6_c96'],
      # stage 6, 7x7 in
      ['cn_r1_k1_s1_c576'],
    ]
    decode_arch_def(arch_def)

  Args:
      arch_def (list[str]): arch definitions.
      depth_multiplier (float): [description]. Defaults to 1.0.
      depth_trunc (str): [description]. Defaults to 'ceil'.
      experts_multiplier (int): [description]. Defaults to 1.
      fix_first_last (bool): [description]. Defaults to False.

  Returns:
      A list of block args (dicts)
  """
  arch_args = []

  # multiplier
  if isinstance(depth_multiplier, tuple):
    assert len(depth_multiplier) == len(arch_def)
  else:
    depth_multiplier = (depth_multiplier, ) * len(arch_def)

  # build blocks
  for idx, (block_defs, multiplier) in enumerate(zip(arch_def, depth_multiplier)):
    assert isinstance(block_defs, list)
    stack_args = []
    repeats = []

    for block_def in block_defs:
      assert isinstance(block_def, str)
      args, repeat = _decode_block_def(block_def)
      if args.get('num_experts', 0) > 0 and experts_multiplier > 1:
        args['num_experts'] *= experts_multiplier
      stack_args.append(args)
      repeats.append(repeat)

    if fix_first_last and (idx == 0 or idx == len(arch_def) - 1):
      arch_args.append(_scale_stage_depth(stack_args, repeats, 1.0, depth_trunc))
    else:
      arch_args.append(_scale_stage_depth(stack_args, repeats, multiplier, depth_trunc))

  return arch_args


def load_state_dict(checkpoint_path, use_ema=False):
  if checkpoint_path and os.path.isfile(checkpoint_path):
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    state_dict_key = 'state_dict'
    if isinstance(checkpoint, dict):
      if use_ema and 'state_dict_ema' in checkpoint:
        state_dict_key = 'state_dict_ema'
    if state_dict_key and state_dict_key in checkpoint:
      new_state_dict = OrderedDict()
      for k, v in checkpoint[state_dict_key].items():
        # strip `module.` prefix
        name = k[7:] if k.startswith('module') else k
        new_state_dict[name] = v
      state_dict = new_state_dict
    else:
      state_dict = checkpoint
    tw.logger.info("Loaded {} from checkpoint '{}'".format(state_dict_key, checkpoint_path))
    return state_dict
  else:
    tw.logger.error("No checkpoint found at '{}'".format(checkpoint_path))
    raise FileNotFoundError()


def load_checkpoint(model, checkpoint_path, use_ema=False, strict=True):
  if os.path.splitext(checkpoint_path)[-1].lower() in ('.npz', '.npy'):
    # numpy checkpoint, try to load via model specific load_pretrained fn
    if hasattr(model, 'load_pretrained'):
      model.load_pretrained(checkpoint_path)
    else:
      raise NotImplementedError('Model cannot load numpy checkpoint')
    return
  state_dict = load_state_dict(checkpoint_path, use_ema)
  model.load_state_dict(state_dict, strict=strict)


def resume_checkpoint(model, checkpoint_path, optimizer=None, loss_scaler=None, log_info=True):
  resume_epoch = None
  if os.path.isfile(checkpoint_path):
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
      if log_info:
        tw.logger.info('Restoring model state from checkpoint...')
      new_state_dict = OrderedDict()
      for k, v in checkpoint['state_dict'].items():
        name = k[7:] if k.startswith('module') else k
        new_state_dict[name] = v
      model.load_state_dict(new_state_dict)

      if optimizer is not None and 'optimizer' in checkpoint:
        if log_info:
          tw.logger.info('Restoring optimizer state from checkpoint...')
        optimizer.load_state_dict(checkpoint['optimizer'])

      if loss_scaler is not None and loss_scaler.state_dict_key in checkpoint:
        if log_info:
          tw.logger.info('Restoring AMP loss scaler state from checkpoint...')
        loss_scaler.load_state_dict(checkpoint[loss_scaler.state_dict_key])

      if 'epoch' in checkpoint:
        resume_epoch = checkpoint['epoch']
        if 'version' in checkpoint and checkpoint['version'] > 1:
          resume_epoch += 1  # start at the next epoch, old checkpoints incremented before save

      if log_info:
        tw.logger.info("Loaded checkpoint '{}' (epoch {})".format(checkpoint_path, checkpoint['epoch']))
    else:
      model.load_state_dict(checkpoint)
      if log_info:
        tw.logger.info("Loaded checkpoint '{}'".format(checkpoint_path))
    return resume_epoch
  else:
    tw.logger.error("No checkpoint found at '{}'".format(checkpoint_path))
    raise FileNotFoundError()


def load_custom_pretrained(model, default_cfg=None, load_fn=None, progress=False, check_hash=False):
  r"""Loads a custom (read non .pth) weight file

  Downloads checkpoint file into cache-dir like torch.hub based loaders, but calls
  a passed in custom load fun, or the `load_pretrained` model member fn.

  If the object is already present in `model_dir`, it's deserialized and returned.
  The default value of `model_dir` is ``<hub_dir>/checkpoints`` where
  `hub_dir` is the directory returned by :func:`~torch.hub.get_dir`.

  Args:
      model: The instantiated model to load weights into
      default_cfg (dict): Default pretrained model cfg
      load_fn: An external stand alone fn that loads weights into provided model, otherwise a fn named
          'laod_pretrained' on the model will be called if it exists
      progress (bool, optional): whether or not to display a progress bar to stderr. Default: False
      check_hash(bool, optional): If True, the filename part of the URL should follow the naming convention
          ``filename-<sha256>.ext`` where ``<sha256>`` is the first eight or more
          digits of the SHA256 hash of the contents of the file. The hash is used to
          ensure unique names and to verify the contents of the file. Default: False
  """
  default_cfg = default_cfg or getattr(model, 'default_cfg', None) or {}
  pretrained_url = default_cfg.get('url', None)
  if not pretrained_url:
    tw.logger.warning("No pretrained weights exist for this model. Using random initialization.")
    return
  cached_file = download_cached_file(default_cfg['url'], check_hash=check_hash, progress=progress)

  if load_fn is not None:
    load_fn(model, cached_file)
  elif hasattr(model, 'load_pretrained'):
    model.load_pretrained(cached_file)
  else:
    tw.logger.warning("Valid function to load pretrained weights is not available, using random initialization.")


def adapt_input_conv(in_chans, conv_weight):
  conv_type = conv_weight.dtype
  conv_weight = conv_weight.float()  # Some weights are in torch.half, ensure it's float for sum on CPU
  O, I, J, K = conv_weight.shape
  if in_chans == 1:
    if I > 3:
      assert conv_weight.shape[1] % 3 == 0
      # For models with space2depth stems
      conv_weight = conv_weight.reshape(O, I // 3, 3, J, K)
      conv_weight = conv_weight.sum(dim=2, keepdim=False)
    else:
      conv_weight = conv_weight.sum(dim=1, keepdim=True)
  elif in_chans != 3:
    if I != 3:
      raise NotImplementedError('Weight format not supported by conversion.')
    else:
      # NOTE this strategy should be better than random init, but there could be other combinations of
      # the original RGB input layer weights that'd work better for specific cases.
      repeat = int(math.ceil(in_chans / 3))
      conv_weight = conv_weight.repeat(1, repeat, 1, 1)[:, :in_chans, :, :]
      conv_weight *= (3 / float(in_chans))
  conv_weight = conv_weight.to(conv_type)
  return conv_weight


def load_pretrained(model, default_cfg=None, num_classes=1000, in_chans=3, filter_fn=None, strict=True, progress=False):
  """ Load pretrained checkpoint

  Args:
      model (nn.Module) : PyTorch model module
      default_cfg (Optional[Dict]): default configuration for pretrained weights / target dataset
      num_classes (int): num_classes for model
      in_chans (int): in_chans for model
      filter_fn (Optional[Callable]): state_dict filter fn for load (takes state_dict, model as args)
      strict (bool): strict load of checkpoint
      progress (bool): enable progress bar for weight download

  """
  default_cfg = default_cfg or getattr(model, 'default_cfg', None) or {}
  pretrained_url = default_cfg.get('url', None)
  state_dict = tw.checkpoint.load(pretrained_url)
  if filter_fn is not None:
    # for backwards compat with filter fn that take one arg, try one first, the two
    try:
      state_dict = filter_fn(state_dict)
    except TypeError:
      state_dict = filter_fn(state_dict, model)

  input_convs = default_cfg.get('first_conv', None)
  if input_convs is not None and in_chans != 3:
    if isinstance(input_convs, str):
      input_convs = (input_convs,)
    for input_conv_name in input_convs:
      weight_name = input_conv_name + '.weight'
      try:
        state_dict[weight_name] = adapt_input_conv(in_chans, state_dict[weight_name])
        tw.logger.info(
            f'Converted input conv {input_conv_name} pretrained weights from 3 to {in_chans} channel(s)')
      except NotImplementedError as e:
        del state_dict[weight_name]
        strict = False
        tw.logger.warning(
            f'Unable to convert pretrained {input_conv_name} weights, using random init for this layer.')

  classifiers = default_cfg.get('classifier', None)
  label_offset = default_cfg.get('label_offset', 0)
  if classifiers is not None:
    if isinstance(classifiers, str):
      classifiers = (classifiers,)
    if num_classes != default_cfg['num_classes']:
      for classifier_name in classifiers:
        # completely discard fully connected if model num_classes doesn't match pretrained weights
        del state_dict[classifier_name + '.weight']
        del state_dict[classifier_name + '.bias']
      strict = False
    elif label_offset > 0:
      for classifier_name in classifiers:
        # special case for pretrained weights with an extra background class in pretrained weights
        classifier_weight = state_dict[classifier_name + '.weight']
        state_dict[classifier_name + '.weight'] = classifier_weight[label_offset:]
        classifier_bias = state_dict[classifier_name + '.bias']
        state_dict[classifier_name + '.bias'] = classifier_bias[label_offset:]

  model.load_state_dict(state_dict, strict=strict)


def extract_layer(model, layer):
  layer = layer.split('.')
  module = model
  if hasattr(model, 'module') and layer[0] != 'module':
    module = model.module
  if not hasattr(model, 'module') and layer[0] == 'module':
    layer = layer[1:]
  for l in layer:
    if hasattr(module, l):
      if not l.isdigit():
        module = getattr(module, l)
      else:
        module = module[int(l)]
    else:
      return module
  return module


def set_layer(model, layer, val):
  layer = layer.split('.')
  module = model
  if hasattr(model, 'module') and layer[0] != 'module':
    module = model.module
  lst_index = 0
  module2 = module
  for l in layer:
    if hasattr(module2, l):
      if not l.isdigit():
        module2 = getattr(module2, l)
      else:
        module2 = module2[int(l)]
      lst_index += 1
  lst_index -= 1
  for l in layer[:lst_index]:
    if not l.isdigit():
      module = getattr(module, l)
    else:
      module = module[int(l)]
  l = layer[lst_index]
  setattr(module, l, val)


def adapt_model_from_string(parent_module, model_string):
  separator = '***'
  state_dict = {}
  lst_shape = model_string.split(separator)
  for k in lst_shape:
    k = k.split(':')
    key = k[0]
    shape = k[1][1:-1].split(',')
    if shape[0] != '':
      state_dict[key] = [int(i) for i in shape]

  new_module = deepcopy(parent_module)
  for n, m in parent_module.named_modules():
    old_module = extract_layer(parent_module, n)
    if isinstance(old_module, nn.Conv2d) or isinstance(old_module, SameConv2d):
      if isinstance(old_module, SameConv2d):
        conv = SameConv2d
      else:
        conv = nn.Conv2d
      s = state_dict[n + '.weight']
      in_channels = s[1]
      out_channels = s[0]
      g = 1
      if old_module.groups > 1:
        in_channels = out_channels
        g = in_channels
      new_conv = conv(
          in_channels=in_channels, out_channels=out_channels, kernel_size=old_module.kernel_size,
          bias=old_module.bias is not None, padding=old_module.padding, dilation=old_module.dilation,
          groups=g, stride=old_module.stride)
      set_layer(new_module, n, new_conv)
    if isinstance(old_module, nn.BatchNorm2d):
      new_bn = nn.BatchNorm2d(
          num_features=state_dict[n + '.weight'][0], eps=old_module.eps, momentum=old_module.momentum,
          affine=old_module.affine, track_running_stats=True)
      set_layer(new_module, n, new_bn)
    if isinstance(old_module, nn.Linear):
      # FIXME extra checks to ensure this is actually the FC classifier layer and not a diff Linear layer?
      num_features = state_dict[n + '.weight'][1]
      new_fc = nn.Linear(
          in_features=num_features, out_features=old_module.out_features, bias=old_module.bias is not None)
      set_layer(new_module, n, new_fc)
      if hasattr(new_module, 'num_features'):
        new_module.num_features = num_features
  new_module.eval()
  parent_module.eval()

  return new_module


def adapt_model_from_file(parent_module, model_variant):
  adapt_file = os.path.join(os.path.dirname(__file__), 'pruned', model_variant + '.txt')
  with open(adapt_file, 'r') as f:
    return adapt_model_from_string(parent_module, f.read().strip())


def default_cfg_for_features(default_cfg):
  default_cfg = deepcopy(default_cfg)
  # remove default pretrained cfg fields that don't have much relevance for feature backbone
  to_remove = ('num_classes', 'crop_pct', 'classifier', 'global_pool')  # add default final pool size?
  for tr in to_remove:
    default_cfg.pop(tr, None)
  return default_cfg


def overlay_external_default_cfg(default_cfg, kwargs):
  """ Overlay 'external_default_cfg' in kwargs on top of default_cfg arg.
  """
  external_default_cfg = kwargs.pop('external_default_cfg', None)
  if external_default_cfg:
    default_cfg.pop('url', None)  # url should come from external cfg
    default_cfg.pop('hf_hub', None)  # hf hub id should come from external cfg
    default_cfg.update(external_default_cfg)


def set_default_kwargs(kwargs, names, default_cfg):
  for n in names:
    # for legacy reasons, model __init__args uses img_size + in_chans as separate args while
    # default_cfg has one input_size=(C, H ,W) entry
    if n == 'img_size':
      input_size = default_cfg.get('input_size', None)
      if input_size is not None:
        assert len(input_size) == 3
        kwargs.setdefault(n, input_size[-2:])
    elif n == 'in_chans':
      input_size = default_cfg.get('input_size', None)
      if input_size is not None:
        assert len(input_size) == 3
        kwargs.setdefault(n, input_size[0])
    else:
      default_val = default_cfg.get(n, None)
      if default_val is not None:
        kwargs.setdefault(n, default_cfg[n])


def filter_kwargs(kwargs, names):
  if not kwargs or not names:
    return
  for n in names:
    kwargs.pop(n, None)


def update_default_cfg_and_kwargs(default_cfg, kwargs, kwargs_filter):
  """ Update the default_cfg and kwargs before passing to model

  FIXME this sequence of overlay default_cfg, set default kwargs, filter kwargs
  could/should be replaced by an improved configuration mechanism

  Args:
      default_cfg: input default_cfg (updated in-place)
      kwargs: keyword args passed to model build fn (updated in-place)
      kwargs_filter: keyword arg keys that must be removed before model __init__
  """
  # Overlay default cfg values from `external_default_cfg` if it exists in kwargs
  overlay_external_default_cfg(default_cfg, kwargs)
  # Set model __init__ args that can be determined by default_cfg (if not already passed as kwargs)
  default_kwarg_names = ('num_classes', 'global_pool', 'in_chans')
  if default_cfg.get('fixed_input_size', False):
    # if fixed_input_size exists and is True, model takes an img_size arg that fixes its input size
    default_kwarg_names += ('img_size',)
  set_default_kwargs(kwargs, names=default_kwarg_names, default_cfg=default_cfg)
  # Filter keyword args for task specific model variants (some 'features only' models, etc.)
  filter_kwargs(kwargs, names=kwargs_filter)


def build_model_with_cfg(
        model_cls: Callable,
        variant: str,
        pretrained: bool,
        default_cfg: dict,
        model_cfg: Optional[Any] = None,
        feature_cfg: Optional[dict] = None,
        pretrained_strict: bool = True,
        pretrained_filter_fn: Optional[Callable] = None,
        pretrained_custom_load: bool = False,
        kwargs_filter: Optional[Tuple[str]] = None,
        **kwargs):
  """ Build model with specified default_cfg and optional model_cfg

  This helper fn aids in the construction of a model including:
    * handling default_cfg and associated pretained weight loading
    * passing through optional model_cfg for models with config based arch spec
    * features_only model adaptation
    * pruning config / model adaptation

  Args:
      model_cls (nn.Module): model class
      variant (str): model variant name
      pretrained (bool): load pretrained weights
      default_cfg (dict): model's default pretrained/task config
      model_cfg (Optional[Dict]): model's architecture config
      feature_cfg (Optional[Dict]: feature extraction adapter config
      pretrained_strict (bool): load pretrained weights strictly
      pretrained_filter_fn (Optional[Callable]): filter callable for pretrained weights
      pretrained_custom_load (bool): use custom load fn, to load numpy or other non PyTorch weights
      kwargs_filter (Optional[Tuple]): kwargs to filter before passing to model
      **kwargs: model args passed through to model __init__
  """
  pruned = kwargs.pop('pruned', False)
  features = False
  feature_cfg = feature_cfg or {}
  default_cfg = deepcopy(default_cfg) if default_cfg else {}
  update_default_cfg_and_kwargs(default_cfg, kwargs, kwargs_filter)
  default_cfg.setdefault('architecture', variant)

  # Setup for feature extraction wrapper done at end of this fn
  if kwargs.pop('features_only', False):
    features = True
    feature_cfg.setdefault('out_indices', (0, 1, 2, 3, 4))
    if 'out_indices' in kwargs:
      feature_cfg['out_indices'] = kwargs.pop('out_indices')

  # Build the model
  model = model_cls(**kwargs) if model_cfg is None else model_cls(cfg=model_cfg, **kwargs)
  model.default_cfg = default_cfg

  if pruned:
    model = adapt_model_from_file(model, variant)

  # For classification models, check class attr, then kwargs, then default to 1k, otherwise 0 for feats
  num_classes_pretrained = 0 if features else getattr(model, 'num_classes', kwargs.get('num_classes', 1000))
  if pretrained:
    if pretrained_custom_load:
      load_custom_pretrained(model)
    else:
      load_pretrained(
          model,
          num_classes=num_classes_pretrained,
          in_chans=kwargs.get('in_chans', 3),
          filter_fn=pretrained_filter_fn,
          strict=pretrained_strict)

  return model


def model_parameters(model, exclude_head=False):
  if exclude_head:
    # FIXME this a bit of a quick and dirty hack to skip classifier head params based on ordering
    return [p for p in model.parameters()][:-2]
  else:
    return model.parameters()


def named_apply(fn: Callable, module: nn.Module, name='', depth_first=True, include_root=False) -> nn.Module:
  if not depth_first and include_root:
    fn(module=module, name=name)
  for child_name, child_module in module.named_children():
    child_name = '.'.join((name, child_name)) if name else child_name
    named_apply(fn=fn, module=child_module, name=child_name, depth_first=depth_first, include_root=True)
  if depth_first and include_root:
    fn(module=module, name=name)
  return module


def named_modules(module: nn.Module, name='', depth_first=True, include_root=False):
  if not depth_first and include_root:
    yield name, module
  for child_name, child_module in module.named_children():
    child_name = '.'.join((name, child_name)) if name else child_name
    yield from named_modules(
        module=child_module, name=child_name, depth_first=depth_first, include_root=True)
  if depth_first and include_root:
    yield name, module


def _get_bn_args_tf():
  return _BN_ARGS_TF.copy()


def resolve_bn_args(kwargs):
  bn_args = _get_bn_args_tf() if kwargs.pop('bn_tf', False) else {}
  bn_momentum = kwargs.pop('bn_momentum', None)
  if bn_momentum is not None:
    bn_args['momentum'] = bn_momentum
  bn_eps = kwargs.pop('bn_eps', None)
  if bn_eps is not None:
    bn_args['eps'] = bn_eps
  return bn_args


def resolve_act_layer(kwargs, name='relu'):
  return dict(
      silu=tw.nn.Swish,
      swish=tw.nn.Swish,
      # mish=nn.Mish,
      relu=nn.ReLU,
      relu6=nn.ReLU6,
      leaky_relu=nn.LeakyReLU,
      elu=nn.ELU,
      prelu=nn.PReLU,
      celu=nn.CELU,
      selu=nn.SELU,
      gelu=nn.GELU,
      sigmoid=torch.sigmoid,
      tanh=torch.tanh,
      hard_sigmoid=nn.Hardsigmoid,
      hard_swish=nn.Hardswish,
      # hard_mish=HardMish,
  )[name]


class EfficientNetBuilder:
  """Build Trunk Blocks

  This ended up being somewhat of a cross between

  https://github.com/tensorflow/tpu/blob/master/models/official/mnasnet/mnasnet_models.py
  and
  https://github.com/facebookresearch/maskrcnn-benchmark/blob/master/maskrcnn_benchmark/modeling/backbone/fbnet_builder.py

  """

  def __init__(self, output_stride=32, pad_type='', round_chs_fn=tw.nn.conv._round_channels, se_from_exp=False,
               act_layer=None, norm_layer=None, se_layer=None, drop_path_rate=0., feature_location=''):
    self.output_stride = output_stride
    self.pad_type = pad_type
    self.round_chs_fn = round_chs_fn
    self.se_from_exp = se_from_exp  # calculate se channel reduction from expanded (mid) chs
    self.act_layer = act_layer
    self.norm_layer = norm_layer

    self.se_layer = se_layer
    try:
      self.se_layer(8, rd_ratio=1.0)  # test if attn layer accepts rd_ratio arg
      self.se_has_ratio = True
    except TypeError:
      self.se_has_ratio = False
    self.drop_path_rate = drop_path_rate

    if feature_location == 'depthwise':
      # old 'depthwise' mode renamed 'expansion' to match TF impl, old expansion mode didn't make sense
      tw.logger.warn("feature_location=='depthwise' is deprecated, using 'expansion'")
      feature_location = 'expansion'
    self.feature_location = feature_location
    assert feature_location in ('bottleneck', 'expansion', '')

    # state updated during build, consumed by model
    self.in_chs = None
    self.features = []

  def _make_block(self, ba, block_idx, block_count):
    drop_path_rate = self.drop_path_rate * block_idx / block_count
    bt = ba.pop('block_type')
    ba['in_chs'] = self.in_chs
    ba['out_chs'] = self.round_chs_fn(ba['out_chs'])
    if 'force_in_chs' in ba and ba['force_in_chs']:
      # NOTE this is a hack to work around mismatch in TF EdgeEffNet impl
      ba['force_in_chs'] = self.round_chs_fn(ba['force_in_chs'])
    ba['pad_type'] = self.pad_type
    # block act fn overrides the model default
    ba['act_layer'] = ba['act_layer'] if ba['act_layer'] is not None else self.act_layer
    assert ba['act_layer'] is not None
    ba['norm_layer'] = self.norm_layer
    ba['drop_path_rate'] = drop_path_rate
    if bt != 'cn':
      se_ratio = ba.pop('se_ratio')
      if se_ratio and self.se_layer is not None:
        if not self.se_from_exp:
          # adjust se_ratio by expansion ratio if calculating se channels from block input
          se_ratio /= ba.get('exp_ratio', 1.0)
        if self.se_has_ratio:
          ba['se_layer'] = partial(self.se_layer, rd_ratio=se_ratio)
        else:
          ba['se_layer'] = self.se_layer

    if bt == 'ir':
      # tw.logger.info('  InvertedResidual {}, Args: {}'.format(block_idx, str(ba)))
      block = tw.nn.CondConvResidual(**ba) if ba.get('num_experts', 0) else tw.nn.InvertedResidual(**ba)
    elif bt == 'ds' or bt == 'dsa':
      # tw.logger.info('  DepthwiseSeparable {}, Args: {}'.format(block_idx, str(ba)))
      block = tw.nn.DepthwiseSeparableConv(**ba)
    elif bt == 'er':
      # tw.logger.info('  EdgeResidual {}, Args: {}'.format(block_idx, str(ba)))
      block = tw.nn.EdgeResidual(**ba)
    elif bt == 'cn':
      # tw.logger.info('  ConvBnAct {}, Args: {}'.format(block_idx, str(ba)))
      block = tw.nn.ConvBnAct(**ba)
    else:
      assert False, 'Uknkown block type (%s) while building model.' % bt

    self.in_chs = ba['out_chs']  # update in_chs for arg of next block
    return block

  def __call__(self, in_chs, model_block_args):
    """ Build the blocks
    Args:
        in_chs: Number of input-channels passed to first block
        model_block_args: A list of lists, outer list defines stages, inner
            list contains strings defining block configuration(s)
    Return:
         List of block stacks (each stack wrapped in nn.Sequential)
    """
    # tw.logger.info('Building model trunk with %d stages...' % len(model_block_args))
    self.in_chs = in_chs
    total_block_count = sum([len(x) for x in model_block_args])
    total_block_idx = 0
    current_stride = 2
    current_dilation = 1
    stages = []
    if model_block_args[0][0]['stride'] > 1:
      # if the first block starts with a stride, we need to extract first level feat from stem
      feature_info = dict(
          module='act1', num_chs=in_chs, stage=0, reduction=current_stride,
          hook_type='forward' if self.feature_location != 'bottleneck' else '')
      self.features.append(feature_info)

    # outer list of block_args defines the stacks
    for stack_idx, stack_args in enumerate(model_block_args):
      last_stack = stack_idx + 1 == len(model_block_args)
      # tw.logger.info('Stack: {}'.format(stack_idx))
      assert isinstance(stack_args, list)

      blocks = []
      # each stack (stage of blocks) contains a list of block arguments
      for block_idx, block_args in enumerate(stack_args):
        last_block = block_idx + 1 == len(stack_args)
        # tw.logger.info(' Block: {}'.format(block_idx))

        assert block_args['stride'] in (1, 2)
        if block_idx >= 1:   # only the first block in any stack can have a stride > 1
          block_args['stride'] = 1

        extract_features = False
        if last_block:
          next_stack_idx = stack_idx + 1
          extract_features = next_stack_idx >= len(model_block_args) or \
              model_block_args[next_stack_idx][0]['stride'] > 1

        next_dilation = current_dilation
        if block_args['stride'] > 1:
          next_output_stride = current_stride * block_args['stride']
          if next_output_stride > self.output_stride:
            next_dilation = current_dilation * block_args['stride']
            block_args['stride'] = 1
            tw.logger.info('  Converting stride to dilation to maintain output_stride=={}'.format(
                self.output_stride))
          else:
            current_stride = next_output_stride
        block_args['dilation'] = current_dilation
        if next_dilation != current_dilation:
          current_dilation = next_dilation

        # create the block
        block = self._make_block(block_args, total_block_idx, total_block_count)
        blocks.append(block)

        # stash feature module name and channel info for model feature extraction
        if extract_features:
          feature_info = dict(
              stage=stack_idx + 1, reduction=current_stride, **block.feature_info(self.feature_location))
          module_name = f'blocks.{stack_idx}.{block_idx}'
          leaf_name = feature_info.get('module', '')
          feature_info['module'] = '.'.join([module_name, leaf_name]) if leaf_name else module_name
          self.features.append(feature_info)

        total_block_idx += 1  # incr global block idx (across all stacks)
      stages.append(nn.Sequential(*blocks))
    return stages


def _init_weight_google(m, n='', fix_group_fanout=True):
  """ Weight initialization as per Tensorflow official implementations.

  Args:
      m (nn.Module): module to init
      n (str): module name
      fix_group_fanout (bool): enable correct (matching Tensorflow TPU impl) fanout calculation w/ group convs

    Handles layers in EfficientNet, EfficientNet-CondConv, MixNet, MnasNet, MobileNetV3, etc:
    * https://github.com/tensorflow/tpu/blob/master/models/official/mnasnet/mnasnet_model.py
    * https://github.com/tensorflow/tpu/blob/master/models/official/efficientnet/efficientnet_model.py

  """
  if isinstance(m, tw.nn.CondConv2d):
    fan_out = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
    if fix_group_fanout:
      fan_out //= m.groups
    init_weight_fn = tw.nn.conv._get_condconv_initializer(
        lambda w: nn.init.normal_(w, 0, math.sqrt(2.0 / fan_out)), m.num_experts, m.weight_shape)
    init_weight_fn(m.weight)
    if m.bias is not None:
      nn.init.zeros_(m.bias)
  elif isinstance(m, nn.Conv2d):
    fan_out = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
    if fix_group_fanout:
      fan_out //= m.groups
    nn.init.normal_(m.weight, 0, math.sqrt(2.0 / fan_out))
    if m.bias is not None:
      nn.init.zeros_(m.bias)
  elif isinstance(m, nn.BatchNorm2d):
    nn.init.ones_(m.weight)
    nn.init.zeros_(m.bias)
  elif isinstance(m, nn.Linear):
    fan_out = m.weight.size(0)  # fan-out
    fan_in = 0
    if 'routing_fn' in n:
      fan_in = m.weight.size(1)
    init_range = 1.0 / math.sqrt(fan_in + fan_out)
    nn.init.uniform_(m.weight, -init_range, init_range)
    nn.init.zeros_(m.bias)


def efficientnet_init_weights(model: nn.Module, init_fn=None):
  init_fn = init_fn or _init_weight_google
  for n, m in model.named_modules():
    init_fn(m, n)


class EfficientNet(nn.Module):
  """ (Generic) EfficientNet

  A flexible and performant PyTorch implementation of efficient network architectures, including:
    * EfficientNet-V2 Small, Medium, Large & B0-B3
    * EfficientNet B0-B8, L2
    * EfficientNet-EdgeTPU
    * EfficientNet-CondConv
    * MixNet S, M, L, XL
    * MnasNet A1, B1, and small
    * FBNet C
    * Single-Path NAS Pixel1

  """

  MEAN = [0.485, 0.456, 0.406]
  STD = [0.229, 0.224, 0.225]
  SIZE = [224, 224]
  SCALE = 255
  CROP = 0.875

  def __init__(self, block_args, num_classes=1000, num_features=1280, in_chans=3, stem_size=32, fix_stem=False,
               output_stride=32, pad_type='', round_chs_fn=round_channels, act_layer=None, norm_layer=None,
               se_layer=None, drop_rate=0., drop_path_rate=0., global_pool='avg', output_backbone=False):
    super(EfficientNet, self).__init__()
    act_layer = act_layer or nn.ReLU
    norm_layer = norm_layer or nn.BatchNorm2d
    se_layer = se_layer or SqueezeExcite
    self.num_classes = num_classes
    self.num_features = num_features
    self.drop_rate = drop_rate
    self.output_backbone = output_backbone

    # Stem
    if not fix_stem:
      stem_size = round_chs_fn(stem_size)
    self.conv_stem = create_conv2d(in_chans, stem_size, 3, stride=2, padding=pad_type)
    self.bn1 = norm_layer(stem_size)
    self.act1 = act_layer()

    # Middle stages (IR/ER/DS Blocks)
    builder = EfficientNetBuilder(
        output_stride=output_stride, pad_type=pad_type, round_chs_fn=round_chs_fn,
        act_layer=act_layer, norm_layer=norm_layer, se_layer=se_layer, drop_path_rate=drop_path_rate)
    self.blocks = nn.Sequential(*builder(stem_size, block_args))
    self.feature_info = builder.features
    head_chs = builder.in_chs

    # Head + Pooling
    self.conv_head = create_conv2d(head_chs, self.num_features, 1, padding=pad_type)
    self.bn2 = norm_layer(self.num_features)
    self.act2 = act_layer()

    # self.global_pool, self.classifier = create_classifier(
    #     self.num_features, self.num_classes, pool_type=global_pool)

    # Head + Pooling
    coeff = 1
    if global_pool == 'avg':
      self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
    elif global_pool == 'max':
      self.global_pool = nn.AdaptiveMaxPool2d((1, 1))
    elif global_pool == 'avgmax':
      self.global_pool = tw.nn.AdaptiveAvgMaxPool2d(1)
    elif global_pool == 'catavgam':
      self.global_pool = tw.nn.AdaptiveCatAvgMaxPool2d(1)
      coeff = 2
    else:
      raise NotImplementedError(global_pool)

    self.flatten = nn.Flatten(1) if global_pool else nn.Identity()

    # build fc
    if num_classes <= 0:
      self.classifier = nn.Identity()
    else:
      self.classifier = nn.Linear(self.num_features * coeff, num_classes)

    efficientnet_init_weights(self)

  def as_sequential(self):
    layers = [self.conv_stem, self.bn1, self.act1]
    layers.extend(self.blocks)
    layers.extend([self.conv_head, self.bn2, self.act2, self.global_pool])
    layers.extend([nn.Dropout(self.drop_rate), self.classifier])
    return nn.Sequential(*layers)

  def get_classifier(self):
    return self.classifier

  def reset_classifier(self, num_classes, global_pool='avg'):
    self.num_classes = num_classes
    self.global_pool, self.classifier = create_classifier(
        self.num_features, self.num_classes, pool_type=global_pool)

  def forward_features(self, x):
    x = self.conv_stem(x)
    x = self.bn1(x)
    x = self.act1(x)
    x = self.blocks(x)
    x = self.conv_head(x)
    x = self.bn2(x)
    x = self.act2(x)
    return x

  def forward(self, x):
    x = self.forward_features(x)
    if self.output_backbone:
      return x, x, x, x
    x = self.global_pool(x)
    x = self.flatten(x)
    if self.drop_rate > 0.:
      x = F.dropout(x, p=self.drop_rate, training=self.training)
    return self.classifier(x)


class EfficientNetFeatures(nn.Module):
  """ EfficientNet Feature Extractor

  A work-in-progress feature extraction module for EfficientNet, to use as a backbone for segmentation
  and object detection models.
  """

  def __init__(self, block_args, out_indices=(0, 1, 2, 3, 4), feature_location='bottleneck', in_chans=3,
               stem_size=32, fix_stem=False, output_stride=32, pad_type='', round_chs_fn=round_channels,
               act_layer=None, norm_layer=None, se_layer=None, drop_rate=0., drop_path_rate=0.):
    super(EfficientNetFeatures, self).__init__()
    act_layer = act_layer or nn.ReLU
    norm_layer = norm_layer or nn.BatchNorm2d
    se_layer = se_layer or SqueezeExcite
    self.drop_rate = drop_rate

    # Stem
    if not fix_stem:
      stem_size = round_chs_fn(stem_size)
    self.conv_stem = create_conv2d(in_chans, stem_size, 3, stride=2, padding=pad_type)
    self.bn1 = norm_layer(stem_size)
    self.act1 = act_layer()

    # Middle stages (IR/ER/DS Blocks)
    builder = EfficientNetBuilder(
        output_stride=output_stride, pad_type=pad_type, round_chs_fn=round_chs_fn,
        act_layer=act_layer, norm_layer=norm_layer, se_layer=se_layer, drop_path_rate=drop_path_rate,
        feature_location=feature_location)
    self.blocks = nn.Sequential(*builder(stem_size, block_args))
    self.feature_info = FeatureInfo(builder.features, out_indices)
    self._stage_out_idx = {v['stage']: i for i, v in enumerate(self.feature_info) if i in out_indices}

    efficientnet_init_weights(self)

    # Register feature extraction hooks with FeatureHooks helper
    self.feature_hooks = None
    if feature_location != 'bottleneck':
      hooks = self.feature_info.get_dicts(keys=('module', 'hook_type'))
      self.feature_hooks = FeatureHooks(hooks, self.named_modules())

  def forward(self, x):
    x = self.conv_stem(x)
    x = self.bn1(x)
    x = self.act1(x)
    if self.feature_hooks is None:
      features = []
      if 0 in self._stage_out_idx:
        features.append(x)  # add stem out
      for i, b in enumerate(self.blocks):
        x = b(x)
        if i + 1 in self._stage_out_idx:
          features.append(x)
      return features
    else:
      self.blocks(x)
      out = self.feature_hooks.get_output(x.device)
      return list(out.values())


def _create_effnet(variant, pretrained=False, **kwargs):
  features_only = False
  model_cls = EfficientNet
  kwargs_filter = None
  if kwargs.pop('features_only', False):
    features_only = True
    kwargs_filter = ('num_classes', 'num_features', 'head_conv', 'global_pool')
    model_cls = EfficientNetFeatures
  model = build_model_with_cfg(
      model_cls, variant, pretrained,
      default_cfg=default_cfgs[variant],
      pretrained_strict=not features_only,
      kwargs_filter=kwargs_filter,
      **kwargs)
  if features_only:
    model.default_cfg = default_cfg_for_features(model.default_cfg)
  return model


def _gen_mnasnet_a1(variant, channel_multiplier=1.0, pretrained=False, **kwargs):
  """Creates a mnasnet-a1 model.

  Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet
  Paper: https://arxiv.org/pdf/1807.11626.pdf.

  Args:
    channel_multiplier: multiplier to number of channels per layer.
  """
  arch_def = [
      # stage 0, 112x112 in
      ['ds_r1_k3_s1_e1_c16_noskip'],
      # stage 1, 112x112 in
      ['ir_r2_k3_s2_e6_c24'],
      # stage 2, 56x56 in
      ['ir_r3_k5_s2_e3_c40_se0.25'],
      # stage 3, 28x28 in
      ['ir_r4_k3_s2_e6_c80'],
      # stage 4, 14x14in
      ['ir_r2_k3_s1_e6_c112_se0.25'],
      # stage 5, 14x14in
      ['ir_r3_k5_s2_e6_c160_se0.25'],
      # stage 6, 7x7 in
      ['ir_r1_k3_s1_e6_c320'],
  ]
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def),
      stem_size=32,
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      **kwargs
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_mnasnet_b1(variant, channel_multiplier=1.0, pretrained=False, **kwargs):
  """Creates a mnasnet-b1 model.

  Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet
  Paper: https://arxiv.org/pdf/1807.11626.pdf.

  Args:
    channel_multiplier: multiplier to number of channels per layer.
  """
  arch_def = [
      # stage 0, 112x112 in
      ['ds_r1_k3_s1_c16_noskip'],
      # stage 1, 112x112 in
      ['ir_r3_k3_s2_e3_c24'],
      # stage 2, 56x56 in
      ['ir_r3_k5_s2_e3_c40'],
      # stage 3, 28x28 in
      ['ir_r3_k5_s2_e6_c80'],
      # stage 4, 14x14in
      ['ir_r2_k3_s1_e6_c96'],
      # stage 5, 14x14in
      ['ir_r4_k5_s2_e6_c192'],
      # stage 6, 7x7 in
      ['ir_r1_k3_s1_e6_c320_noskip']
  ]
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def),
      stem_size=32,
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      **kwargs
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_mnasnet_small(variant, channel_multiplier=1.0, pretrained=False, **kwargs):
  """Creates a mnasnet-b1 model.

  Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet
  Paper: https://arxiv.org/pdf/1807.11626.pdf.

  Args:
    channel_multiplier: multiplier to number of channels per layer.
  """
  arch_def = [
      ['ds_r1_k3_s1_c8'],
      ['ir_r1_k3_s2_e3_c16'],
      ['ir_r2_k3_s2_e6_c16'],
      ['ir_r4_k5_s2_e6_c32_se0.25'],
      ['ir_r3_k3_s1_e6_c32_se0.25'],
      ['ir_r3_k5_s2_e6_c88_se0.25'],
      ['ir_r1_k3_s1_e6_c144']
  ]
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def),
      stem_size=8,
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      **kwargs
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_mobilenet_v2(
        variant, channel_multiplier=1.0, depth_multiplier=1.0, fix_stem_head=False, pretrained=False, **kwargs):
  """ Generate MobileNet-V2 network
  Ref impl: https://github.com/tensorflow/models/blob/master/research/slim/nets/mobilenet/mobilenet_v2.py
  Paper: https://arxiv.org/abs/1801.04381
  """
  arch_def = [
      ['ds_r1_k3_s1_c16'],
      ['ir_r2_k3_s2_e6_c24'],
      ['ir_r3_k3_s2_e6_c32'],
      ['ir_r4_k3_s2_e6_c64'],
      ['ir_r3_k3_s1_e6_c96'],
      ['ir_r3_k3_s2_e6_c160'],
      ['ir_r1_k3_s1_e6_c320'],
  ]
  round_chs_fn = partial(round_channels, multiplier=channel_multiplier)
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier=depth_multiplier, fix_first_last=fix_stem_head),
      num_features=1280 if fix_stem_head else round_chs_fn(1280),
      stem_size=32,
      fix_stem=fix_stem_head,
      round_chs_fn=round_chs_fn,
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      act_layer=resolve_act_layer(kwargs, 'relu6'),
      **kwargs
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_fbnetc(variant, channel_multiplier=1.0, pretrained=False, **kwargs):
  """ FBNet-C

      Paper: https://arxiv.org/abs/1812.03443
      Ref Impl: https://github.com/facebookresearch/maskrcnn-benchmark/blob/master/maskrcnn_benchmark/modeling/backbone/fbnet_modeldef.py

      NOTE: the impl above does not relate to the 'C' variant here, that was derived from paper,
      it was used to confirm some building block details
  """
  arch_def = [
      ['ir_r1_k3_s1_e1_c16'],
      ['ir_r1_k3_s2_e6_c24', 'ir_r2_k3_s1_e1_c24'],
      ['ir_r1_k5_s2_e6_c32', 'ir_r1_k5_s1_e3_c32', 'ir_r1_k5_s1_e6_c32', 'ir_r1_k3_s1_e6_c32'],
      ['ir_r1_k5_s2_e6_c64', 'ir_r1_k5_s1_e3_c64', 'ir_r2_k5_s1_e6_c64'],
      ['ir_r3_k5_s1_e6_c112', 'ir_r1_k5_s1_e3_c112'],
      ['ir_r4_k5_s2_e6_c184'],
      ['ir_r1_k3_s1_e6_c352'],
  ]
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def),
      stem_size=16,
      num_features=1984,  # paper suggests this, but is not 100% clear
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      **kwargs
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_spnasnet(variant, channel_multiplier=1.0, pretrained=False, **kwargs):
  """Creates the Single-Path NAS model from search targeted for Pixel1 phone.

  Paper: https://arxiv.org/abs/1904.02877

  Args:
    channel_multiplier: multiplier to number of channels per layer.
  """
  arch_def = [
      # stage 0, 112x112 in
      ['ds_r1_k3_s1_c16_noskip'],
      # stage 1, 112x112 in
      ['ir_r3_k3_s2_e3_c24'],
      # stage 2, 56x56 in
      ['ir_r1_k5_s2_e6_c40', 'ir_r3_k3_s1_e3_c40'],
      # stage 3, 28x28 in
      ['ir_r1_k5_s2_e6_c80', 'ir_r3_k3_s1_e3_c80'],
      # stage 4, 14x14in
      ['ir_r1_k5_s1_e6_c96', 'ir_r3_k5_s1_e3_c96'],
      # stage 5, 14x14in
      ['ir_r4_k5_s2_e6_c192'],
      # stage 6, 7x7 in
      ['ir_r1_k3_s1_e6_c320_noskip']
  ]
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def),
      stem_size=32,
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      **kwargs
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_efficientnet(variant, channel_multiplier=1.0, depth_multiplier=1.0, pretrained=False, **kwargs):
  """Creates an EfficientNet model.

  Ref impl: https://github.com/tensorflow/tpu/blob/master/models/official/efficientnet/efficientnet_model.py
  Paper: https://arxiv.org/abs/1905.11946

  EfficientNet params
  name: (channel_multiplier, depth_multiplier, resolution, dropout_rate)
  'efficientnet-b0': (1.0, 1.0, 224, 0.2),
  'efficientnet-b1': (1.0, 1.1, 240, 0.2),
  'efficientnet-b2': (1.1, 1.2, 260, 0.3),
  'efficientnet-b3': (1.2, 1.4, 300, 0.3),
  'efficientnet-b4': (1.4, 1.8, 380, 0.4),
  'efficientnet-b5': (1.6, 2.2, 456, 0.4),
  'efficientnet-b6': (1.8, 2.6, 528, 0.5),
  'efficientnet-b7': (2.0, 3.1, 600, 0.5),
  'efficientnet-b8': (2.2, 3.6, 672, 0.5),
  'efficientnet-l2': (4.3, 5.3, 800, 0.5),

  Args:
    channel_multiplier: multiplier to number of channels per layer
    depth_multiplier: multiplier to number of repeats per stage

  """
  arch_def = [
      ['ds_r1_k3_s1_e1_c16_se0.25'],
      ['ir_r2_k3_s2_e6_c24_se0.25'],
      ['ir_r2_k5_s2_e6_c40_se0.25'],
      ['ir_r3_k3_s2_e6_c80_se0.25'],
      ['ir_r3_k5_s1_e6_c112_se0.25'],
      ['ir_r4_k5_s2_e6_c192_se0.25'],
      ['ir_r1_k3_s1_e6_c320_se0.25'],
  ]
  round_chs_fn = partial(round_channels, multiplier=channel_multiplier)
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier),
      num_features=round_chs_fn(1280),
      stem_size=32,
      round_chs_fn=round_chs_fn,
      act_layer=resolve_act_layer(kwargs, 'swish'),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      **kwargs,
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_efficientnet_edge(variant, channel_multiplier=1.0, depth_multiplier=1.0, pretrained=False, **kwargs):
  """ Creates an EfficientNet-EdgeTPU model

  Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/efficientnet/edgetpu
  """

  arch_def = [
      # NOTE `fc` is present to override a mismatch between stem channels and in chs not
      # present in other models
      ['er_r1_k3_s1_e4_c24_fc24_noskip'],
      ['er_r2_k3_s2_e8_c32'],
      ['er_r4_k3_s2_e8_c48'],
      ['ir_r5_k5_s2_e8_c96'],
      ['ir_r4_k5_s1_e8_c144'],
      ['ir_r2_k5_s2_e8_c192'],
  ]
  round_chs_fn = partial(round_channels, multiplier=channel_multiplier)
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier),
      num_features=round_chs_fn(1280),
      stem_size=32,
      round_chs_fn=round_chs_fn,
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      act_layer=resolve_act_layer(kwargs, 'relu'),
      **kwargs,
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_efficientnet_condconv(
        variant, channel_multiplier=1.0, depth_multiplier=1.0, experts_multiplier=1, pretrained=False, **kwargs):
  """Creates an EfficientNet-CondConv model.

  Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/efficientnet/condconv
  """
  arch_def = [
      ['ds_r1_k3_s1_e1_c16_se0.25'],
      ['ir_r2_k3_s2_e6_c24_se0.25'],
      ['ir_r2_k5_s2_e6_c40_se0.25'],
      ['ir_r3_k3_s2_e6_c80_se0.25'],
      ['ir_r3_k5_s1_e6_c112_se0.25_cc4'],
      ['ir_r4_k5_s2_e6_c192_se0.25_cc4'],
      ['ir_r1_k3_s1_e6_c320_se0.25_cc4'],
  ]
  # NOTE unlike official impl, this one uses `cc<x>` option where x is the base number of experts for each stage and
  # the expert_multiplier increases that on a per-model basis as with depth/channel multipliers
  round_chs_fn = partial(round_channels, multiplier=channel_multiplier)
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier, experts_multiplier=experts_multiplier),
      num_features=round_chs_fn(1280),
      stem_size=32,
      round_chs_fn=round_chs_fn,
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      act_layer=resolve_act_layer(kwargs, 'swish'),
      **kwargs,
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_efficientnet_lite(variant, channel_multiplier=1.0, depth_multiplier=1.0, pretrained=False, **kwargs):
  """Creates an EfficientNet-Lite model.

  Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/efficientnet/lite
  Paper: https://arxiv.org/abs/1905.11946

  EfficientNet params
  name: (channel_multiplier, depth_multiplier, resolution, dropout_rate)
    'efficientnet-lite0': (1.0, 1.0, 224, 0.2),
    'efficientnet-lite1': (1.0, 1.1, 240, 0.2),
    'efficientnet-lite2': (1.1, 1.2, 260, 0.3),
    'efficientnet-lite3': (1.2, 1.4, 280, 0.3),
    'efficientnet-lite4': (1.4, 1.8, 300, 0.3),

  Args:
    channel_multiplier: multiplier to number of channels per layer
    depth_multiplier: multiplier to number of repeats per stage
  """
  arch_def = [
      ['ds_r1_k3_s1_e1_c16'],
      ['ir_r2_k3_s2_e6_c24'],
      ['ir_r2_k5_s2_e6_c40'],
      ['ir_r3_k3_s2_e6_c80'],
      ['ir_r3_k5_s1_e6_c112'],
      ['ir_r4_k5_s2_e6_c192'],
      ['ir_r1_k3_s1_e6_c320'],
  ]
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier, fix_first_last=True),
      num_features=1280,
      stem_size=32,
      fix_stem=True,
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      act_layer=resolve_act_layer(kwargs, 'relu6'),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      **kwargs,
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_efficientnetv2_base(
        variant, channel_multiplier=1.0, depth_multiplier=1.0, pretrained=False, **kwargs):
  """ Creates an EfficientNet-V2 base model

  Ref impl: https://github.com/google/automl/tree/master/efficientnetv2
  Paper: `EfficientNetV2: Smaller Models and Faster Training` - https://arxiv.org/abs/2104.00298
  """
  arch_def = [
      ['cn_r1_k3_s1_e1_c16_skip'],
      ['er_r2_k3_s2_e4_c32'],
      ['er_r2_k3_s2_e4_c48'],
      ['ir_r3_k3_s2_e4_c96_se0.25'],
      ['ir_r5_k3_s1_e6_c112_se0.25'],
      ['ir_r8_k3_s2_e6_c192_se0.25'],
  ]
  round_chs_fn = partial(round_channels, multiplier=channel_multiplier, round_limit=0.)
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier),
      num_features=round_chs_fn(1280),
      stem_size=32,
      round_chs_fn=round_chs_fn,
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      act_layer=resolve_act_layer(kwargs, 'silu'),
      **kwargs,
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_efficientnetv2_s(
        variant, channel_multiplier=1.0, depth_multiplier=1.0, rw=False, pretrained=False, **kwargs):
  """ Creates an EfficientNet-V2 Small model

  Ref impl: https://github.com/google/automl/tree/master/efficientnetv2
  Paper: `EfficientNetV2: Smaller Models and Faster Training` - https://arxiv.org/abs/2104.00298

  NOTE: `rw` flag sets up 'small' variant to behave like my initial v2 small model,
      before ref the impl was released.
  """
  arch_def = [
      ['cn_r2_k3_s1_e1_c24_skip'],
      ['er_r4_k3_s2_e4_c48'],
      ['er_r4_k3_s2_e4_c64'],
      ['ir_r6_k3_s2_e4_c128_se0.25'],
      ['ir_r9_k3_s1_e6_c160_se0.25'],
      ['ir_r15_k3_s2_e6_c256_se0.25'],
  ]
  num_features = 1280
  if rw:
    # my original variant, based on paper figure differs from the official release
    arch_def[0] = ['er_r2_k3_s1_e1_c24']
    arch_def[-1] = ['ir_r15_k3_s2_e6_c272_se0.25']
    num_features = 1792

  round_chs_fn = partial(round_channels, multiplier=channel_multiplier)
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier),
      num_features=round_chs_fn(num_features),
      stem_size=24,
      round_chs_fn=round_chs_fn,
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      act_layer=resolve_act_layer(kwargs, 'silu'),
      **kwargs,
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_efficientnetv2_m(variant, channel_multiplier=1.0, depth_multiplier=1.0, pretrained=False, **kwargs):
  """ Creates an EfficientNet-V2 Medium model

  Ref impl: https://github.com/google/automl/tree/master/efficientnetv2
  Paper: `EfficientNetV2: Smaller Models and Faster Training` - https://arxiv.org/abs/2104.00298
  """

  arch_def = [
      ['cn_r3_k3_s1_e1_c24_skip'],
      ['er_r5_k3_s2_e4_c48'],
      ['er_r5_k3_s2_e4_c80'],
      ['ir_r7_k3_s2_e4_c160_se0.25'],
      ['ir_r14_k3_s1_e6_c176_se0.25'],
      ['ir_r18_k3_s2_e6_c304_se0.25'],
      ['ir_r5_k3_s1_e6_c512_se0.25'],
  ]

  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier),
      num_features=1280,
      stem_size=24,
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      act_layer=resolve_act_layer(kwargs, 'silu'),
      **kwargs,
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_efficientnetv2_l(variant, channel_multiplier=1.0, depth_multiplier=1.0, pretrained=False, **kwargs):
  """ Creates an EfficientNet-V2 Large model

  Ref impl: https://github.com/google/automl/tree/master/efficientnetv2
  Paper: `EfficientNetV2: Smaller Models and Faster Training` - https://arxiv.org/abs/2104.00298
  """

  arch_def = [
      ['cn_r4_k3_s1_e1_c32_skip'],
      ['er_r7_k3_s2_e4_c64'],
      ['er_r7_k3_s2_e4_c96'],
      ['ir_r10_k3_s2_e4_c192_se0.25'],
      ['ir_r19_k3_s1_e6_c224_se0.25'],
      ['ir_r25_k3_s2_e6_c384_se0.25'],
      ['ir_r7_k3_s1_e6_c640_se0.25'],
  ]

  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier),
      num_features=1280,
      stem_size=32,
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      act_layer=resolve_act_layer(kwargs, 'silu'),
      **kwargs,
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_mixnet_s(variant, channel_multiplier=1.0, pretrained=False, **kwargs):
  """Creates a MixNet Small model.

  Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet/mixnet
  Paper: https://arxiv.org/abs/1907.09595
  """
  arch_def = [
      # stage 0, 112x112 in
      ['ds_r1_k3_s1_e1_c16'],  # relu
      # stage 1, 112x112 in
      ['ir_r1_k3_a1.1_p1.1_s2_e6_c24', 'ir_r1_k3_a1.1_p1.1_s1_e3_c24'],  # relu
      # stage 2, 56x56 in
      ['ir_r1_k3.5.7_s2_e6_c40_se0.5_nsw', 'ir_r3_k3.5_a1.1_p1.1_s1_e6_c40_se0.5_nsw'],  # swish
      # stage 3, 28x28 in
      ['ir_r1_k3.5.7_p1.1_s2_e6_c80_se0.25_nsw', 'ir_r2_k3.5_p1.1_s1_e6_c80_se0.25_nsw'],  # swish
      # stage 4, 14x14in
      ['ir_r1_k3.5.7_a1.1_p1.1_s1_e6_c120_se0.5_nsw', 'ir_r2_k3.5.7.9_a1.1_p1.1_s1_e3_c120_se0.5_nsw'],  # swish
      # stage 5, 14x14in
      ['ir_r1_k3.5.7.9.11_s2_e6_c200_se0.5_nsw', 'ir_r2_k3.5.7.9_p1.1_s1_e6_c200_se0.5_nsw'],  # swish
      # 7x7
  ]
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def),
      num_features=1536,
      stem_size=16,
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      **kwargs
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def _gen_mixnet_m(variant, channel_multiplier=1.0, depth_multiplier=1.0, pretrained=False, **kwargs):
  """Creates a MixNet Medium-Large model.

  Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet/mixnet
  Paper: https://arxiv.org/abs/1907.09595
  """
  arch_def = [
      # stage 0, 112x112 in
      ['ds_r1_k3_s1_e1_c24'],  # relu
      # stage 1, 112x112 in
      ['ir_r1_k3.5.7_a1.1_p1.1_s2_e6_c32', 'ir_r1_k3_a1.1_p1.1_s1_e3_c32'],  # relu
      # stage 2, 56x56 in
      ['ir_r1_k3.5.7.9_s2_e6_c40_se0.5_nsw', 'ir_r3_k3.5_a1.1_p1.1_s1_e6_c40_se0.5_nsw'],  # swish
      # stage 3, 28x28 in
      ['ir_r1_k3.5.7_s2_e6_c80_se0.25_nsw', 'ir_r3_k3.5.7.9_a1.1_p1.1_s1_e6_c80_se0.25_nsw'],  # swish
      # stage 4, 14x14in
      ['ir_r1_k3_s1_e6_c120_se0.5_nsw', 'ir_r3_k3.5.7.9_a1.1_p1.1_s1_e3_c120_se0.5_nsw'],  # swish
      # stage 5, 14x14in
      ['ir_r1_k3.5.7.9_s2_e6_c200_se0.5_nsw', 'ir_r3_k3.5.7.9_p1.1_s1_e6_c200_se0.5_nsw'],  # swish
      # 7x7
  ]
  model_kwargs = dict(
      block_args=decode_arch_def(arch_def, depth_multiplier, depth_trunc='round'),
      num_features=1536,
      stem_size=24,
      round_chs_fn=partial(round_channels, multiplier=channel_multiplier),
      norm_layer=partial(nn.BatchNorm2d, **resolve_bn_args(kwargs)),
      **kwargs
  )
  model = _create_effnet(variant, pretrained, **model_kwargs)
  return model


def mnasnet_050(pretrained=False, **kwargs):
  """ MNASNet B1, depth multiplier of 0.5. """
  model = _gen_mnasnet_b1('mnasnet_050', 0.5, pretrained=pretrained, **kwargs)
  return model


def mnasnet_075(pretrained=False, **kwargs):
  """ MNASNet B1, depth multiplier of 0.75. """
  model = _gen_mnasnet_b1('mnasnet_075', 0.75, pretrained=pretrained, **kwargs)
  return model


def mnasnet_100(pretrained=False, **kwargs):
  """ MNASNet B1, depth multiplier of 1.0. """
  model = _gen_mnasnet_b1('mnasnet_100', 1.0, pretrained=pretrained, **kwargs)
  return model


def mnasnet_b1(pretrained=False, **kwargs):
  """ MNASNet B1, depth multiplier of 1.0. """
  return mnasnet_100(pretrained, **kwargs)


def mnasnet_140(pretrained=False, **kwargs):
  """ MNASNet B1,  depth multiplier of 1.4 """
  model = _gen_mnasnet_b1('mnasnet_140', 1.4, pretrained=pretrained, **kwargs)
  return model


def semnasnet_050(pretrained=False, **kwargs):
  """ MNASNet A1 (w/ SE), depth multiplier of 0.5 """
  model = _gen_mnasnet_a1('semnasnet_050', 0.5, pretrained=pretrained, **kwargs)
  return model


def semnasnet_075(pretrained=False, **kwargs):
  """ MNASNet A1 (w/ SE),  depth multiplier of 0.75. """
  model = _gen_mnasnet_a1('semnasnet_075', 0.75, pretrained=pretrained, **kwargs)
  return model


def semnasnet_100(pretrained=False, **kwargs):
  """ MNASNet A1 (w/ SE), depth multiplier of 1.0. """
  model = _gen_mnasnet_a1('semnasnet_100', 1.0, pretrained=pretrained, **kwargs)
  return model


def mnasnet_a1(pretrained=False, **kwargs):
  """ MNASNet A1 (w/ SE), depth multiplier of 1.0. """
  return semnasnet_100(pretrained, **kwargs)


def semnasnet_140(pretrained=False, **kwargs):
  """ MNASNet A1 (w/ SE), depth multiplier of 1.4. """
  model = _gen_mnasnet_a1('semnasnet_140', 1.4, pretrained=pretrained, **kwargs)
  return model


def mnasnet_small(pretrained=False, **kwargs):
  """ MNASNet Small,  depth multiplier of 1.0. """
  model = _gen_mnasnet_small('mnasnet_small', 1.0, pretrained=pretrained, **kwargs)
  return model


def mobilenetv2_100(pretrained=False, **kwargs):
  """ MobileNet V2 w/ 1.0 channel multiplier """
  model = _gen_mobilenet_v2('mobilenetv2_100', 1.0, pretrained=pretrained, **kwargs)
  return model


def mobilenetv2_140(pretrained=False, **kwargs):
  """ MobileNet V2 w/ 1.4 channel multiplier """
  model = _gen_mobilenet_v2('mobilenetv2_140', 1.4, pretrained=pretrained, **kwargs)
  return model


def mobilenetv2_110d(pretrained=False, **kwargs):
  """ MobileNet V2 w/ 1.1 channel, 1.2 depth multipliers"""
  model = _gen_mobilenet_v2(
      'mobilenetv2_110d', 1.1, depth_multiplier=1.2, fix_stem_head=True, pretrained=pretrained, **kwargs)
  return model


def mobilenetv2_120d(pretrained=False, **kwargs):
  """ MobileNet V2 w/ 1.2 channel, 1.4 depth multipliers """
  model = _gen_mobilenet_v2(
      'mobilenetv2_120d', 1.2, depth_multiplier=1.4, fix_stem_head=True, pretrained=pretrained, **kwargs)
  return model


def fbnetc_100(pretrained=False, **kwargs):
  """ FBNet-C """
  if pretrained:
    # pretrained model trained with non-default BN epsilon
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  model = _gen_fbnetc('fbnetc_100', 1.0, pretrained=pretrained, **kwargs)
  return model


def spnasnet_100(pretrained=False, **kwargs):
  """ Single-Path NAS Pixel1"""
  model = _gen_spnasnet('spnasnet_100', 1.0, pretrained=pretrained, **kwargs)
  return model


def efficientnet_b0(pretrained=False, **kwargs):
  """ EfficientNet-B0 """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_b0', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def eca_efficientnet_b0(pretrained=False, **kwargs):
  """ EfficientNet-B0 w/ ECA attn """
  # NOTE experimental config
  model = _gen_efficientnet(
      'eca_efficientnet_b0', se_layer='ecam', channel_multiplier=1.0, depth_multiplier=1.0,
      pretrained=pretrained, **kwargs)
  return model


def gc_efficientnet_b0(pretrained=False, **kwargs):
  """ EfficientNet-B0 w/ GlobalContext """
  # NOTE experminetal config
  model = _gen_efficientnet(
      'gc_efficientnet_b0', se_layer='gc', channel_multiplier=1.0, depth_multiplier=1.0,
      pretrained=pretrained, **kwargs)
  return model


def efficientnet_b1(pretrained=False, **kwargs):
  """ EfficientNet-B1 """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_b1', channel_multiplier=1.0, depth_multiplier=1.1, pretrained=pretrained, **kwargs)
  return model


def efficientnet_b2(pretrained=False, **kwargs):
  """ EfficientNet-B2 """
  # NOTE for train, drop_rate should be 0.3, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_b2', channel_multiplier=1.1, depth_multiplier=1.2, pretrained=pretrained, **kwargs)
  model.SIZE = [256, 256]
  model.CROP = 1.0
  return model


def efficientnet_b2a(pretrained=False, **kwargs):
  """ EfficientNet-B2 @ 288x288 w/ 1.0 test crop"""
  # WARN this model def is deprecated, different train/test res + test crop handled by default_cfg now
  return efficientnet_b2(pretrained=pretrained, **kwargs)


def efficientnet_b3(pretrained=False, **kwargs):
  """ EfficientNet-B3 """
  # NOTE for train, drop_rate should be 0.3, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_b3', channel_multiplier=1.2, depth_multiplier=1.4, pretrained=pretrained, **kwargs)
  model.SIZE = [288, 288]
  model.CROP = 1.0
  return model


def efficientnet_b3a(pretrained=False, **kwargs):
  """ EfficientNet-B3 @ 320x320 w/ 1.0 test crop-pct """
  # WARN this model def is deprecated, different train/test res + test crop handled by default_cfg now
  return efficientnet_b3(pretrained=pretrained, **kwargs)


def efficientnet_b4(pretrained=False, **kwargs):
  """ EfficientNet-B4 """
  # NOTE for train, drop_rate should be 0.4, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_b4', channel_multiplier=1.4, depth_multiplier=1.8, pretrained=pretrained, **kwargs)
  model.SIZE = [320, 320]
  model.CROP = 1.0
  return model


def efficientnet_b5(pretrained=False, **kwargs):
  """ EfficientNet-B5 """
  # NOTE for train, drop_rate should be 0.4, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_b5', channel_multiplier=1.6, depth_multiplier=2.2, pretrained=pretrained, **kwargs)
  model.SIZE = [456, 456]
  model.CROP = 0.934
  return model


def efficientnet_b6(pretrained=False, **kwargs):
  """ EfficientNet-B6 """
  # NOTE for train, drop_rate should be 0.5, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_b6', channel_multiplier=1.8, depth_multiplier=2.6, pretrained=pretrained, **kwargs)
  model.SIZE = [528, 528]
  model.CROP = 0.942
  return model


def efficientnet_b7(pretrained=False, **kwargs):
  """ EfficientNet-B7 """
  # NOTE for train, drop_rate should be 0.5, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_b7', channel_multiplier=2.0, depth_multiplier=3.1, pretrained=pretrained, **kwargs)
  model.SIZE = [600, 600]
  model.CROP = 0.949
  return model


def efficientnet_b8(pretrained=False, **kwargs):
  """ EfficientNet-B8 """
  # NOTE for train, drop_rate should be 0.5, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_b8', channel_multiplier=2.2, depth_multiplier=3.6, pretrained=pretrained, **kwargs)
  model.SIZE = [672, 672]
  model.CROP = 0.954
  return model


def efficientnet_l2(pretrained=False, **kwargs):
  """ EfficientNet-L2."""
  # NOTE for train, drop_rate should be 0.5, drop_path_rate should be 0.2
  model = _gen_efficientnet(
      'efficientnet_l2', channel_multiplier=4.3, depth_multiplier=5.3, pretrained=pretrained, **kwargs)
  model.SIZE = [800, 800]
  model.CROP = 0.961
  return model


def efficientnet_es(pretrained=False, **kwargs):
  """ EfficientNet-Edge Small. """
  model = _gen_efficientnet_edge(
      'efficientnet_es', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def efficientnet_em(pretrained=False, **kwargs):
  """ EfficientNet-Edge-Medium. """
  model = _gen_efficientnet_edge(
      'efficientnet_em', channel_multiplier=1.0, depth_multiplier=1.1, pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.882
  return model


def efficientnet_el(pretrained=False, **kwargs):
  """ EfficientNet-Edge-Large. """
  model = _gen_efficientnet_edge(
      'efficientnet_el', channel_multiplier=1.2, depth_multiplier=1.4, pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 0.904
  return model


def efficientnet_cc_b0_4e(pretrained=False, **kwargs):
  """ EfficientNet-CondConv-B0 w/ 8 Experts """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  model = _gen_efficientnet_condconv(
      'efficientnet_cc_b0_4e', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def efficientnet_cc_b0_8e(pretrained=False, **kwargs):
  """ EfficientNet-CondConv-B0 w/ 8 Experts """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  model = _gen_efficientnet_condconv(
      'efficientnet_cc_b0_8e', channel_multiplier=1.0, depth_multiplier=1.0, experts_multiplier=2,
      pretrained=pretrained, **kwargs)
  return model


def efficientnet_cc_b1_8e(pretrained=False, **kwargs):
  """ EfficientNet-CondConv-B1 w/ 8 Experts """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  model = _gen_efficientnet_condconv(
      'efficientnet_cc_b1_8e', channel_multiplier=1.0, depth_multiplier=1.1, experts_multiplier=2,
      pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.882
  return model


def efficientnet_lite0(pretrained=False, **kwargs):
  """ EfficientNet-Lite0 """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  model = _gen_efficientnet_lite(
      'efficientnet_lite0', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def efficientnet_lite1(pretrained=False, **kwargs):
  """ EfficientNet-Lite1 """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  model = _gen_efficientnet_lite(
      'efficientnet_lite1', channel_multiplier=1.0, depth_multiplier=1.1, pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.882
  return model


def efficientnet_lite2(pretrained=False, **kwargs):
  """ EfficientNet-Lite2 """
  # NOTE for train, drop_rate should be 0.3, drop_path_rate should be 0.2
  model = _gen_efficientnet_lite(
      'efficientnet_lite2', channel_multiplier=1.1, depth_multiplier=1.2, pretrained=pretrained, **kwargs)
  model.SIZE = [260, 260]
  model.CROP = 0.890
  return model


def efficientnet_lite3(pretrained=False, **kwargs):
  """ EfficientNet-Lite3 """
  # NOTE for train, drop_rate should be 0.3, drop_path_rate should be 0.2
  model = _gen_efficientnet_lite(
      'efficientnet_lite3', channel_multiplier=1.2, depth_multiplier=1.4, pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 0.904
  return model


def efficientnet_lite4(pretrained=False, **kwargs):
  """ EfficientNet-Lite4 """
  # NOTE for train, drop_rate should be 0.4, drop_path_rate should be 0.2
  model = _gen_efficientnet_lite(
      'efficientnet_lite4', channel_multiplier=1.4, depth_multiplier=1.8, pretrained=pretrained, **kwargs)
  model.SIZE = [380, 380]
  model.CROP = 0.922
  return model


def efficientnetv2_rw_t(pretrained=False, **kwargs):
  """ EfficientNet-V2 Tiny (Custom variant, tiny not in paper). """
  model = _gen_efficientnetv2_s(
      'efficientnetv2_rw_t', channel_multiplier=0.8, depth_multiplier=0.9, rw=False, pretrained=pretrained, **kwargs)
  model.SIZE = [224, 224]
  model.CROP = 1.0
  return model


def gc_efficientnetv2_rw_t(pretrained=False, **kwargs):
  """ EfficientNet-V2 Tiny w/ Global Context Attn (Custom variant, tiny not in paper). """
  model = _gen_efficientnetv2_s(
      'gc_efficientnetv2_t', channel_multiplier=0.8, depth_multiplier=0.9,
      rw=False, se_layer='gc', pretrained=pretrained, **kwargs)
  model.SIZE = [224, 224]
  model.CROP = 1.0
  return model


def efficientnetv2_rw_s(pretrained=False, **kwargs):
  """ EfficientNet-V2 Small (RW variant).
  NOTE: This is my initial (pre official code release) w/ some differences.
  See efficientnetv2_s and tf_efficientnetv2_s for versions that match the official w/ PyTorch vs TF padding
  """
  model = _gen_efficientnetv2_s('efficientnetv2_rw_s', rw=True, pretrained=pretrained, **kwargs)
  model.SIZE = [288, 288]
  model.CROP = 1.0
  return model


def efficientnetv2_rw_m(pretrained=False, **kwargs):
  """ EfficientNet-V2 Medium (RW variant).
  """
  model = _gen_efficientnetv2_s(
      'efficientnetv2_rw_m', channel_multiplier=1.2, depth_multiplier=(1.2,) * 4 + (1.6,) * 2, rw=True,
      pretrained=pretrained, **kwargs)
  model.SIZE = [320, 320]
  model.CROP = 1.0
  return model


def efficientnetv2_s(pretrained=False, **kwargs):
  """ EfficientNet-V2 Small. """
  model = _gen_efficientnetv2_s('efficientnetv2_s', pretrained=pretrained, **kwargs)
  model.SIZE = [288, 288]
  model.CROP = 1.0
  return model


def efficientnetv2_m(pretrained=False, **kwargs):
  """ EfficientNet-V2 Medium. """
  model = _gen_efficientnetv2_m('efficientnetv2_m', pretrained=pretrained, **kwargs)
  model.SIZE = [320, 320]
  model.CROP = 1.0
  return model


def efficientnetv2_l(pretrained=False, **kwargs):
  """ EfficientNet-V2 Large. """
  model = _gen_efficientnetv2_l('efficientnetv2_l', pretrained=pretrained, **kwargs)
  model.SIZE = [384, 384]
  model.CROP = 1.0
  return model


def tf_efficientnet_b0(pretrained=False, **kwargs):
  """ EfficientNet-B0. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b0', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def tf_efficientnet_b1(pretrained=False, **kwargs):
  """ EfficientNet-B1. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b1', channel_multiplier=1.0, depth_multiplier=1.1, pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.882
  return model


def tf_efficientnet_b2(pretrained=False, **kwargs):
  """ EfficientNet-B2. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b2', channel_multiplier=1.1, depth_multiplier=1.2, pretrained=pretrained, **kwargs)
  model.SIZE = [260, 260]
  model.CROP = 0.890
  return model


def tf_efficientnet_b3(pretrained=False, **kwargs):
  """ EfficientNet-B3. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b3', channel_multiplier=1.2, depth_multiplier=1.4, pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 0.904
  return model


def tf_efficientnet_b4(pretrained=False, **kwargs):
  """ EfficientNet-B4. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b4', channel_multiplier=1.4, depth_multiplier=1.8, pretrained=pretrained, **kwargs)
  model.SIZE = [380, 380]
  model.CROP = 0.922
  return model


def tf_efficientnet_b5(pretrained=False, **kwargs):
  """ EfficientNet-B5. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b5', channel_multiplier=1.6, depth_multiplier=2.2, pretrained=pretrained, **kwargs)
  model.SIZE = [456, 456]
  model.CROP = 0.934
  return model


def tf_efficientnet_b6(pretrained=False, **kwargs):
  """ EfficientNet-B6. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b6', channel_multiplier=1.8, depth_multiplier=2.6, pretrained=pretrained, **kwargs)
  model.SIZE = [528, 528]
  model.CROP = 0.942
  return model


def tf_efficientnet_b7(pretrained=False, **kwargs):
  """ EfficientNet-B7. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b7', channel_multiplier=2.0, depth_multiplier=3.1, pretrained=pretrained, **kwargs)
  model.SIZE = [600, 600]
  model.CROP = 0.949
  return model


def tf_efficientnet_b8(pretrained=False, **kwargs):
  """ EfficientNet-B8. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b8', channel_multiplier=2.2, depth_multiplier=3.6, pretrained=pretrained, **kwargs)
  model.SIZE = [672, 672]
  model.CROP = 0.954
  return model


def tf_efficientnet_b0_ap(pretrained=False, **kwargs):
  """ EfficientNet-B0 AdvProp. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b0_ap', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  model.SIZE = [224, 224]
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_b1_ap(pretrained=False, **kwargs):
  """ EfficientNet-B1 AdvProp. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b1_ap', channel_multiplier=1.0, depth_multiplier=1.1, pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.882
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_b2_ap(pretrained=False, **kwargs):
  """ EfficientNet-B2 AdvProp. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b2_ap', channel_multiplier=1.1, depth_multiplier=1.2, pretrained=pretrained, **kwargs)
  model.SIZE = [260, 260]
  model.CROP = 0.890
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_b3_ap(pretrained=False, **kwargs):
  """ EfficientNet-B3 AdvProp. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b3_ap', channel_multiplier=1.2, depth_multiplier=1.4, pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 0.904
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_b4_ap(pretrained=False, **kwargs):
  """ EfficientNet-B4 AdvProp. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b4_ap', channel_multiplier=1.4, depth_multiplier=1.8, pretrained=pretrained, **kwargs)
  model.SIZE = [380, 380]
  model.CROP = 0.922
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_b5_ap(pretrained=False, **kwargs):
  """ EfficientNet-B5 AdvProp. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b5_ap', channel_multiplier=1.6, depth_multiplier=2.2, pretrained=pretrained, **kwargs)
  model.SIZE = [456, 456]
  model.CROP = 0.934
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_b6_ap(pretrained=False, **kwargs):
  """ EfficientNet-B6 AdvProp. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b6_ap', channel_multiplier=1.8, depth_multiplier=2.6, pretrained=pretrained, **kwargs)
  model.SIZE = [528, 528]
  model.CROP = 0.942
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_b7_ap(pretrained=False, **kwargs):
  """ EfficientNet-B7 AdvProp. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b7_ap', channel_multiplier=2.0, depth_multiplier=3.1, pretrained=pretrained, **kwargs)
  model.SIZE = [600, 600]
  model.CROP = 0.949
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_b8_ap(pretrained=False, **kwargs):
  """ EfficientNet-B8 AdvProp. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b8_ap', channel_multiplier=2.2, depth_multiplier=3.6, pretrained=pretrained, **kwargs)
  model.SIZE = [672, 672]
  model.CROP = 0.954
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_b0_ns(pretrained=False, **kwargs):
  """ EfficientNet-B0 NoisyStudent. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b0_ns', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def tf_efficientnet_b1_ns(pretrained=False, **kwargs):
  """ EfficientNet-B1 NoisyStudent. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b1_ns', channel_multiplier=1.0, depth_multiplier=1.1, pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.882
  return model


def tf_efficientnet_b2_ns(pretrained=False, **kwargs):
  """ EfficientNet-B2 NoisyStudent. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b2_ns', channel_multiplier=1.1, depth_multiplier=1.2, pretrained=pretrained, **kwargs)
  model.SIZE = [260, 260]
  model.CROP = 0.890
  return model


def tf_efficientnet_b3_ns(pretrained=False, **kwargs):
  """ EfficientNet-B3 NoisyStudent. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b3_ns', channel_multiplier=1.2, depth_multiplier=1.4, pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 0.904
  return model


def tf_efficientnet_b4_ns(pretrained=False, **kwargs):
  """ EfficientNet-B4 NoisyStudent. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b4_ns', channel_multiplier=1.4, depth_multiplier=1.8, pretrained=pretrained, **kwargs)
  model.SIZE = [380, 380]
  model.CROP = 0.922
  return model


def tf_efficientnet_b5_ns(pretrained=False, **kwargs):
  """ EfficientNet-B5 NoisyStudent. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b5_ns', channel_multiplier=1.6, depth_multiplier=2.2, pretrained=pretrained, **kwargs)
  model.SIZE = [456, 456]
  model.CROP = 0.934
  return model


def tf_efficientnet_b6_ns(pretrained=False, **kwargs):
  """ EfficientNet-B6 NoisyStudent. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b6_ns', channel_multiplier=1.8, depth_multiplier=2.6, pretrained=pretrained, **kwargs)
  model.SIZE = [528, 528]
  model.CROP = 0.942
  return model


def tf_efficientnet_b7_ns(pretrained=False, **kwargs):
  """ EfficientNet-B7 NoisyStudent. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_b7_ns', channel_multiplier=2.0, depth_multiplier=3.1, pretrained=pretrained, **kwargs)
  model.SIZE = [600, 600]
  model.CROP = 0.949
  return model


def tf_efficientnet_l2_ns_475(pretrained=False, **kwargs):
  """ EfficientNet-L2 NoisyStudent @ 475x475. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_l2_ns_475', channel_multiplier=4.3, depth_multiplier=5.3, pretrained=pretrained, **kwargs)
  model.SIZE = [475, 475]
  model.CROP = 0.936
  return model


def tf_efficientnet_l2_ns(pretrained=False, **kwargs):
  """ EfficientNet-L2 NoisyStudent. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.5
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet(
      'tf_efficientnet_l2_ns', channel_multiplier=4.3, depth_multiplier=5.3, pretrained=pretrained, **kwargs)
  model.SIZE = [800, 800]
  model.CROP = 0.96
  return model


def tf_efficientnet_es(pretrained=False, **kwargs):
  """ EfficientNet-Edge Small. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_edge(
      'tf_efficientnet_es', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_em(pretrained=False, **kwargs):
  """ EfficientNet-Edge-Medium. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_edge(
      'tf_efficientnet_em', channel_multiplier=1.0, depth_multiplier=1.1, pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.882
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_el(pretrained=False, **kwargs):
  """ EfficientNet-Edge-Large. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_edge(
      'tf_efficientnet_el', channel_multiplier=1.2, depth_multiplier=1.4, pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 0.904
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_cc_b0_4e(pretrained=False, **kwargs):
  """ EfficientNet-CondConv-B0 w/ 4 Experts. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_condconv(
      'tf_efficientnet_cc_b0_4e', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_cc_b0_8e(pretrained=False, **kwargs):
  """ EfficientNet-CondConv-B0 w/ 8 Experts. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_condconv(
      'tf_efficientnet_cc_b0_8e', channel_multiplier=1.0, depth_multiplier=1.0, experts_multiplier=2,
      pretrained=pretrained, **kwargs)
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_cc_b1_8e(pretrained=False, **kwargs):
  """ EfficientNet-CondConv-B1 w/ 8 Experts. Tensorflow compatible variant """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_condconv(
      'tf_efficientnet_cc_b1_8e', channel_multiplier=1.0, depth_multiplier=1.1, experts_multiplier=2,
      pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.882
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_lite0(pretrained=False, **kwargs):
  """ EfficientNet-Lite0 """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_lite(
      'tf_efficientnet_lite0', channel_multiplier=1.0, depth_multiplier=1.0, pretrained=pretrained, **kwargs)
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_lite1(pretrained=False, **kwargs):
  """ EfficientNet-Lite1 """
  # NOTE for train, drop_rate should be 0.2, drop_path_rate should be 0.2
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_lite(
      'tf_efficientnet_lite1', channel_multiplier=1.0, depth_multiplier=1.1, pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.882
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_lite2(pretrained=False, **kwargs):
  """ EfficientNet-Lite2 """
  # NOTE for train, drop_rate should be 0.3, drop_path_rate should be 0.2
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_lite(
      'tf_efficientnet_lite2', channel_multiplier=1.1, depth_multiplier=1.2, pretrained=pretrained, **kwargs)
  model.SIZE = [260, 260]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_lite3(pretrained=False, **kwargs):
  """ EfficientNet-Lite3 """
  # NOTE for train, drop_rate should be 0.3, drop_path_rate should be 0.2
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_lite(
      'tf_efficientnet_lite3', channel_multiplier=1.2, depth_multiplier=1.4, pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 0.904
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnet_lite4(pretrained=False, **kwargs):
  """ EfficientNet-Lite4 """
  # NOTE for train, drop_rate should be 0.4, drop_path_rate should be 0.2
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnet_lite(
      'tf_efficientnet_lite4', channel_multiplier=1.4, depth_multiplier=1.8, pretrained=pretrained, **kwargs)
  model.SIZE = [380, 380]
  model.CROP = 0.920
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_s(pretrained=False, **kwargs):
  """ EfficientNet-V2 Small. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_s('tf_efficientnetv2_s', pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_m(pretrained=False, **kwargs):
  """ EfficientNet-V2 Medium. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_m('tf_efficientnetv2_m', pretrained=pretrained, **kwargs)
  model.SIZE = [384, 384]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_l(pretrained=False, **kwargs):
  """ EfficientNet-V2 Large. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_l('tf_efficientnetv2_l', pretrained=pretrained, **kwargs)
  model.SIZE = [384, 384]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_s_in21ft1k(pretrained=False, **kwargs):
  """ EfficientNet-V2 Small. Pretrained on ImageNet-21k, fine-tuned on 1k. Tensorflow compatible variant
  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_s('tf_efficientnetv2_s_in21ft1k', pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_m_in21ft1k(pretrained=False, **kwargs):
  """ EfficientNet-V2 Medium. Pretrained on ImageNet-21k, fine-tuned on 1k. Tensorflow compatible variant
  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_m('tf_efficientnetv2_m_in21ft1k', pretrained=pretrained, **kwargs)
  model.SIZE = [384, 384]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_l_in21ft1k(pretrained=False, **kwargs):
  """ EfficientNet-V2 Large. Pretrained on ImageNet-21k, fine-tuned on 1k. Tensorflow compatible variant
  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_l('tf_efficientnetv2_l_in21ft1k', pretrained=pretrained, **kwargs)
  model.SIZE = [384, 384]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_s_in21k(pretrained=False, **kwargs):
  """ EfficientNet-V2 Small w/ ImageNet-21k pretrained weights. Tensorflow compatible variant
  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_s('tf_efficientnetv2_s_in21k', pretrained=pretrained, **kwargs)
  model.SIZE = [300, 300]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_m_in21k(pretrained=False, **kwargs):
  """ EfficientNet-V2 Medium w/ ImageNet-21k pretrained weights. Tensorflow compatible variant
  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_m('tf_efficientnetv2_m_in21k', pretrained=pretrained, **kwargs)
  model.SIZE = [384, 384]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_l_in21k(pretrained=False, **kwargs):
  """ EfficientNet-V2 Large w/ ImageNet-21k pretrained weights. Tensorflow compatible variant
  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_l('tf_efficientnetv2_l_in21k', pretrained=pretrained, **kwargs)
  model.SIZE = [384, 384]
  model.CROP = 1.0
  model.MEAN = [0.5, 0.5, 0.5]
  model.STD = [0.5, 0.5, 0.5]
  return model


def tf_efficientnetv2_b0(pretrained=False, **kwargs):
  """ EfficientNet-V2-B0. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_base('tf_efficientnetv2_b0', pretrained=pretrained, **kwargs)
  model.SIZE = [192, 192]
  return model


def tf_efficientnetv2_b1(pretrained=False, **kwargs):
  """ EfficientNet-V2-B1. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_base(
      'tf_efficientnetv2_b1', channel_multiplier=1.0, depth_multiplier=1.1, pretrained=pretrained, **kwargs)
  model.SIZE = [192, 192]
  model.CROP = 0.882
  return model


def tf_efficientnetv2_b2(pretrained=False, **kwargs):
  """ EfficientNet-V2-B2. Tensorflow compatible variant  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_base(
      'tf_efficientnetv2_b2', channel_multiplier=1.1, depth_multiplier=1.2, pretrained=pretrained, **kwargs)
  model.SIZE = [208, 208]
  model.CROP = 0.890
  return model


def tf_efficientnetv2_b3(pretrained=False, **kwargs):
  """ EfficientNet-V2-B3. Tensorflow compatible variant """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_efficientnetv2_base(
      'tf_efficientnetv2_b3', channel_multiplier=1.2, depth_multiplier=1.4, pretrained=pretrained, **kwargs)
  model.SIZE = [240, 240]
  model.CROP = 0.904
  return model


def mixnet_s(pretrained=False, **kwargs):
  """Creates a MixNet Small model.
  """
  model = _gen_mixnet_s(
      'mixnet_s', channel_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def mixnet_m(pretrained=False, **kwargs):
  """Creates a MixNet Medium model.
  """
  model = _gen_mixnet_m(
      'mixnet_m', channel_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def mixnet_l(pretrained=False, **kwargs):
  """Creates a MixNet Large model.
  """
  model = _gen_mixnet_m(
      'mixnet_l', channel_multiplier=1.3, pretrained=pretrained, **kwargs)
  return model


def mixnet_xl(pretrained=False, **kwargs):
  """Creates a MixNet Extra-Large model.
  Not a paper spec, experimental def by RW w/ depth scaling.
  """
  model = _gen_mixnet_m(
      'mixnet_xl', channel_multiplier=1.6, depth_multiplier=1.2, pretrained=pretrained, **kwargs)
  return model


def mixnet_xxl(pretrained=False, **kwargs):
  """Creates a MixNet Double Extra Large model.
  Not a paper spec, experimental def by RW w/ depth scaling.
  """
  model = _gen_mixnet_m(
      'mixnet_xxl', channel_multiplier=2.4, depth_multiplier=1.3, pretrained=pretrained, **kwargs)
  return model


def tf_mixnet_s(pretrained=False, **kwargs):
  """Creates a MixNet Small model. Tensorflow compatible variant
  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_mixnet_s(
      'tf_mixnet_s', channel_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def tf_mixnet_m(pretrained=False, **kwargs):
  """Creates a MixNet Medium model. Tensorflow compatible variant
  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_mixnet_m(
      'tf_mixnet_m', channel_multiplier=1.0, pretrained=pretrained, **kwargs)
  return model


def tf_mixnet_l(pretrained=False, **kwargs):
  """Creates a MixNet Large model. Tensorflow compatible variant
  """
  kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
  kwargs['pad_type'] = 'same'
  model = _gen_mixnet_m(
      'tf_mixnet_l', channel_multiplier=1.3, pretrained=pretrained, **kwargs)
  return model
