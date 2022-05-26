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

from .backbone2d import alexnet
from .backbone2d import bcnn
from .backbone2d import densenet
from .backbone2d import densenet_cifar
from .backbone2d import efficientnet
from .backbone2d import efficientnet_cifar
from .backbone2d import googlenet
from .backbone2d import inceptionresnetv2
from .backbone2d import mobilenet_v2
from .backbone2d import mobilenet_v2_cifar
from .backbone2d import mobilenet_v2_deeplab
from .backbone2d import mobilenet_v3
from .backbone2d import resnet
from .backbone2d import resnet_cifar
from .backbone2d import resnet_tf
from .backbone2d import senet
from .backbone2d import senet_cifar
from .backbone2d import shufflenet_v1_cifar
from .backbone2d import shufflenet_v2
from .backbone2d import shufflenet_v2_cifar
from .backbone2d import squeezenet
from .backbone2d import vgg
from .backbone2d import vgg_cifar
from .backbone2d import vgg_extractor
from .backbone2d import xception

from .segment2d import asffnet
from .segment2d import bgmv2
from .segment2d import bisenet
from .segment2d import ccnet
from .segment2d import cgnet
from .segment2d import danet
from .segment2d import deeplabv3p
from .segment2d import drn
from .segment2d import dunet
from .segment2d import encnet
from .segment2d import enet
from .segment2d import erfnet
from .segment2d import espnet
from .segment2d import fastscnn
from .segment2d import fcn
from .segment2d import fenet
from .segment2d import frvsr
from .segment2d import icnet
from .segment2d import lednet
from .segment2d import lenet
from .segment2d import ocnet
from .segment2d import poolnet
from .segment2d import psanet
from .segment2d import pspnet
from .segment2d import unet

from .backbone3d import c3d
from .backbone3d import i3d
from .backbone3d import p3d
from .backbone3d import p3d_without_bn
from .backbone3d import r2plus1d
from .backbone3d import r3d

from .transformer2d import vit
