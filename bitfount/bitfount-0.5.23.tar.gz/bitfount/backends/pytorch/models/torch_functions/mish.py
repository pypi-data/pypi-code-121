"""Copyright 2019 Less Wright.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Mish: A Self Regularized Non-Monotonic Neural Activation Function
https://arxiv.org/abs/1908.08681v1
github: https://github.com/lessw2020/mish
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class Mish(nn.Module):
    """Mish: A Self Regularized Non-Monotonic Neural Activation Function.

    More information here:
        Paper: https://arxiv.org/abs/1908.08681
        Github: https://github.com/lessw2020/mish
    """

    def __init__(self) -> None:
        super().__init__()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward method.

        Args:
            x: Input to the activation layer.

        Returns:
            Output of the activation layer.
        """
        # inlining this saves 1 second per epoch (V100 GPU) vs having a temp x
        # and then returning x
        return x * (torch.tanh(F.softplus(x)))
