#!/usr/bin/env python
# coding: utf-8

from intelliw.datasets.datasets import DataSets
from intelliw.core.pipeline import Pipeline


class Trainer:
    def __init__(self, path, reporter=None, perodic_interval=-1):
        self.pipeline = Pipeline(reporter, perodic_interval)
        self.pipeline.importmodel(path, False)

    def train(self, datasets: DataSets):
        if not isinstance(datasets, DataSets):
            raise TypeError("datasets has a wrong type, required: DataSets, actually: {}"
                            .format(type(datasets).__name__))

        return self.pipeline.train(datasets)

    def perodic_callback(self):
        self.pipeline.perodic_callback_train()
