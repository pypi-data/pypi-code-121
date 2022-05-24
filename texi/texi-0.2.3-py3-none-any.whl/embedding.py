# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from collections.abc import Container
from typing import Optional, Union

import numpy as np


def load_vectors(
    filename: Union[str, os.PathLike],
    skip_headers: int = 0,
    word_only: bool = False,
    vocab: Optional[Container[str]] = None,
    keep_case: bool = False,
    sep: str = " ",
) -> Union[list[str], dict[str, np.ndarray]]:
    with open(filename) as f:
        for i in range(skip_headers):
            f.readline()

        dim = -1
        words, vectors = [], []
        for i, line in enumerate(f):
            # Split line.
            word, remains = line.rstrip().split(sep, 1)

            # Parse word.
            if not keep_case:
                word = word.lower()
            if vocab is not None and word not in vocab:
                continue
            words += [word]

            # Parse vector.
            if not word_only:
                vector = [float(x) for x in remains.split(sep)]
                if dim > 0 and len(vector) != dim:
                    raise ValueError(
                        f"Inconsistent vector size at line: {skip_headers + i}"
                    )
                vectors += [np.asarray(vector, dtype=np.float32)]
                dim = len(vector)

        if word_only:
            return words

        return dict(zip(words, vectors))
