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

from .base import Evaluator
from .base import ComposeEvaluator

from .classification import TopkEvaluator
from .classification import MultiLabelClsEvaluator
from .classification import ConfusionMatrixEvaluator

from .image import ImageSimilarityEvaluator

from .regression import RegressionEvaluator
from .avec2014 import Avec2014Evaluator
from .quality_assess import QualityAssessEvaluator

from .segmentation import SegmentationEvaluator
from .segmentation import SaliencyEvaluator
from .segmentation import MattingEvaluator
from .segmentation import PointCloudSegmentEvaluator

from .verification import VerificationEvaluator

from .detection import CocoEvaluator
from .widerface import WiderfaceEvaluator

from .landmark import FaceLandmarkEvaluator

from .optical_flow import OpticalFlowEvaluator