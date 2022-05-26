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
"""TensorWrapper Transform

  There are four core components to describe a variety of data type.

  - Meta: used in datasets and transform: it is usually used in Datasets class
    and maintains a numpy-like binary information. Generally, we use opencv or
    numpy to manipulate them.

  - [P]pil: it use Image.PIL as inputs.
    e.g: <T._random_crop_pil, T.RandomCropPIL>

  - [F]functional: it use SampleMetas as inputs.
    e.g. <T._random_crop_meta, T.RandomCropMeta>

  - [T]tensor: it use torch.Tensor as inputs.
    e.g. <T._random_crop_tensor, T.RandomCropTensor>

  - [N]numpy: it use np.array as inputs
    e.g. <T._random_crop_np, T.RandomCropNumpy>

  - General: <T.random_crop, T.RandomCrop> to dispatch.

"""

# constant
from .meta import COLORSPACE
from .meta import COLORSPACE_MAPPING
from .meta import INTER_CV_TO_PIL
from .meta import INTER_CV_TO_TCH

# container
from .meta import MetaBase
from .meta import ImageMeta
from .meta import VideoMeta
from .meta import WaveformMeta
from .meta import BoxListMeta
from .meta import KpsListMeta
from .meta import MetaWrapper
from .meta import PointCloudMeta

# checker
from .meta import IsMeta
from .meta import IsNumpy
from .meta import IsPilImage
from .meta import IsTensor

# augmentation
from .primitive.affine import vflip
from .primitive.affine import random_vflip
from .primitive.affine import hflip
from .primitive.affine import random_hflip
from .primitive.affine import rotate
from .primitive.affine import random_rotate
from .primitive.affine import restoration_augment
from .primitive.affine import random_affine

from .primitive import bbox

from .primitive.colorspace import change_colorspace
from .primitive.colorspace import random_photometric_distortion

from .primitive.crop import random_crop
from .primitive.crop import center_crop
from .primitive.crop import random_zoom_in_crop
from .primitive.crop import minimum_iou_random_crop
from .primitive.crop import non_overlap_crop_patch
from .primitive.crop import random_crop_and_pad
from .primitive.crop import center_crop_and_pad

from .primitive.filter import random_iso_noise
from .primitive.filter import random_gaussian_noise
from .primitive.filter import random_gaussian_blur
from .primitive.filter import random_median_blur
from .primitive.filter import random_motion_blur
from .primitive.filter import sobel
from .primitive.filter import random_gamma

from .primitive.morphology import random_alpha_to_trimap
from .primitive.morphology import alpha_to_trimap

from .primitive.normalize import to_tensor
from .primitive.normalize import to_float
from .primitive.normalize import equal_hist
from .primitive.normalize import truncated_standardize
from .primitive.normalize import local_contrast_normalize

from .primitive.pad import pad
from .primitive.pad import pad_to_size_divisible
from .primitive.pad import pad_to_square
from .primitive.pad import random_expand
from .primitive.pad import pad_to_target_size

from .primitive.resize import shortside_resize
from .primitive.resize import resize
from .primitive.resize import random_resize

# external
from . import pil
