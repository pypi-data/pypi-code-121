# -*- coding: utf-8 -*-

from __future__ import annotations

from collections.abc import Callable, Mapping

import torch


def get_pooling(method: str) -> Callable[[Mapping, torch.Tensor], torch.Tensor]:
    methods = {
        "cls": cls_pooling,
        "mean": mean_pooling,
        "max": max_pooling,
    }
    pooling = methods.get(method)
    if pooling is None:
        raise ValueError(f"Pooling `method` should be one of {list(methods)}")

    return pooling


def mean_pooling(model_output: Mapping, attention_mask: torch.Tensor) -> torch.Tensor:
    token_embeddings = model_output["last_hidden_state"]
    input_mask_expanded = attention_mask.unsqueeze(dim=-1).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)
    sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)

    return sum_embeddings / sum_mask


def max_pooling(model_output: Mapping, attention_mask: torch.Tensor) -> torch.Tensor:
    token_embeddings = model_output["last_hidden_state"]
    input_mask_expanded = (
        attention_mask.unsqueeze(dim=-1).expand(token_embeddings.size()).float()
    )
    token_embeddings[input_mask_expanded == 0] = -1e9
    max_over_time = torch.max(token_embeddings, dim=1)[0]

    return max_over_time


def cls_pooling(model_output: Mapping, attention_mask: torch.Tensor) -> torch.Tensor:
    return model_output["last_hidden_state"][:, 0]
