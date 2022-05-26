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
"""Reference
  https://github.com/cs-giung/face-detection-pytorch
"""
from .dsfd.dsfd import DSFD
from .faceboxes.faceboxes import FaceBoxes
from .mtcnn.mtcnn import MTCNN
from .pyramidbox.pyramidbox import PyramidBox
from .retinaface.retinaface import RetinafaceDetector
from .s3fd.s3fd import S3FD
from .tinyface.tinyface import TinyFace
