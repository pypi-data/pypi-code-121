# -*- coding: utf-8 -*-

from __future__ import annotations

import itertools
import random
from typing import Optional

from texi.apps.ner.utils import Entity, NerExample, Relation


def sample_negative_entities(
    example: NerExample,
    max_length: int,
    size: Optional[int] = None,
    negative_entity_type: str = "NEGATIVE_ENTITY",
) -> list[Entity]:
    text = example["tokens"]
    positives = example["entities"]
    positive_tuples = {(x["start"], x["end"]) for x in positives}
    negatives = []
    for length in range(1, max_length + 1):
        for i in range(0, len(text) - length + 1):
            negative_tuple = (i, i + length)
            if negative_tuple in positive_tuples:
                continue

            negative: Entity = {
                "type": negative_entity_type,
                "start": i,
                "end": i + length,
            }
            negatives += [negative]

    if size is not None:
        negatives = random.sample(negatives, min(len(negatives), size))

    return negatives


def sample_negative_relations(
    example: NerExample,
    size: Optional[int] = None,
    negative_relation_type: str = "NEGATIVE_RELATION",
) -> list[Relation]:
    entities = example["entities"]
    if not entities:
        return []

    positive_tuples = {(r["head"], r["tail"]) for r in example["relations"]}

    negatives = []
    for i, j in itertools.product(range(len(entities)), repeat=2):
        if i != j and (i, j) not in positive_tuples:
            negative: Relation = {
                "head": i,
                "tail": j,
                "type": negative_relation_type,
            }
            negatives += [negative]

    if size is not None:
        negatives = random.sample(negatives, min(len(negatives), size))

    return negatives


class SpanNerNegativeSampler(object):
    def __init__(
        self,
        max_entity_length: int,
        num_negative_entities: Optional[int] = None,
        num_negative_relations: Optional[int] = None,
        negative_entity_type: str = "NEGATIVE_ENTITY",
        negative_relation_type: str = "NEGATIVE_RELATION",
    ) -> None:
        self.num_negative_entities = num_negative_entities
        self.num_negative_relations = num_negative_relations
        self.max_entity_length = max_entity_length
        self.negative_entity_type = negative_entity_type
        self.negative_relation_type = negative_relation_type

    def sample_negative_entities(self, example: NerExample) -> list[Entity]:
        return sample_negative_entities(
            example,
            self.max_entity_length,
            size=self.num_negative_entities,
            negative_entity_type=self.negative_entity_type,
        )

    def sample_negative_relations(self, example: NerExample) -> list[Relation]:
        return sample_negative_relations(
            example,
            size=self.num_negative_relations,
            negative_relation_type=self.negative_relation_type,
        )
