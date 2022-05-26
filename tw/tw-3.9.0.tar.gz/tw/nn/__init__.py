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

from .activation import Swish
from .activation import Mish

from .attention import CBAMModule
from .attention import CECAModule
from .attention import ChannelAttention
from .attention import CollectAttention
from .attention import DistributeAttention
from .attention import ECAModule
from .attention import EffectiveSEModule
from .attention import SEModule
from .attention import SpatialAttention
from .attention import SqueezeExciteModule

from .conv import CondConv2d
from .conv import CondConvResidual
from .conv import ConvBnAct
from .conv import ConvModule
from .conv import DeformConv
from .conv import DeformConvFunction
from .conv import DepthwiseSeparableConv
from .conv import EdgeResidual
from .conv import InvertedResidual
from .conv import MixedConv2d
from .conv import ModulatedDeformConv
from .conv import ModulatedDeformConvFunction
from .conv import ModulatedDeformConvPack
from .conv import SameConv2d

from .convert import EmptyConv2d
from .convert import EmptyConvTranspose2d
from .convert import EmptyBatchNorm2d
from .convert import EmptyLayer
from .convert import FrozenBatchNorm2d

from .correlation import CorrLookup

from .drop import DropBlock2d
from .drop import DropPath

from .embedding import AngleLinear

from . import initialize
from . import losses

from .interpolate import PixelUnshuffle

from .losses import AngleLoss
from .losses import CharbonnierLoss
from .losses import ContentLoss
from .losses import EBMLoss
from .losses import GeneralGanLoss
from .losses import GradientPenaltyLoss
from .losses import KLStandardGaussianLoss
from .losses import LabelSmoothLoss
from .losses import LogRatioMetricLoss
from .losses import LPIPSLoss
from .losses import MutualChannelLoss
from .losses import OrderSensitiveMetricLoss
from .losses import PixelPositionAwareLoss
from .losses import PSNRLoss
from .losses import ReliabLoss
from .losses import SigmoidFocalLoss
from .losses import SmoothL1Loss
from .losses import StructuralSimilarityLoss

from .losses import PerceptualLoss
from .losses import WeightedTVLoss

from .losses import CIoULoss
from .losses import DIoULoss
from .losses import GIoULoss
from .losses import IoULoss

from .losses import MonotonicityRelatedLoss
from .losses import PLCCLoss

from .losses import LaplacianLoss
from .losses import NMELoss
from .losses import WingLoss
from .losses import SmoothWingLoss
from .losses import WiderWingLoss
from .losses import NormalizedWiderWingLoss

from .losses import MultiLevelEPELoss
from .losses import MultiLevelCharbonnierLoss

from .nms import MulticlassNMS
from .nms import MultiLabelNonMaxSuppression
from .nms import NonMaxSuppression

from .normalize import L2Norm
from .normalize import Scale

from .pooling import AdaptiveAvgMaxPool2d
from .pooling import AdaptiveCatAvgMaxPool2d
from .pooling import AtrousSpatialPyramidPooling
from .pooling import ChannelAvgPool
from .pooling import ChannelMaxPool
from .pooling import CrissCrossAttention
from .pooling import DeformRoIPooling
from .pooling import DeformRoIPoolingFunction
from .pooling import DeformRoIPoolingPack
from .pooling import ModulatedDeformRoIPoolingPack
from .pooling import RoIAlign
from .pooling import RoIPool

from .sample import GMMSampler
from .sample import GridSubSampling

from .search import KnnSearch

from .rnn import GRU
from .rnn import LSTM
from .rnn import RNN

from .filter import GradientIntensity

# detection related
from .anchor import AnchorMatcher
from .anchor import RetinaFaceAnchorGenerator
from .anchor import RetinaNetAnchorGenerator
from .anchor import SSDAnchorGenerator

from .bbox import GeneralBoxCoder
from .keypoints import BboxPtsCoder

from .head import RoIBoxHeadFCOS
from .head import RoIBoxHeadRetinaNet
from .head import RoIBoxHeadSSD
from .head import RoIBoxHeadYOLO
from .head import RoIBoxHeadYOLOF

from .fpn import FpnRetinaNet
from .fpn import FpnSSDExtraLayer
from .fpn import FpnYOLOFDilatedEncoder

from . import functional
