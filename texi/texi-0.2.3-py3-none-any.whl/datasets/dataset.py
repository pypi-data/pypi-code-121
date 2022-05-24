# -*- coding: utf-8 -*-

from __future__ import annotations

import abc
import collections
import glob
import itertools
import json
import logging
import os
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, Generic, Optional, Type, TypeVar, Union, cast

from carton.logger import log_dict
from torchlight.utils.phase import ModeKeys

T_co = TypeVar("T_co", covariant=True)

logger = logging.getLogger(__name__)


class DatasetTransformMixin(Iterable, metaclass=abc.ABCMeta):
    _mixin_attributes: list[str] = []
    _mixin_transform: Optional[str] = None
    _mixin_inverse_transform: Optional[str] = None
    __iter__: Callable
    __getitem__: Callable

    def _check_transform(self):
        if any(hasattr(self, x) for x in self._mixin_attributes):
            raise RuntimeError(f"Can not call `.{self._mixin_transform}()` twice.")

    def _check_inverse_transform(self):
        if any(not hasattr(self, x) for x in self._mixin_attributes):
            raise RuntimeError(
                f"Can not call `.{self._mixin_inverse_transform}()`"
                f" before `.{self._mixin_transform}()`."
            )

    def _remove_attributes(self):
        for attr in self._mixin_attributes:
            delattr(self, attr)


class SplitableMixin(DatasetTransformMixin):
    _mixin_attributes = ["_split_lengths"]
    _mixin_transform = "split"
    _mixin_inverse_transform = "merge"

    def split(self, fn: Callable) -> None:
        self._check_transform()

        splits = [fn(x) for x in self]
        lengths = [len(x) for x in splits]

        self._split_lengths = lengths

        self.examples = list(itertools.chain.from_iterable(splits))

    def merge(self, fn: Callable) -> None:
        self._check_inverse_transform()

        examples = []

        offset = 0
        for length in self._split_lengths:
            examples += [fn(self[offset : offset + length])]
            offset += length

        self.examples = examples

        self._remove_attributes()


class MaskableMixin(DatasetTransformMixin):
    _mixin_attributes = [
        "_masked_positives",
        "_masked_negatives",
    ]
    _mixin_transform = "mask"
    _mixin_inverse_transform = "unmask"

    def mask(self, fn: Callable) -> None:
        self._check_transform()

        positives, negatives = [], []
        for i, example in enumerate(self):
            flag = fn(example)
            if flag:
                positives += [(i, example)]
            else:
                negatives += [(i, example)]

        self._masked_positives = positives
        self._masked_negatives = negatives

        self.examples = [x[1] for x in positives]

    def unmask(self) -> None:
        self._check_inverse_transform()

        examples = sorted(
            self._masked_positives + self._masked_negatives, key=lambda x: x[0]
        )

        self.examples = [x[1] for x in examples]

        self._remove_attributes()


class Dataset(MaskableMixin, SplitableMixin, Generic[T_co]):
    T = TypeVar("T", bound="Dataset")

    def __init__(
        self,
        examples: Union[Iterable[T_co], Callable[[], Iterable[T_co]]],
        mode: ModeKeys = ModeKeys.TRAIN,
    ) -> None:
        if callable(examples):
            self.load_examples = examples  # type: Optional[Callable]
            self.examples = None  # type: ignore
        else:
            self.examples = list(examples)
            self.load_examples = None

        self.mode = mode

    def __getitem__(self, key) -> T_co:
        self._check_loaded()

        return self.examples[key]

    def __iter__(self):
        if self.examples is not None:
            yield from iter(self.examples)
        elif callable(self.load_examples):
            yield from self.load_examples()

    def __len__(self):
        self._check_loaded()

        return len(self.examples)

    def __repr__(self):
        if self.examples is None:
            return f"{self.__class__.__name__}(Not loaded)"

        return f"{self.__class__.__name__}({len(self)} examples)"

    def _check_loaded(self):
        if self.examples is None:
            raise RuntimeError("Dataset is not loaded, call `.load()` first")

    def load(self: T) -> T:
        if callable(self.load_examples) and self.examples is None:
            self.examples = list(self.load_examples())

        return self

    def map(self, fn: Callable[..., Union[T_co, Sequence[T_co]]]) -> None:
        self._check_loaded()

        examples = [fn(x) for x in cast(list, self.examples)]
        if examples and isinstance(examples[0], list):
            examples = list(itertools.chain.from_iterable(examples))  # type: ignore

        self.examples = examples

    def describe(self) -> dict[str, Any]:
        return {
            "size": len(self)
            if isinstance(self.examples, collections.abc.Sized)
            else "-"
        }

    @staticmethod
    def map_modekeys(mode):
        return {
            "train": ModeKeys.TRAIN,
            "val": ModeKeys.EVAL,
            "test": ModeKeys.PREDICT,
        }[mode]

    @staticmethod
    def map_modes(mode):
        return {
            ModeKeys.TRAIN: "train",
            ModeKeys.EVAL: "val",
            ModeKeys.PREDICT: "test",
        }[mode]

    @classmethod
    def from_json(
        cls: Type[T],
        filename: Union[str, os.PathLike],
        format_function: Optional[Callable] = lambda x: x,
        array: bool = False,
        mode: ModeKeys = ModeKeys.TRAIN,
    ) -> T:
        def _iter_whole_file():
            with open(filename) as f:
                yield from map(format_function, json.load(f))

        def _iter_multiple_lines():
            with open(filename) as f:
                for line in f:
                    line = line.rstrip()
                    if line:
                        yield format_function(json.loads(line))

        def _iter_dir():
            for json_file in glob.iglob(
                os.path.join(filename, "**/*.json"), recursive=True
            ):
                with open(json_file) as f:
                    yield format_function(json.load(f))

        if os.path.isdir(filename):
            fn = _iter_dir
        else:
            fn = _iter_whole_file if array else _iter_multiple_lines

        return cls(fn, mode=mode)


T_Dataset = TypeVar("T_Dataset", bound="Dataset")


class Datasets(Generic[T_Dataset]):
    T = TypeVar("T", bound="Datasets")

    def __init__(
        self,
        train: Optional[Union[T_Dataset, Iterable, Callable]] = None,
        val: Optional[Union[T_Dataset, Iterable, Callable]] = None,
        test: Optional[Union[T_Dataset, Iterable, Callable]] = None,
        dirname: Optional[Union[str, os.PathLike]] = None,
        filename: Optional[Union[str, os.PathLike]] = None,
    ) -> None:
        def _wrap(d):
            if d is not None and not isinstance(d, Dataset):
                return Dataset(d)

            return d

        self.train = _wrap(train)
        self.val = _wrap(val)
        self.test = _wrap(test)
        self.dirname = dirname
        self.filename = filename

        self.modes = {"train", "val", "test"}

    def __getitem__(self, key) -> T_Dataset:
        assert key in self.modes

        return getattr(self, key)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(train={self.train}"
            f", val={self.val}, test={self.test}"
            f", dirname={self.dirname!r}, filename={self.filename!r})"
        )

    def _map_dataset_methods(self, method, *args, **kwargs):
        outputs = dict.fromkeys(self.modes)
        for mode, dataset in self.items():
            if dataset is not None:
                outputs[mode] = getattr(dataset, method)(*args, **kwargs)

        return outputs

    def load(self: T) -> T[T_Dataset]:
        for mode in self.modes:
            dataset = getattr(self, mode)
            if dataset is not None:
                dataset.load()

        return self

    def items(self) -> Iterable[tuple[str, T_Dataset]]:
        for mode in self.modes:
            yield mode, getattr(self, mode)

    def to_dict(self) -> dict[str, Optional[Dataset]]:
        return {
            "train": self.train,
            "val": self.val,
            "test": self.test,
        }

    def map(self, fn: Callable) -> None:
        self._map_dataset_methods("map", fn)

    def split(self, fn: Callable) -> None:
        self._map_dataset_methods("split", fn)

    def mask(self, fn: Callable) -> None:
        self._map_dataset_methods("mask", fn)

    def describe(self):
        for mode, dataset in self.items():
            if dataset is not None:
                logger.info("Dataset info [%s]: ", mode)
                log_dict(logger, dataset.describe())

    @classmethod
    def format(cls: Type[T], x: Any) -> Any:
        return x

    @classmethod
    def from_dir(
        cls: Type[T],
        dirname: Union[str, os.PathLike],
    ) -> T:
        raise NotImplementedError()

    @classmethod
    def from_json(
        cls: Type[T],
        dirname: Union[str, os.PathLike],
        *args,
        array: bool = False,
        class_: Type[Dataset] = Dataset,
        files: Optional[Mapping[str, str]] = None,
        **kwargs,
    ) -> T:
        # pylint: disable=arguments-differ

        if files is None:
            files = {
                "train": "train.json",
                "val": "val.json",
                "test": "test.json",
            }

        data = {
            key: class_.from_json(
                os.path.join(dirname, value),
                cls.format,
                *args,
                array=array,
                mode=Dataset.map_modekeys(key),
                **kwargs,
            )
            for key, value in files.items()
        }  # type: dict[str, Dataset[dict]]

        return cls(
            train=data["train"], val=data["val"], test=data["test"], dirname=dirname
        )


class JSONDatasets(Datasets):
    T = TypeVar("T", bound="JSONDatasets")

    files = {
        "train": "train.json",
        "val": "val.json",
        "test": "test.json",
    }

    @classmethod
    def from_dir(
        cls: Type[T],
        dirname: Union[str, os.PathLike],
        array: bool = False,
    ) -> T:
        # pylint: disable=arguments-differ

        return cls.from_json(dirname, array=array, files=cls.files)
