# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wrapper over pandas.cut for binning the train data into intervals and then applying them to test data."""
from azureml.training.tabular.featurization.numeric.bin_transformer import BinTransformer
