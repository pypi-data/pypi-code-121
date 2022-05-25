# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Transforms column using a label encoder to encode categories into numbers."""
from .._azureml_transformer import AzureMLTransformer


class PrefittedStandardScaler(AzureMLTransformer):
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def get_params(self, deep=True):
        return {"mean": self.mean, "std": self.std}

    def fit(self, X):
        return self

    def transform(self, X):
            X -= self.mean
            X /= self.std
            return X
