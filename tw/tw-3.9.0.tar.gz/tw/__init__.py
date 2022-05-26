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
# autopep8: off

# constant
from enum import Enum

class phase(Enum):
  train = 0
  val = 1
  test = 2
  viz = 3

# 1 - independent
from .utils.logger import logger
from .utils import filesystem as fs
from .utils import timer
from .utils import tensorboard
from .utils import stat
from .utils import drawer
from .utils import parser
from .utils import export

# media
from .media import ply
from .media import media
# from .media import raw
from .media import flow
from .media import mesh

# 2 - utils level
from .utils import checkpoint
from .utils import runner
from . import evaluator

# 3 - transform level
from . import transform

# 4 - op level
from . import nn

# 5 - network level
from . import models

# 6 - dataset level
from . import datasets
from .utils import flops

# extra repo
from . import contrib

# optim
from . import optim

# autopep8: on
