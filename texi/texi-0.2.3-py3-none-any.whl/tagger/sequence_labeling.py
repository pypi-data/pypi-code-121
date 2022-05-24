# -*- coding: utf-8 -*-

from __future__ import annotations

import abc
import collections
import itertools
import os
from collections.abc import Iterable, Mapping
from typing import TypedDict, Union


class Tagged(TypedDict):
    tokens: list[str]
    labels: list[str]


class SequeceLabelingTagger(metaclass=abc.ABCMeta):
    def __init__(self, type_field: str = "type", span_field: str = "span") -> None:
        self.type_field = type_field
        self.span_field = span_field

    def _iter_spans(self, spans):
        for chunk in spans:
            if isinstance(chunk, collections.abc.Mapping):
                type_, start, end = (
                    chunk[self.type_field],
                    int(chunk["start"]),
                    int(chunk["end"]),
                )
            else:
                type_, start, end = chunk
                start, end = int(start), int(end)

            yield type_, start, end

    @abc.abstractmethod
    def encode(self, inputs: Mapping) -> Tagged:
        raise NotImplementedError()

    @abc.abstractmethod
    def decode(self, inputs: Tagged) -> dict:
        raise NotImplementedError()

    @staticmethod
    def from_text(filename: Union[str, os.PathLike], sep: str = "\t") -> list[Tagged]:
        examples: list[Tagged] = []
        example: list[list[str]] = []

        with open(filename) as f:
            for line in f:
                line = line.rstrip()

                if not line:
                    if example:
                        tokens, spans = zip(*example)
                        examples += [{"tokens": list(tokens), "labels": list(spans)}]
                        example = []
                    continue

                example += [line.split(sep)]

        return examples

    @classmethod
    def to_text(
        cls,
        filename: Union[str, os.PathLike],
        examples: Iterable[Tagged],
        sep: str = "\t",
    ) -> None:
        with open(filename, mode="w") as f:
            for example in examples:
                f.writelines(
                    itertools.chain(
                        f"{token}{sep}{label}\n"
                        for token, label in zip(example["tokens"], example["labels"])
                    )
                )
                f.writelines("\n")


class IOB1(SequeceLabelingTagger):
    def encode(self, inputs: Mapping) -> Tagged:
        tokens, spans = inputs["tokens"], inputs[self.span_field]

        labels = ["O"] * len(tokens)
        for label, start, end in self._iter_spans(spans):
            I_label, B_label = f"I-{label}", f"B-{label}"
            labels[start:end] = [I_label] * (end - start)
            if start > 0 and labels[start - 1] in {I_label, B_label}:
                labels[start] = f"B-{label}"

        return {"tokens": tokens, "labels": labels}

    def decode(self, inputs: Tagged) -> dict:
        tokens, labels = inputs["tokens"], inputs["labels"]

        spans = []
        start = -1
        current_label = None
        for i, label in enumerate(labels):
            if label == "O":
                prefix, label = label, None  # type: ignore
            else:
                prefix, label = label.split("-")

            if prefix == "I" and label == current_label:
                continue

            if current_label and start >= 0:
                spans += [
                    {
                        self.type_field: current_label,
                        "start": start,
                        "end": i,
                    }
                ]
                start = -1
                current_label = None

            if (
                prefix == "B"
                or prefix == "I"
                and not current_label
                or label != current_label
            ):
                start = i
                current_label = label

        if prefix != "O":
            spans += [
                {
                    self.type_field: label,
                    "start": start,
                    "end": len(tokens),
                }
            ]

        return {"tokens": tokens, self.span_field: spans}


class IOB2(SequeceLabelingTagger):
    def encode(self, inputs: Mapping) -> Tagged:
        tokens, spans = inputs["tokens"], inputs[self.span_field]

        labels = ["O"] * len(tokens)
        for label, start, end in self._iter_spans(spans):
            labels[start] = f"B-{label}"
            labels[start + 1 : end] = [f"I-{label}"] * (end - start - 1)

        return {"tokens": tokens, "labels": labels}

    def decode(self, inputs: Tagged) -> dict:
        tokens, labels = inputs["tokens"], inputs["labels"]

        spans = []
        start = -1
        current_label = None
        for i, label in enumerate(labels):
            if label == "O":
                prefix, label = label, None  # type: ignore
            else:
                prefix, label = label.split("-")

            if prefix == "I" and label == current_label:
                continue

            if current_label and start >= 0:
                spans += [
                    {
                        self.type_field: current_label,
                        "start": start,
                        "end": i,
                    }
                ]
                start = -1
                current_label = None

            if prefix == "B":
                start = i
                current_label = label

        if prefix != "O":
            spans += [
                {
                    self.type_field: label,
                    "start": start,
                    "end": len(tokens),
                }
            ]

        return {"tokens": tokens, self.span_field: spans}


class IOBES(SequeceLabelingTagger):
    def encode(self, inputs: Mapping) -> Tagged:
        tokens, spans = inputs["tokens"], inputs[self.span_field]

        labels = ["O"] * len(tokens)
        for label, start, end in self._iter_spans(spans):
            if start + 1 == end:
                labels[start] = f"S-{label}"
            else:
                labels[start] = f"B-{label}"
                labels[start + 1 : end - 1] = [f"I-{label}"] * (end - start - 2)
                labels[end - 1] = f"E-{label}"

        return {"tokens": tokens, "labels": labels}

    def decode(self, inputs: Tagged) -> dict:
        tokens, labels = inputs["tokens"], inputs["labels"]

        spans = []
        start = -1
        current_label = None
        for i, label in enumerate(labels):
            if label == "O":
                prefix, label = label, None  # type: ignore
            else:
                prefix, label = label.split("-")

            if prefix == "S":
                spans += [{self.type_field: label, "start": i, "end": i + 1}]
                start = -1
                current_label = None
                continue

            if prefix == "I":
                if label == current_label:
                    continue

                start = -1
                current_label = None

            if prefix == "E":
                if current_label and start >= 0 and label == current_label:
                    spans += [
                        {
                            self.type_field: current_label,
                            "start": start,
                            "end": i + 1,
                        }
                    ]
                start = -1
                current_label = None

            if prefix == "B":
                start = i
                current_label = label

        return {"tokens": tokens, self.span_field: spans}
