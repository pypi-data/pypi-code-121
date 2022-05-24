# -*- coding: utf-8 -*-

from __future__ import annotations

import itertools
import json
import os
from collections.abc import Iterable
from typing import Optional, Type, TypeVar, Union

import torch


class LabelEncoder(object):
    T = TypeVar("T", bound="LabelEncoder")

    def __init__(
        self, labels: Optional[Iterable[str]] = None, default: Optional[str] = None
    ) -> None:
        self.default = default
        self.init(labels)

    def __len__(self):
        return len(self.index2label)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(labels={self.labels!r}, default={self.default!r})"
        )

    @property
    def labels(self):
        return list(self.label2index)

    @property
    def num_labels(self):
        return len(self)

    @property
    def default_index(self):
        return self.get_index(self.default)

    def reset(self) -> None:
        self.index2label = {}
        self.label2index = {}

        if self.default:
            self.label2index[self.default] = 0
            self.index2label[0] = self.default

    def init(self, labels: Optional[Iterable[str]]) -> None:
        self.reset()

        if not labels:
            return

        for label in labels:
            self.label2index.setdefault(label, len(self.label2index))

        self.index2label = {v: k for k, v in self.label2index.items()}

    def add(self, label: str) -> int:
        index = self.label2index.setdefault(label, len(self))
        self.index2label.setdefault(index, label)

        return index

    def get_index(self, label: str) -> int:
        index = self.label2index.get(label)
        if index is None:
            if self.default is not None:
                return 0

            raise KeyError(label)

        return index

    def get_label(self, index: int) -> str:
        label = self.index2label.get(index)
        if label is None:
            if self.default is not None:
                return self.default

            raise KeyError(index)

        return label

    def encode_label(
        self, label: str, return_tensors: Optional[str] = None
    ) -> Union[int, torch.Tensor]:
        index = self.get_index(label)

        if return_tensors == "pt":
            return torch.tensor(index, dtype=torch.int64)

        if isinstance(return_tensors, str):
            raise ValueError('`return_tensors` should be "pt" or None')

        return index

    def decode_label(self, index: Union[int, torch.Tensor]) -> str:
        if isinstance(index, torch.Tensor):
            if index.ndim > 0:
                raise ValueError(
                    f"tensor should be 0-d tensor, got: ndim == {index.ndim}"
                )
            index = int(index.cpu().numpy())

        if not isinstance(index, int):
            raise ValueError(
                "`index` should be int or torch.Tensor, "
                f"got: {index.__class__.__name__}"
            )

        return self.get_label(index)

    def encode(
        self, labels: Iterable[str], return_tensors: Optional[str] = None
    ) -> Union[list[int], torch.Tensor]:
        indices = [self.get_index(x) for x in labels]
        if return_tensors == "pt":
            return torch.tensor(indices, dtype=torch.int64)

        if isinstance(return_tensors, str):
            raise ValueError('`return_tensors` should be "pt" or None')

        return indices

    def decode(self, indices: Union[torch.Tensor, Iterable[int]]) -> list[str]:
        if isinstance(indices, torch.Tensor):
            if indices.ndim != 1:
                raise ValueError(
                    f"tensor should be 1-d tensor, got: ndim == {indices.ndim}"
                )
            indices = indices.cpu().numpy()

        labels = [self.get_label(x) for x in indices]

        return labels

    def save(self, filename: Union[str, os.PathLike]) -> None:
        with open(filename, mode="w", encoding="utf-8") as f:
            data = {
                "labels": self.labels,
                "default": self.default,
            }
            json.dump(data, f, ensure_ascii=False, indent=4)

    @classmethod
    def from_iterable(cls: Type[T], labels: Iterable[Iterable[str]]) -> T:
        return cls(itertools.chain.from_iterable(labels))

    @classmethod
    def load(cls: Type[T], filename: Union[str, os.PathLike]) -> T:
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)

            return cls(data["labels"], default=data["default"])
