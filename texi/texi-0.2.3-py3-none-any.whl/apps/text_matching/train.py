# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
from collections.abc import Mapping
from typing import Union

import ignite.distributed as idist
import torch
from ignite.engine import Engine
from ignite.metrics import Accuracy, Fbeta, Precision, Recall
from torch import nn
from torch.optim import Optimizer
from torch.optim.lr_scheduler import _LRScheduler
from torch.utils.data import DataLoader
from torchlight.dataset import get_dataloader
from torchlight.preprocessing import LabelEncoder
from torchlight.training import create_engines, run, setup_env
from torchlight.training.params import Params as _Params
from torchlight.utils.file import plm_path
from torchlight.utils.pytorch import get_pretrained_optimizer_and_scheduler
from transformers import BertTokenizer, BertTokenizerFast

from texi.datasets import JSONDatasets
from texi.datasets.dataset import Dataset, Datasets
from texi.pytorch.dataset.plm_collator import TextMatchingCollator
from texi.pytorch.models.text_matching import SBertForClassification, SBertForRegression


class Params(_Params):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_name = kwargs["model_name"]
        self.num_labels = kwargs["num_labels"]
        self.pretrained_model = kwargs.get("pretrained_model", "hfl/chinese-bert-wwm")
        self.dropout = kwargs.get("dropout", 0.1)
        self.pooling = kwargs.get("pooling", "mean")


def get_dataflows(
    datasets: Datasets,
    tokenizer: Union[BertTokenizerFast, BertTokenizer],
    label_encoder: LabelEncoder,
    params: Params,
) -> dict[str, DataLoader]:
    dataflows = {
        mode: get_dataloader(
            dataset,
            batch_size=params[f"{Dataset.map_modekeys(mode)}_batch_size"],
            collate_fn=TextMatchingCollator(
                tokenizer, label_encoder, mode=Dataset.map_modekeys(mode)
            ),
            sort_key=(lambda x: sum(len(xi) for xi in x["texts"]))
            if mode == "train"
            else None,
            num_workers=params["num_workers"],
            pin_memory=params["pin_memory"],
        )
        for mode, dataset in datasets.items()
    }

    return dataflows


def get_model(params: Params) -> nn.Module:
    name = params["model_name"].lower()
    if name == "sbert":
        if params["num_labels"] == 1:
            model = SBertForRegression(
                params["pretrained_model"], pooling=params["pooling"]
            )
        else:
            model = SBertForClassification(
                params["pretrained_model"],
                dropout=params["dropout"],
                pooling=params["pooling"],
                num_labels=params["num_labels"],
            )
    else:
        raise KeyError(name)

    return model


def get_criteria(params: Params) -> nn.Module:
    if params["num_labels"] == 1:
        return nn.MSELoss()

    if params["num_labels"] == 2:
        return nn.BCEWithLogitsLoss()

    return nn.CrossEntropyLoss()


def initialize(
    params: Params, num_train_examples: int
) -> tuple[nn.Module, nn.Module, Optimizer, _LRScheduler]:
    model = get_model(params)

    criteria = get_criteria(params)

    num_training_steps = (
        num_train_examples // params["train_batch_size"] * params["max_epochs"]
    )
    warmup_steps = params["lr_warmup"] * num_training_steps
    optimizer, lr_scheduler = get_pretrained_optimizer_and_scheduler(
        model, params["lr"], params["weight_decay"], warmup_steps, num_training_steps
    )

    model = idist.auto_model(model)
    criteria = criteria.to(idist.device())
    optimizer = idist.auto_optim(optimizer)

    return model, criteria, optimizer, lr_scheduler


def train_step(
    _: Engine, model: nn.Module, batch: Mapping, criteria: nn.Module
) -> dict:
    x, y = batch

    logit = model(**x)

    loss = criteria(logit, y.float())

    return {"loss": loss}


def eval_step(
    _: Engine, model: nn.Module, batch: Mapping
) -> tuple[torch.Tensor, torch.Tensor]:
    x, y = batch

    logit = model(**x)

    if logit.ndim == 1:
        y_pred = torch.sigmoid(logit.squeeze(dim=-1)).round()
        # FIXME: y_pred = (logit > 0).float() for SBertForRegression
    else:
        y_pred = torch.argmax(logit, dim=-1)

    return y_pred, y.float()


def training(local_rank: int, params: Params) -> None:
    if idist.get_rank() == 0:
        setup_env(params)

    # Load datasets.
    datasets = JSONDatasets.from_dir(params.data_dir, array=True).load()
    datasets.describe()
    tokenizer = BertTokenizerFast.from_pretrained(plm_path(params["pretrained_model"]))
    label_encoder = LabelEncoder(x["label"] for x in datasets.train)

    # Get data dataflows.
    dataflows = get_dataflows(datasets, tokenizer, label_encoder, params)

    # Create model.
    model, criteria, optimizer, lr_scheduler = initialize(params, len(datasets.train))

    accuracy = Accuracy(device=idist.device())
    precision = Precision(average=False, device=idist.device())
    recall = Recall(average=False, device=idist.device())
    f1 = Fbeta(1.0, precision=precision, recall=recall, device=idist.device())

    # Create engines
    trainer, *_ = create_engines(
        params,
        train_step,
        eval_step,
        dataflows,
        model,
        criteria,
        optimizer,
        lr_scheduler,
        eval_metrics={
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        },
        with_handlers=True,
    )

    # Train!
    trainer.run(dataflows["train"], max_epochs=params["max_epochs"])


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--params", type=Params.from_yaml, required=True)

    return parser.parse_args()


if __name__ == "__main__":
    run(training, parse_args().params)
