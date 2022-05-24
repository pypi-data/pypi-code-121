# -*- coding: utf-8 -*-

from __future__ import annotations

import itertools
import os
import re
import subprocess
import tempfile
from collections.abc import Iterable
from typing import Optional, Union

import pandas as pd


def conlleval_file(filename: Union[str, os.PathLike]) -> dict:
    script = os.path.join(os.path.dirname(__file__), "conlleval.pl")
    with open(filename) as f:
        outputs = subprocess.run(
            [script, "-d", "\t"], text=True, stdin=f, capture_output=True, check=True
        ).stdout
        # Parse outputs
        results = {"tags": {}}  # type: dict

        lines = []
        for line in outputs.split("\n"):
            line = line.strip()
            if line:
                lines += [line]

        for i, line in enumerate(lines):
            if i == 0:
                results["stats"] = {
                    key: float(value)
                    for key, value in zip(
                        ["tokens", "phrases", "found", "correct"],
                        re.findall(r"[0-9.]", line),
                    )
                }
            elif i == 1:
                results["metrics"] = {
                    key if key != "FB1" else "f1": float(value) / 100.0
                    for key, value in zip(
                        ["accuracy", "precision", "recall", "FB1"],
                        re.findall(r"(?<=\s)[0-9.]+", line),
                    )
                }
            else:
                tag, *metrics, support = re.split(r"(?:%;|:)?\s+", line)
                results["tags"][tag] = {
                    metrics[i]
                    if metrics[i] != "FB1"
                    else "f1": float(metrics[i + 1]) / 100.0
                    for i in range(0, len(metrics), 2)
                }
                results["tags"][tag]["support"] = float(support)

        return results


def conlleval(
    data: Iterable[Iterable[Iterable[str]]],
    filename: Optional[Union[str, os.PathLike]] = None,
) -> dict:
    with (
        (filename and open(filename, mode="w"))
        or tempfile.NamedTemporaryFile(mode="w", delete=False)
    ) as f:
        for example in data:
            for row in zip(*example):
                f.writelines("\t".join(row))
                f.writelines("\n")
            f.writelines("\n")

    return conlleval_file(f.name)


# TODO: Put the following functions to some sequence labeling module.


def classification_report(y_true, y_pred, **kwargs):
    # pylint: disable=import-outside-toplevel
    from sklearn.metrics import classification_report as sklearn_classification_report
    from sklearn.preprocessing import LabelBinarizer

    lb = LabelBinarizer()
    y_true_combined = lb.fit_transform(list(itertools.chain.from_iterable(y_true)))
    y_pred_combined = lb.transform(list(itertools.chain.from_iterable(y_pred)))

    tagset = set(lb.classes_) - {"O"}
    tagset = sorted(tagset, key=lambda tag: tag.split("-", 1)[::-1])
    class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}

    return sklearn_classification_report(
        y_true_combined,
        y_pred_combined,
        labels=[class_indices[cls] for cls in tagset],
        target_names=tagset,
        **kwargs,
    )


def confusion_matrix(y_true, y_pred):
    # pylint: disable=import-outside-toplevel
    from sklearn.metrics import confusion_matrix as sklearn_confusion_matrix

    y_true = [*itertools.chain.from_iterable(y_true)]
    y_pred = [*itertools.chain.from_iterable(y_pred)]

    tags = sorted(
        list(set(y_true)),
        key=lambda x: tuple(reversed(x.split("-"))) if "-" in x else (x,),
    )

    return pd.DataFrame(
        sklearn_confusion_matrix(y_true, y_pred, labels=tags), index=tags, columns=tags
    )
