# -*- coding: utf-8 -*-

from __future__ import annotations

import collections
import itertools
import os
import sys
from collections.abc import Iterable, Sequence
from typing import Optional, Union

import numpy as np


class SpecialTokens(object):
    def __init__(
        self,
        pad: str = "[PAD]",
        unk: str = "[UNK]",
        bos: str = "[BOS]",
        eos: str = "[EOS]",
    ) -> None:
        self.pad = pad
        self.unk = unk
        self.bos = bos
        self.eos = eos


class Vocabulary(object):
    def __init__(
        self,
        docs: Optional[Union[str, Sequence[str], Sequence[Sequence[str]]]] = None,
        min_count: int = 1,
        max_size: int = sys.maxsize,
        keep_case: bool = False,
        specials: Iterable[str] = None,
        default: str = None,
    ):
        self.keep_case = keep_case
        if specials is None:
            specials = []
        else:
            specials = list(specials)
        if default is not None:
            specials += [default]
        if not self.keep_case:
            specials = [x.lower() for x in specials]
        self.specials = collections.OrderedDict.fromkeys(specials)
        self.default = default
        self.reset()

        if docs:
            self.learn(docs)
            self.trim(min_count=min_count, max_size=max_size)

    def __contains__(self, key):
        return key in self.freqs.keys()

    def __delitem__(self, word):
        if word in self.specials:
            raise ValueError("can not delete special token")

        if word not in self:
            return

        index = self.word2index[word]
        del self.word2index[word]
        del self.index2word[index]
        del self.freqs[word]

    def __getitem__(self, key):
        return self.get_index(key)

    def __len__(self):
        return len(self.freqs)

    @property
    def words(self):
        return set(self.freqs.keys())

    def _preprocess(self, word):
        if not self.keep_case:
            word = word.lower()

        return word

    def reset(self) -> None:
        self.freqs = collections.defaultdict(
            int, {w: float("inf") for w in self.specials}
        )
        self.word2index = {w: i for i, w in enumerate(self.freqs)}
        self.index2word = {i: w for w, i in self.word2index.items()}

    def add(self, word: str, freq: int = 1) -> None:
        word = self._preprocess(word)

        if word in self.specials:
            raise ValueError("can not add special token")

        if word not in self.freqs:
            self.word2index[word] = len(self)
            self.index2word[len(self)] = word
        self.freqs[word] += freq

    def learn(self, docs: Union[str, Sequence[str], Sequence[Sequence[str]]]) -> None:
        if isinstance(docs, str):
            self.add(docs)
            return

        if not isinstance(docs[0], str):
            for word in itertools.chain(*docs):
                self.add(word)
        else:
            for word in docs:  # type: ignore
                self.add(word)

    def compactify(self) -> None:
        freqs = {w: f for w, f in self.freqs.items() if w not in self.specials}
        self.reset()
        offset = len(self.freqs)
        for i, (w, f) in enumerate(freqs.items()):
            self.word2index.update({w: i + offset})
            self.index2word.update({i + offset: w})
            self.freqs.update({w: f})

    def trim(
        self,
        min_count: Optional[int] = None,
        max_size: Optional[int] = None,
        compactify: bool = False,
    ) -> None:
        if min_count:
            self.freqs = collections.defaultdict(
                int, {k: v for k, v in self.freqs.items() if v >= min_count}
            )

        if max_size is not None:
            if max_size < len(self.specials):
                raise ValueError("`max_size` too small")
            if len(self) > max_size:
                self.freqs = collections.defaultdict(
                    int, sorted(self.freqs.items(), key=lambda x: -x[1])[:max_size]
                )

        if compactify:
            self.compactify()

    def save(self, filename: Union[str, os.PathLike]) -> None:
        with open(filename, mode="w") as f:
            f.writelines(
                "\n".join(
                    [
                        f"{word}\t{freq}"
                        for word, freq in self.freqs.items()
                        if word not in set(self.specials)
                    ]
                )
            )

    def load(self, filename: Union[str, os.PathLike]) -> None:
        self.reset()

        with open(filename) as f:
            for line in f:
                line = line.strip()
                if line:
                    word, freq = line.split("")
                    if word in freq:
                        raise ValueError(f"Duplicate key: {word!r}")
                    self.add(word, int(freq))

    def get_index(self, word: str) -> int:
        word = self._preprocess(word)
        index = self.word2index.get(word)

        if index is not None:
            return index

        if self.default is not None:
            return self.word2index[self.default]

        raise KeyError(f"Word not found while `default` is not set: {word}")

    def get_word(self, index: Union[int, np.integer]) -> str:
        return self.index2word[int(index)]

    def transform(self, words: Union[str, Iterable[str]]) -> Union[int, list[int]]:
        if isinstance(words, str):
            return self.get_index(words)

        return [self.transform(word) for word in words]  # type: ignore

    def inverse_transform(
        self, ids: Union[int, np.integer, Iterable[Union[int, np.integer]]]
    ) -> Union[str, list[str]]:
        if isinstance(ids, (int, np.integer)):
            return self.get_word(ids)

        return [self.inverse_transform(x) for x in ids]  # type: ignore
