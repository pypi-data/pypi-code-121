# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Transforms column using a label encoder to encode categories into numbers."""
import numpy as np
from .._azureml_transformer import AzureMLTransformer


class PrefittedLabelEncoderTransformer(AzureMLTransformer):
    """Transforms column using a pre-determined set of labels."""

    def __init__(self, classes: np.ndarray):
        self.classes = classes

    def get_params(self, deep=True):
        return {"classes": self.classes}

    def fit(self, x, y=None):
        return self

    def transform(self, X):
        return np.searchsorted(self.classes, X)
