# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional, Union

import torch
import torch.nn as nn
import torch.optim as optim
from transformers.optimization import get_linear_schedule_with_warmup


def cuda(enable: bool) -> bool:
    return enable and torch.cuda.is_available()


def device(
    device_str: str = "", return_string: bool = True
) -> Union[str, "torch.device"]:
    if (
        not device_str
        or device_str.startswith("cuda")
        and not torch.cuda.is_available()
    ):
        device_str = "cpu"

    return device_str if return_string else torch.device(device_str)


def get_pretrained_optimizer_and_scheduler(
    model: nn.Module,
    lr: float,
    weight_decay: float,
    warmup_steps: int,
    num_training_steps: Union[int, float],
    optimizer_kwargs: Optional[dict] = None,
    scheduler_kwargs: Optional[dict] = None,
) -> tuple[optim.Optimizer, optim.lr_scheduler.LambdaLR]:
    if lr <= 0:
        raise ValueError("`lr` must be positive.")

    if warmup_steps <= 0:
        raise ValueError("`warmup_steps` must be positive")

    if isinstance(warmup_steps, float):
        warmup_steps = int(warmup_steps * num_training_steps)

    if not optimizer_kwargs:
        optimizer_kwargs = {}

    if not scheduler_kwargs:
        scheduler_kwargs = {}

    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_parameters = [
        {
            "params": [
                p
                for n, p in model.named_parameters()
                if not any(nd in n for nd in no_decay)
            ],
            "weight_decay": weight_decay,
        },
        {
            "params": [
                p
                for n, p in model.named_parameters()
                if any(nd in n for nd in no_decay)
            ],
            "weight_decay": 0.0,
        },
    ]
    optimizer = optim.AdamW(optimizer_grouped_parameters, lr=lr, **optimizer_kwargs)

    lr_scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=num_training_steps,
        **scheduler_kwargs,
    )

    return (optimizer, lr_scheduler)
