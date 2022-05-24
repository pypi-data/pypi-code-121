# -*- coding: utf-8 -*-

from __future__ import annotations

import collections
import copy
import dataclasses
import json
import os
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Optional, TypedDict, Union, cast

from carton.collections import dict_to_tuple
from carton.data import describe_series
from torchlight.preprocessing import LabelEncoder


class NerExample(TypedDict, total=False):
    id: Optional[str]
    tokens: list[str]
    entities: list[Entity]
    relations: list[Relation]


class Entity(TypedDict, total=False):
    id: Optional[str]
    type: str
    start: int
    end: int


class Relation(TypedDict, total=False):
    id: Optional[str]
    type: str
    head: int
    tail: int


class RelationExpanded(TypedDict, total=False):
    id: Optional[str]
    type: str
    head: Entity
    tail: Entity


def entity_to_tuple(entity: Entity) -> tuple:
    return dict_to_tuple(entity, ["type", "start", "end"])


def relation_to_tuple(
    relation: Relation, entities: Optional[list[Entity]] = None
) -> tuple:
    def _convert_entity(entity):
        if isinstance(entity, Mapping):
            return entity_to_tuple(entity)

        if entities:
            return entities[entity]

        return entity

    return (
        relation["type"],
        _convert_entity(relation["head"]),
        _convert_entity(relation["tail"]),
    )


def expand_tokens(entities: Iterable[Entity], tokens: Sequence[str]) -> list[dict]:
    return [
        {
            "type": entity["type"],
            "start": entity["start"],
            "end": entity["end"],
            "tokens": tokens[entity["start"] : entity["end"]],
        }
        for entity in entities
    ]


def expand_entities(
    relations: Iterable[Relation], entities: Sequence[Entity]
) -> list[dict]:
    return [
        {
            "type": relation["type"],
            "head": dict(entities[relation["head"]]),
            "tail": dict(entities[relation["tail"]]),
        }
        for relation in relations
    ]


def collapse_entities(
    relations: Iterable[RelationExpanded], entities: Iterable[Entity]
) -> list[Relation]:
    entity_indices = {entity_to_tuple(entity): i for i, entity in enumerate(entities)}

    return [
        {
            "type": str(relation["type"]),
            "head": int(entity_indices[entity_to_tuple(relation["head"])]),
            "tail": int(entity_indices[entity_to_tuple(relation["tail"])]),
        }
        for relation in relations
    ]


def encode_labels(
    examples: Iterable[NerExample],
    negative_entity_type: Optional[str] = None,
    negative_relation_type: Optional[str] = None,
) -> tuple[LabelEncoder, LabelEncoder]:
    entity_label_encoder = LabelEncoder(default=negative_entity_type)
    relation_label_encoder = LabelEncoder(default=negative_relation_type)

    for example in examples:
        for entity in example["entities"]:
            entity_label_encoder.add(entity["type"])

        for relation in example["relations"]:
            relation_label_encoder.add(relation["type"])

    return entity_label_encoder, relation_label_encoder


def compare_prediction_with_ground_truth(
    example: NerExample,
    entity_predictions: Sequence[Entity],
    relation_predictions: Sequence[Relation],
    entity_scores: Iterable[float],
    relation_scores: Iterable[float],
) -> dict[str, list[dict]]:
    def _compare(y, y_pred, f, scores):
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

    diff = {
        "tokens": example["tokens"],
        "entities": _compare(
            example["entities"], entity_predictions, entity_to_tuple, entity_scores
        ),
        "relations": _compare(
            expand_entities(example["relations"], example["entities"]),
            expand_entities(relation_predictions, entity_predictions),
            relation_to_tuple,
            relation_scores,
        ),
    }

    return diff


def from_pybrat_example(example: Mapping) -> NerExample:
    # NOTE:
    # 1. ID fields are kept.
    # 2. Entities are sort before conversion.

    # Convert tokens.
    tokens: list[str] = list(example["text"])

    # Record entity indices.
    entities = sorted(example["entities"], key=lambda x: x["start"])

    # Convert relation.
    entity_indices = {x["id"]: i for i, x in enumerate(entities)}
    converted_relations: list[Relation] = [
        {
            "id": x["id"],
            "type": x["type"],
            "head": entity_indices[x["arg1"]["id"]],
            "tail": entity_indices[x["arg2"]["id"]],
        }
        for x in example["relations"]
    ]

    # Convert entities.
    converted_entities: list[Entity] = [
        {
            "id": x["id"],
            "type": x["type"],
            "start": x["start"],
            "end": x["end"],
        }
        for x in entities
    ]

    return {
        "id": example["id"],
        "tokens": tokens,
        "entities": converted_entities,
        "relations": converted_relations,
    }


def to_pybrat_example(example: NerExample, delimiter: str = "") -> dict:
    def _new_id_builder(prefix):
        i = 1

        def _new_id():
            nonlocal i

            while True:
                yield f"{prefix}{i}"
                i += 1

        return _new_id()

    token_lengths = [len(x) for x in example["tokens"]]
    offsets = [0]
    for length in token_lengths:
        offsets += [offsets[-1] + length + len(delimiter)]
    assert len(offsets) == len(example["tokens"]) + 1

    entities = []
    entity_id = _new_id_builder("T")
    for entity in example["entities"]:
        entity_slice = slice(entity["start"], entity["end"])

        pybrat_entity = {
            "id": next(entity_id),
            "word": delimiter.join(example["tokens"][entity_slice]),
            "type": entity["type"],
            "start": offsets[entity["start"]],
            "end": offsets[entity["end"]] - len(delimiter),
        }

        entities += [pybrat_entity]

    relation_id = _new_id_builder("R")
    relations = [
        {
            "id": next(relation_id),
            "type": x["type"],
            "arg1": entities[x["head"]],
            "arg2": entities[x["tail"]],
        }
        for x in example["relations"]
    ]

    return {
        "text": delimiter.join(example["tokens"]),
        "entities": entities,
        "relations": relations,
    }


def load_pybrat_examples(
    dirname: Union[str, os.PathLike], *args, **kwargs
) -> list[NerExample]:
    # pylint: disable=import-outside-toplevel
    from pybrat.parser import BratParser

    parser = BratParser(*args, **kwargs)
    parsed = parser.parse(dirname)

    examples = []
    for parsed_example in parsed:
        example = from_pybrat_example(dataclasses.asdict(parsed_example))
        examples += [example]

    return examples


def convert_pybrat_examples(
    input_dir: Union[str, os.PathLike],
    output_dir: Union[str, os.PathLike],
    test_size: float = 0.2,
    val_size: float = 0.1,
    shuffle: bool = True,
    random_state: Optional[int] = None,
    **kwargs,
) -> None:
    # pylint: disable=import-outside-toplevel
    from sklearn.model_selection import train_test_split

    def _optional_split(data, size):
        if size > 0:
            first, second = train_test_split(
                data, test_size=size, shuffle=shuffle, random_state=random_state
            )
        else:
            first, second = data, None

        return first, second

    # Load examples.
    examples = load_pybrat_examples(input_dir, **kwargs)

    # Split examples.
    train, test = _optional_split(examples, test_size)
    train, val = _optional_split(train, val_size)

    # Dump examples.
    prefix = os.path.basename(input_dir)
    os.makedirs(output_dir, exist_ok=True)
    datasets = {
        "train": train,
        "val": val,
        "test": test,
    }
    for mode, dataset in datasets.items():
        if dataset is not None:
            with open(
                os.path.join(str(output_dir), f"{prefix!s}_{mode}.json"), mode="w"
            ) as f:
                json.dump(dataset, f, ensure_ascii=False)


def check_example(example: NerExample) -> bool:
    if len(example["tokens"]) < 1:
        raise ValueError("`example` has no tokens")

    num_tokens = len(example["tokens"])
    for entity in example.get("entities", []):
        if entity["start"] >= entity["end"]:
            raise ValueError(f"Invalid entity span: {entity}")

        if (
            entity["start"] >= num_tokens
            or entity["end"] >= num_tokens
            or entity["start"] < 0
            or entity["end"] < 0
        ):
            raise ValueError(f"Entity token out of bound: {entity}")

    num_entities = len(example.get("entities", []))
    for relation in example.get("relations", []):
        if relation["head"] >= num_entities or relation["tail"] >= num_entities:
            raise ValueError(f"Entity not found for relation: {relation}")

        if relation["head"] == relation["tail"]:
            raise ValueError(
                f"Relation should have different head and tail: {relation}"
            )

    return True


def describe_examples(examples: Iterable[NerExample], r: int = 4) -> dict:
    def _compute_frequency(counter):
        total = sum(counter.values())

        return {key: round(value / total, r) for key, value in counter.items()}

    examples = list(examples)

    entity_type_counter = collections.Counter()  # type: collections.Counter[str]
    relation_type_counter = collections.Counter()  # type: collections.Counter[str]

    num_tokens, num_entities, num_relations = [], [], []
    entity_sizes = []
    for x in examples:
        entities, relations = x.get("entities", []), x.get("relations", [])

        num_tokens += [len(x["tokens"])]
        num_entities += [len(entities)]
        num_relations += [len(relations)]

        for entity in entities:
            entity_sizes += [entity["end"] - entity["start"]]
            entity_type_counter[entity["type"]] += 1

        for relation in relations:
            relation_type_counter[relation["type"]] += 1

    return {
        "token": {
            "count": describe_series(num_tokens, r=r),
        },
        "entity": {
            "type": {
                "count": dict(entity_type_counter),
                "frequency": _compute_frequency(entity_type_counter),
            },
            "count": describe_series(num_entities, r=r),
            "size": describe_series(entity_sizes, r=r),
        },
        "relation": {
            "type": {
                "count": dict(relation_type_counter),
                "frequency": _compute_frequency(relation_type_counter),
            },
            "count": describe_series(num_relations, r=r),
        },
    }


def filter_example_tokens(
    example: NerExample,
    filters: Iterable[Union[str, re.Pattern, Callable[[str], bool]]],
) -> NerExample:
    if not hasattr(filters, "__iter__") or isinstance(filters, str):
        filters = [filters]  # type: ignore

    for f in filters:
        if not isinstance(f, (str, re.Pattern)) and not callable(f):
            raise ValueError(
                "Filter should be str, re.Pattern or Callable,"
                f" not: {f.__class__.__name__}"
            )

    def _filter(x):
        for f in filters:
            if isinstance(f, re.Pattern):
                if re.match(f, x):
                    return True

            elif isinstance(f, str):
                if f == x:
                    return True

            elif callable(f):
                if f(x):
                    return True

        return False

    backup = example
    example = copy.deepcopy(example)
    entities = sorted(enumerate(example["entities"]), key=lambda x: x[1]["start"])

    entity_index = 0
    num_entities = len(entities)
    tokens = example["tokens"]
    num_tokens = len(tokens)
    i = 0
    while i < num_tokens:
        if _filter(tokens[i]):
            while entity_index < num_entities and entities[entity_index][1]["end"] <= i:
                entity_index += 1

            if entity_index < num_entities and entities[entity_index][1]["start"] <= i:
                entity_tokens = tokens[
                    entities[entity_index][1]["start"] : entities[entity_index][1][
                        "end"
                    ]
                ]
                raise RuntimeError(f"Can not filter entity tokens: {entity_tokens}")

            j = entity_index
            while j < num_entities:
                entities[j][1]["start"] -= 1
                entities[j][1]["end"] -= 1
                j += 1

            tokens.pop(i)
            num_tokens -= 1
        else:
            i += 1

    example["tokens"] = tokens
    if entities:
        converted_entities: list[Entity] = list(
            list(zip(*sorted(entities, key=lambda x: x[0])))[1]
        )
    example["entities"] = converted_entities

    assert len(example["entities"]) == len(backup["entities"]), "Mismatched entity list"
    for i, entity in enumerate(example["entities"]):
        assert (
            example["tokens"][entity["start"] : entity["end"]]
            == backup["tokens"][
                backup["entities"][i]["start"] : backup["entities"][i]["end"]
            ]
        ), "Mismatched entity spans"

    return example


def split_example(
    example: NerExample,
    delimiters: Union[str, Iterable[str]],
    ignore_errors: bool = False,
) -> list[NerExample]:
    if isinstance(delimiters, str):
        delimiters = {delimiters}
    else:
        delimiters = set(delimiters)

    # Sorting entities may change indices.
    if not example["tokens"]:
        raise ValueError("`example` should at least contain one token")

    entities = list(example["entities"])
    relations = sorted(example["relations"], key=lambda x: (x["head"], x["tail"]))

    splits: list[NerExample] = []
    current_tokens: list[str] = []
    current_entities: list[Entity] = []
    current_relations: list[Relation] = []
    entity_index, relation_index = 0, 0
    for i, token in enumerate(example["tokens"] + [next(iter(delimiters))]):
        current_tokens += [token]

        if token in delimiters:
            # Collect entities.
            entity_indices = {}  # type: dict[int, int]
            while entity_index < len(entities) and entities[entity_index]["end"] <= i:
                entity_indices[entity_index] = len(entity_indices)
                entity = entities[entity_index]
                entity_start = len(current_tokens) - (i - entity["start"]) - 1
                entity_end = len(current_tokens) - (i - entity["end"]) - 1
                current_entity: Entity = {
                    "type": entities[entity_index]["type"],
                    "start": entity_start,
                    "end": entity_end,
                }
                current_entities += [current_entity]
                entity_index += 1
                entity_start += 1

            if entity_index < len(entities) and entities[entity_index]["start"] <= i:
                if ignore_errors:
                    entity_index += 1
                else:
                    raise RuntimeError(
                        "Entity must not contains delimiters,"
                        f" delimiters: {delimiters}, entity: {entities[entity_index]}"
                    )

            # Collect relations.
            while relation_index < len(relations):
                relation = relations[relation_index]
                head_index = entity_indices.get(relation["head"])
                tail_index = entity_indices.get(relation["tail"])
                in_range = bool(head_index is None) + bool(tail_index is None)
                if in_range == 1:
                    if ignore_errors:
                        relation_index += 1
                    else:
                        raise RuntimeError(
                            "Relation must not across delimiters,"
                            f" delimiters: {delimiters}, relation: {relation}"
                        )

                if in_range == 0:
                    current_relation: Relation = {
                        "type": relation["type"],
                        "head": cast(int, head_index),
                        "tail": cast(int, tail_index),
                    }
                    current_relations += [current_relation]
                    relation_index += 1
                else:
                    # This also implies that invalid relations will be drop.
                    break

            # Create new split.
            split: NerExample = {
                "tokens": current_tokens,
                "entities": current_entities,
                "relations": current_relations,
            }
            splits += [split]

            # Reset states.
            current_tokens, current_entities, current_relations = [], [], []

    if len(splits[-1]["tokens"]) == 1:
        splits.pop()
    else:
        splits[-1]["tokens"].pop()

    return splits


def merge_examples(examples: Sequence[NerExample]) -> NerExample:
    if len(examples) < 1:
        raise ValueError("At least one example must be given to merge")

    tokens: list[str] = []
    entities: list[Entity] = []
    relations: list[Relation] = []

    for example in examples:
        token_offset = len(tokens)

        # Collect tokens.
        tokens += example["tokens"]

        # Collect entities.
        entity_indices = {}
        num_entities_so_far = len(entities)
        for i, entity in enumerate(example["entities"]):
            new_entity: Entity = {
                "type": entity["type"],
                "start": entity["start"] + token_offset,
                "end": entity["end"] + token_offset,
            }
            entity_indices[i] = i + num_entities_so_far
            entities += [new_entity]

        # Collect relations.
        for relation in example["relations"]:
            new_relation: Relation = {
                "type": relation["type"],
                # `dict.get` is not used implies invalid relations should fail.
                "head": entity_indices[relation["head"]],
                "tail": entity_indices[relation["tail"]],
            }
            relations += [new_relation]

    return {
        "tokens": tokens,
        "entities": entities,
        "relations": relations,
    }


def texify_example(example: NerExample, delimiter: str) -> dict:
    entities = example["entities"]
    if not entities:
        return {
            "tokens": delimiter.join(example["tokens"]),
            "entities": entities,
            "relations": example["relations"],
        }

    num_tokens = len(example["tokens"])
    delimiter_length = len(delimiter)
    entity_index = 0
    entity = entities[entity_index]
    new_tokens, new_entities = [], []
    start = -1
    char_offset = 0
    for i, token in enumerate(example["tokens"]):
        if i == entity["end"]:
            if start < 0:
                raise ValueError(f"Invalid entity: {entity}")

            new_enitty = {
                "type": entity["type"],
                "start": start,
                "end": char_offset - delimiter_length,
            }
            new_entities += [new_enitty]

            entity_index += 1
            if entity_index < len(entities):
                start = -1
                entity = entities[entity_index]

        if i == entity["start"]:
            start = char_offset

        new_tokens += [token]
        char_offset += len(token)

        if i < num_tokens - 1:
            new_tokens += [delimiter]
            char_offset += delimiter_length

    return {
        "tokens": "".join(new_tokens),
        "entities": new_entities,
        "relations": example["relations"],
    }
