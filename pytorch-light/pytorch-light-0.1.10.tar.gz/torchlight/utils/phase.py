# -*- coding: utf-8 -*-

from __future__ import annotations

import enum


class ModeKeys(str, enum.Enum):
    TRAIN = "train"
    EVAL = "eval"
    PREDICT = "predict"


class PhaseMixin(object):
    mode = ModeKeys.TRAIN

    def train(self) -> None:
        self.mode = ModeKeys.TRAIN

    def eval(self) -> None:
        self.mode = ModeKeys.EVAL

    def predict(self) -> None:
        self.mode = ModeKeys.PREDICT

    def is_train(self) -> bool:
        return self.mode == ModeKeys.TRAIN
