# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Union

import torch
from ignite.handlers.checkpoint import Checkpoint
from torch import nn


def load_checkpoint(
    to_load: Union[Mapping, nn.Module], checkpoint: Union[str, os.PathLike]
) -> None:
    if isinstance(to_load, nn.Module):
        to_load = {"model": to_load}

    ckpt = torch.load(checkpoint, map_location="cpu")
    Checkpoint.load_objects(to_load=to_load, checkpoint=ckpt)


def plm_path(path: Union[str, os.PathLike]) -> str:
    root = os.getenv("PRETRAINED_MODEL_DIR")
    if root:
        return os.path.join(root, path)

    return str(path)
