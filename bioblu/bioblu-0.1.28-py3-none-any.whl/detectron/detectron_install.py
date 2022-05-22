#!/usr/bin/env python3

import pip
import torch
import shutil

TORCH_VERSION = ".".join(torch.__version__.split(".")[:2])
CUDA_VERSION = torch.__version__.split("+")[-1]
print("torch: ", TORCH_VERSION, "; cuda: ", CUDA_VERSION)
# Install detectron that matches the above pytorch version
# See https://detectron2.readthedocs.io/tutorials/install.html for instructions


# pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/$CUDA_VERSION/torch$TORCH_VERSION/index.html
# If there is not yet a detectron release that matches the given torch + CUDA version, you need to install a different pytorch.
