# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import os
import random
from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Optional, Union

import ignite.distributed as idist
from ignite.engine import Engine, Events
from ignite.handlers import global_step_from_engine
from torch import nn
from torchlight.preprocessing import LabelEncoder
from torchlight.training import Metrics
from torchlight.training.params import Params

from texi.apps.ner import (
    NerReVisualizer,
    compare_prediction_with_ground_truth,
    expand_entities,
)
from texi.pytorch.metrics import NerMetrics, ReMetrics
from texi.pytorch.models.spert import predict

try:
    import wandb
except ModuleNotFoundError:
    wandb = None  # type: ignore


if TYPE_CHECKING:
    from ignite.contrib.handlers import WandBLogger
    from transformers import BertTokenizer, BertTokenizerFast

    from texi.pytorch.models.spert.model import SpERT


class SpERTParams(Params):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pretrained_model = kwargs.get("pretrained_model", "bert-base-uncased")
        self.embedding_dim = kwargs.get("embedding_dim", 25)
        self.dropout = kwargs.get("dropout", 0.1)
        self.global_context_pooling = kwargs.get("global_context_pooling", "cls")
        self.negative_entity_type = kwargs.get(
            "negative_entity_type", "NEGATIVE_ENTITY"
        )
        self.negative_relation_type = kwargs.get(
            "negative_relation_type", "NEGATIVE_RELATION"
        )
        self.num_negative_entities = kwargs.get("num_negative_entities", 100)
        self.num_negative_relations = kwargs.get("num_negative_relations", 100)
        self.max_entity_length = kwargs.get("max_entity_length", 10)
        self.max_entities = kwargs.get("max_entities", 1000)
        self.max_relation_pairs = kwargs.get("max_relation_pairs", 1000)
        self.relation_filter_threshold = kwargs.get("relation_filter_threshold", 0.4)
        self.token_delimiter = kwargs.get("token_delimiter", " ")
        self.split_delimiter = kwargs.get("split_delimiter")
        self.max_length = kwargs.get("max_length", -1)


def train_step(_: Engine, model: SpERT, batch: Mapping, criteria: nn.Module) -> dict:
    output = model(
        batch["input_ids"],
        batch["attention_mask"],
        batch["token_type_ids"],
        batch["entity_mask"],
        batch["relation"],
        batch["relation_context_mask"],
    )

    loss = criteria(
        output["entity_logit"],
        batch["entity_label"],
        batch["entity_sample_mask"],
        output["relation_logit"],
        batch["relation_label"],
        batch["relation_sample_mask"],
    )

    return {"batch": batch, "loss": loss}


def eval_step(_: Engine, model: SpERT, batch: Mapping) -> dict:
    target, input_ = batch
    output = model.infer(
        input_["input_ids"],
        input_["attention_mask"],
        input_["token_type_ids"],
        input_["entity_mask"],
    )

    return {
        "target": target,
        "input": input_,
        "output": output,
    }


class SpERTEnv(object):
    def __init__(
        self,
        entity_label_encoder: LabelEncoder,
        negative_entity_index: int,
        relation_label_encoder: LabelEncoder,
        negative_relation_index: int,
        relation_filter_threshold: float,
    ) -> None:
        super().__init__()
        self.entity_label_encoder = entity_label_encoder
        self.negative_entity_index = negative_entity_index
        self.relation_label_encoder = relation_label_encoder
        self.negative_relation_index = negative_relation_index
        self.relation_filter_threshold = relation_filter_threshold

    def get_metrics(self, train: bool = True) -> Metrics:
        if train:
            return {}

        return {
            "ner": NerMetrics(
                self.entity_label_encoder.index2label,
                self.negative_entity_index,
                prefix="NER",
                output_transform=lambda outputs: {
                    "y": {
                        "label": outputs["target"]["entity_label"],
                        "span": outputs["target"]["entity_span"],
                        "mask": outputs["target"]["entity_sample_mask"],
                    },
                    "y_pred": {
                        "label": outputs["output"]["entity_logit"].argmax(dim=-1),
                        "span": outputs["input"]["entity_span"],
                        "mask": outputs["input"]["entity_sample_mask"],
                    },
                },
                device=idist.device(),
            ),
            "re": ReMetrics(
                self.relation_label_encoder.index2label,
                self.negative_relation_index,
                self.relation_filter_threshold,
                prefix="RE",
                output_transform=lambda outputs: {
                    "y": {
                        "label": outputs["target"]["relation_label"],
                        "pair": outputs["target"]["relation"],
                        "mask": outputs["target"]["relation_sample_mask"],
                        "entity_span": outputs["target"]["entity_span"],
                        "entity_label": outputs["target"]["entity_label"],
                    },
                    "y_pred": {
                        "label": outputs["output"]["relation_logit"],
                        "pair": outputs["output"]["relation"],
                        "mask": outputs["output"]["relation_sample_mask"],
                        "entity_span": outputs["input"]["entity_span"],
                        "entity_label": outputs["output"]["entity_logit"].argmax(
                            dim=-1
                        ),
                    },
                },
                device=idist.device(),
            ),
        }


class SpERTEvalExporter(object):
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.reset()

    def reset(self):
        self.targets = []
        self.predictions = []

    def update(
        self, targets: Iterable[Mapping], predictions: Iterable[Mapping]
    ) -> None:
        self.targets += list(targets)
        self.predictions += list(predictions)

    def export(
        self,
        epoch: Optional[int] = None,
        iteration: Optional[int] = None,
        filename: Optional[str] = None,
    ) -> None:
        if not filename:
            if epoch is None and iteration is None:
                raise ValueError(
                    "Either `filename` or `epoch` and `iteration` must be given"
                )
            filename = ""
            if epoch:
                filename += f"_epoch_{epoch}"
            if iteration:
                filename += f"_iteration_{iteration}"

        with open(os.path.join(self.output_dir, filename), mode="w") as f:
            outputs = [
                {"target": target, "prediction": prediction}
                for target, prediction in zip(self.targets, self.predictions)
            ]
            json.dump(outputs, f, ensure_ascii=False)

        self.reset()


class SpERTEvalSampler(object):
    # pylint: disable=no-self-use, too-many-arguments, too-many-instance-attributes
    def __init__(
        self,
        visualizer: NerReVisualizer,
        tokenizer: Union[BertTokenizer, BertTokenizerFast],
        entity_label_encoder: LabelEncoder,
        negative_entity_index: int,
        relation_label_encoder: LabelEncoder,
        negative_relation_index: int,
        relation_filter_threshold: float,
        save_dir: str,
        sample_size: Optional[int] = None,
        wandb_logger: Optional[WandBLogger] = None,
    ) -> None:
        self.visualizer = visualizer
        self.tokenizer = tokenizer
        self.entity_label_encoder = entity_label_encoder
        self.negative_entity_index = negative_entity_index
        self.relation_label_encoder = relation_label_encoder
        self.negative_relation_index = negative_relation_index
        self.relation_filter_threshold = relation_filter_threshold
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
        self.sample_size = sample_size
        self.wandb_logger = wandb_logger

        self.exporter = SpERTEvalExporter(os.path.join(self.save_dir, "data"))

        self.global_step_transform = None  # type: Optional[Callable]
        self.reset()

    def reset(self) -> None:
        self.entity_samples = []  # type: list[dict]
        self.relation_samples = []  # type: list[dict]

    def started(self, _: Engine) -> None:
        self.reset()

    def _expand_entities(self, relations, entities):
        return list(map(expand_entities, relations, entities))

    def _compare(self, y, y_pred, f, scores):
        y_trans = [*map(f, y)]
        y_pred_trans = [*map(f, y_pred)]

        tps = set(y_trans) & set(y_pred_trans)

        items = []
        for yi_pred, yi_pred_tran, score in zip(y_pred, y_pred_trans, scores):
            if yi_pred_tran in tps:
                items += [(yi_pred, 0, score)]  # tp
            else:
                items += [(yi_pred, 1, score)]  # fp

        for yi, yi_tran in zip(y, y_trans):
            if yi_tran not in tps:  # fn
                items += [(yi, -1, -1)]

        return items

    def update(self, engine: Engine) -> None:
        target = engine.state.output["target"]
        input_ = engine.state.output["input"]
        output = engine.state.output["output"]

        (
            entity_predictions,
            entity_scores,
            relation_predictions,
            relation_scores,
        ) = predict(
            output["entity_logit"],
            input_["entity_sample_mask"],
            input_["entity_span"],
            self.entity_label_encoder,
            self.negative_entity_index,
            output["relation_logit"],
            output["relation"],
            output["relation_sample_mask"],
            self.relation_label_encoder,
            self.negative_relation_index,
            self.relation_filter_threshold,
            return_scores=True,
        )  # type: ignore

        # pylint: disable=unbalanced-tuple-unpacking
        entity_targets, relation_targets = predict(
            target["entity_label"],
            target["entity_sample_mask"],
            target["entity_span"],
            self.entity_label_encoder,
            self.negative_entity_index,
            target["relation_label"],
            target["relation"],
            target["relation_sample_mask"],
            self.relation_label_encoder,
            self.negative_relation_index,
            self.relation_filter_threshold,
            return_scores=False,
        )  # type: ignore

        def _convert_to_example(entities, relations):
            examples = [
                {
                    "tokens": tokens[1:-1],
                    "entities": sample_entities,
                    "relations": sample_relations,
                }
                for tokens, sample_entities, sample_relations in zip(
                    input_["tokens"], entities, relations
                )
            ]

            return examples

        targets = _convert_to_example(entity_targets, relation_targets)
        predictions = _convert_to_example(entity_predictions, relation_predictions)
        self.exporter.update(targets, predictions)

        for args in zip(
            targets,
            entity_predictions,
            relation_predictions,
            entity_scores,
            relation_scores,
        ):
            diff = compare_prediction_with_ground_truth(*args)
            self.entity_samples += diff["entities"]
            self.relation_samples += diff["relations"]

    def _sample(self, examples):
        if self.sample_size is not None:
            examples = random.sample(examples, min(len(examples), self.sample_size))

        return examples

    def export(self, _: Engine) -> None:
        if self.global_step_transform is None:
            raise RuntimeError("Call `.setup()` first")

        epoch = self.global_step_transform(_, Events.EPOCH_COMPLETED)
        iteration = self.global_step_transform(_, Events.ITERATION_COMPLETED)
        suffix = f"epoch_{epoch}_iteration_{iteration}"

        entity_html = os.path.join(self.save_dir, f"entity_{suffix}.html")
        self.visualizer.export_entities(self._sample(self.entity_samples), entity_html)

        relation_html = os.path.join(self.save_dir, f"relation_{suffix}.html")
        self.visualizer.export_relations(
            self._sample(self.relation_samples), relation_html
        )

        if self.wandb_logger:
            if not wandb:
                raise RuntimeError("Install `wandb` package to enable HTML logging.")

            self.wandb_logger.log(
                {"Entity Extraction Examples": wandb.Html(open(entity_html))},
                step=iteration,
            )
            self.wandb_logger.log(
                {"Relation Extraction Examples": wandb.Html(open(relation_html))},
                step=iteration,
            )

        self.exporter.export(filename=f"sample_{suffix}.json")

    def setup(self, trainer: Engine, evaluator: Engine) -> None:
        self.global_step_transform = global_step_from_engine(trainer)

        evaluator.add_event_handler(Events.EPOCH_STARTED, self.reset)
        evaluator.add_event_handler(Events.ITERATION_COMPLETED, self.update)
        evaluator.add_event_handler(Events.EPOCH_COMPLETED, self.export)
