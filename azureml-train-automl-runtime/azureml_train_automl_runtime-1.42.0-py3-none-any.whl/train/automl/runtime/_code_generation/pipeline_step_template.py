# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import List

from sklearn.pipeline import Pipeline

from azureml.automl.runtime.featurization import DataTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries import TimeSeriesTransformer


class PipelineStepTemplate(ABC):
    @abstractmethod
    def get_function_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_step_name(self) -> str:
        raise NotImplementedError

    def generate_pipeline_step(self) -> List[str]:
        """
        Generate the pipeline step corresponding to this template.

        May return an empty list.

        :return: a list containing the pipeline step code
        """
        return [f"('{self.get_step_name()}', {self.get_function_name()}()),"]


class NoOpTemplate(PipelineStepTemplate):
    def get_function_name(self) -> str:
        return ""

    def get_step_name(self) -> str:
        return ""

    def generate_pipeline_step(self) -> List[str]:
        return []


def pipeline_has_preprocessor(pipeline: Pipeline) -> bool:
    """
    Check whether this pipeline has a preprocessor.

    :param pipeline: the pipeline to check
    :return: True if a preprocessor is present, False otherwise
    """
    return len(pipeline.steps) > 1 and not isinstance(pipeline.steps[-2][1], (DataTransformer, TimeSeriesTransformer))


def pipeline_has_featurizer(pipeline: Pipeline) -> bool:
    """
    Check whether this pipeline has a featurizer.

    :param pipeline: the pipeline to check
    :return: True if a featurizer is present, False otherwise
    """
    return len(pipeline.steps) > 1 and isinstance(pipeline.steps[0][1], (DataTransformer, TimeSeriesTransformer))
