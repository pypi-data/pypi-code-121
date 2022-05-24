# -*- coding: utf-8 -*-

from __future__ import annotations

import itertools
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Union

import torch
from carton.collections import collate, flatten_dict
from torchlight.dataset import Collator
from torchlight.masking import create_span_mask
from torchlight.preprocessing import LabelEncoder
from torchlight.utils.phase import ModeKeys
from torchlight.utils.tensor import pad_stack_1d, pad_stack_2d

from texi.apps.ner.utils import Entity, NerExample, Relation, describe_examples
from texi.datasets import Dataset
from texi.pytorch.models.spert.sampler import SpERTSampler

if TYPE_CHECKING:
    from transformers import BertTokenizer, BertTokenizerFast


class SpERTDataset(Dataset):
    def describe(self) -> dict[str, Any]:
        info = super().describe()
        type_stats = flatten_dict(describe_examples(self.examples), sep="/")
        info.update(type_stats)

        return info


class SpERTCollator(Collator):
    def __init__(
        self,
        negative_sampler: SpERTSampler,
        tokenizer: Union[BertTokenizer, BertTokenizerFast],
        entity_label_encoder: LabelEncoder,
        relation_label_encoder: LabelEncoder,
        mode: ModeKeys = ModeKeys.TRAIN,
    ) -> None:
        super().__init__(mode=mode)

        self.tokenizer = tokenizer
        self.negative_sampler = negative_sampler
        self.entity_label_encoder = entity_label_encoder
        self.relation_label_encoder = relation_label_encoder

    def _encode_entities(self, entities, tokens):
        num_tokens = sum(map(len, tokens))

        if not entities:
            mask = torch.zeros((0, num_tokens), dtype=torch.int64)
            label = torch.zeros((0,), dtype=torch.int64)
            entity_span = torch.zeros((0, 2), dtype=torch.int64)
            sample_mask = torch.zeros((0,), dtype=torch.int64)

            return mask, label, entity_span, sample_mask

        # Compute encoded token offsets.
        offset, offsets = 0, []
        for token in tokens:
            offsets += [offset]
            offset += len(token)

        # Collect `entity_mask`, `entity_label`, `entity_span` and
        # `entity_sample_mask`.
        outputs = []
        for entity in entities:
            # `start` and `end` are the boundaries of the encoded tokens.
            start = offsets[entity["start"] + 1]
            end = offsets[entity["end"] - 1 + 1] + len(tokens[entity["end"] - 1 + 1])
            assert (
                start < end
            ), "Possibly found emtpy tokens after tokenizer encoding..."

            token_span = [start, end]
            label = self.entity_label_encoder.encode_label(entity["type"])

            # `entity["start"]` and `entity["end"]` are the boundaries
            # of the original tokens.
            entity_span = [entity["start"], entity["end"]]

            outputs += [(token_span, label, entity_span, 1)]

        outputs = [torch.tensor(x, dtype=torch.int64) for x in zip(*outputs)]
        token_span, label, entity_span, sample_mask = outputs
        mask = create_span_mask(token_span[:, 0], token_span[:, 1], num_tokens)

        return mask, label, entity_span, sample_mask

    def _encode_relations(self, relations, entity_mask, tokens):
        def _compute_context_span(head_mask, tail_mask):
            head_start, tail_start = head_mask.argmax(), tail_mask.argmax()
            head_end = head_start + head_mask.sum()
            tail_end = tail_start + tail_mask.sum()
            assert (
                head_start >= tail_end or tail_start >= head_end
            ), "Relations of overlapped entities are not allowed"

            return min(head_end, tail_end), max(head_start, tail_start)

        num_tokens = sum(map(len, tokens))

        if not relations:
            mask = torch.zeros((0, num_tokens), dtype=torch.int64)
            label = torch.zeros(
                (0, len(self.relation_label_encoder)), dtype=torch.int64
            )
            pair = torch.zeros((0, 2), dtype=torch.int64)
            sample_mask = torch.zeros((0,), dtype=torch.int64)

            return mask, label, pair, sample_mask

        # Collect `relation_context_mask`, `relation_label`,
        # `relation_pair` and `relation_sample_mask`.
        outputs = []
        for relation in relations:
            # Compute the relation context span based on encoded tokens.
            head_mask = entity_mask[relation["head"]]
            tail_mask = entity_mask[relation["tail"]]
            context = _compute_context_span(head_mask, tail_mask)

            label = self.relation_label_encoder.encode_label(relation["type"])
            pair = [relation["head"], relation["tail"]]

            outputs += [(context, label, pair, 1)]

        outputs = [torch.tensor(x, dtype=torch.int64) for x in zip(*outputs)]
        context, label, pair, sample_mask = outputs
        num_tokens = sum(map(len, tokens))
        mask = create_span_mask(context[:, 0], context[:, 1], num_tokens)
        label = torch.nn.functional.one_hot(label)

        return mask, label, pair, sample_mask

    def encode_example(
        self,
        tokens: Sequence[str],
        entities: Sequence[Entity],
        relations: Sequence[Relation],
    ) -> dict[str, Any]:
        # Encode tokens.
        tokens = [self.tokenizer.cls_token] + list(tokens) + [self.tokenizer.sep_token]
        output = self.tokenizer(tokens, add_special_tokens=False)

        # Encode entities.
        (
            entity_mask,
            entity_label,
            entity_span,
            entity_sample_mask,
        ) = self._encode_entities(entities, output["input_ids"])

        # Encode relations.
        (
            relation_context_mask,
            relation_label,
            relation,
            relation_sample_mask,
        ) = self._encode_relations(relations, entity_mask, output["input_ids"])

        output = {
            k: torch.tensor(list(itertools.chain.from_iterable(v)), dtype=torch.int64)
            for k, v in output.items()
        }

        return {
            "tokens": tokens,
            "input_ids": output["input_ids"],
            "attention_mask": output["attention_mask"],
            "token_type_ids": output["token_type_ids"],
            "entity_mask": entity_mask,
            "entity_label": entity_label,
            "entity_span": entity_span,
            "entity_sample_mask": entity_sample_mask,
            "relation_context_mask": relation_context_mask,
            "relation_label": relation_label,
            "relation": relation,
            "relation_sample_mask": relation_sample_mask,
        }

    def encode(
        self, example: NerExample
    ) -> Union[dict[str, Any], tuple[dict[str, Any], dict[str, Any]]]:
        tokens = example["tokens"]

        positive_entities = example["entities"]
        positive_relations = example["relations"]
        negative_entities = self.negative_sampler.sample_negative_entities(example)

        if self.is_train():
            negative_relations = self.negative_sampler.sample_negative_relations(
                example
            )
            entities = positive_entities + negative_entities
            relations = positive_relations + negative_relations

            return self.encode_example(tokens, entities, relations)

        return (
            self.encode_example(tokens, positive_entities, positive_relations),
            self.encode_example(tokens, positive_entities + negative_entities, []),
        )

    def _collate_internal(self, batch):
        max_length, max_entities = 0, 0
        for mask in batch["entity_mask"]:
            max_entities = max(max_entities, mask.size(0))
            max_length = max(max_length, mask.size(1))

        max_relations = 0
        for mask in batch["relation_context_mask"]:
            max_relations = max(max_relations, mask.size(0))

        input_ids = pad_stack_1d(batch["input_ids"], max_length)
        attention_mask = pad_stack_1d(batch["attention_mask"], max_length)
        token_type_ids = pad_stack_1d(batch["token_type_ids"], max_length)

        entity_mask = pad_stack_2d(batch["entity_mask"], max_entities, max_length)
        entity_label = pad_stack_1d(batch["entity_label"], max_entities)
        entity_span = pad_stack_2d(batch["entity_span"], max_entities, 2)
        entity_sample_mask = pad_stack_1d(batch["entity_sample_mask"], max_entities)

        relation_context_mask = pad_stack_2d(
            batch["relation_context_mask"], max_relations, max_length
        )
        relation_label = pad_stack_2d(
            batch["relation_label"], max_relations, len(self.relation_label_encoder)
        )
        relation = pad_stack_2d(batch["relation"], max_relations, 2)
        relation_sample_mask = pad_stack_1d(
            batch["relation_sample_mask"], max_relations
        )

        return {
            "tokens": batch["tokens"],
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
            "entity_mask": entity_mask,
            "entity_label": entity_label,
            "entity_span": entity_span,
            "entity_sample_mask": entity_sample_mask,
            "relation_context_mask": relation_context_mask,
            "relation_label": relation_label,
            "relation": relation,
            "relation_sample_mask": relation_sample_mask,
        }

    def collate_train(self, batch: Sequence[NerExample]) -> dict[str, torch.Tensor]:
        assert self.is_train(), "`collate_train` must be called in train mode"

        return self._collate_internal(collate(batch))

    def collate_eval(
        self, batch: Sequence[NerExample]
    ) -> Union[
        dict[str, torch.Tensor], tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]]
    ]:
        assert not self.is_train(), "`collate_train` must NOT be called in train mode"

        positives, negatives = zip(*batch)

        return (
            self._collate_internal(collate(positives)),
            self._collate_internal(collate(negatives)),
        )
