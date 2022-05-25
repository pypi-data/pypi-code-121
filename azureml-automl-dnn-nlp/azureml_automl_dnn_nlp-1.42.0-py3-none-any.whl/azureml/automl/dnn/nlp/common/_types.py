# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Convenience types for Azure AutoNLP constructs."""

from typing import Union

from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper as MultilabelModelWrapper
from azureml.automl.dnn.nlp.classification.multiclass.model_wrapper import ModelWrapper as MulticlassModelWrapper
from azureml.automl.dnn.nlp.ner.model_wrapper import ModelWrapper as NERModelWrapper

MODEL_WRAPPER_TYPE = Union[MulticlassModelWrapper, MultilabelModelWrapper, NERModelWrapper]
