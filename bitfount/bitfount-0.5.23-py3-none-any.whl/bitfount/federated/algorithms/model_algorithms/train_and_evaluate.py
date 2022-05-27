"""Algorithm to train and evaluate a model on remote data."""
from __future__ import annotations

from typing import Any, Dict, List, cast

import numpy as np

from bitfount.data.datasources.base_source import _BaseSource
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModelAlgorithmFactory,
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.hub.api import BitfountHub
from bitfount.metrics import MetricCollection

logger = _get_federated_logger(__name__)


class _ModellerSide(_BaseModellerModelAlgorithm):
    """Modeller side of the ModelTrainingAndEvaluation algorithm."""

    def run(self, results: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """Simply returns results."""
        return results


class _WorkerSide(_BaseWorkerModelAlgorithm):
    """Worker side of the ModelTrainingAndEvaluation algorithm."""

    def run(self, data: _BaseSource) -> Dict[str, float]:
        """Runs training and evaluation and returns metrics."""
        self.model.fit(data)
        preds, targs = self.model.evaluate()
        # TODO: [BIT-1604] Remove these cast statements once they become superfluous.
        preds = cast(np.ndarray, preds)
        targs = cast(np.ndarray, targs)
        m = MetricCollection.create_from_model(self.model)
        return m.compute(targs, preds)


class ModelTrainingAndEvaluation(_BaseModelAlgorithmFactory):
    """Algorithm for training a model, evaluating it and returning metrics.

    Args:
        model: The model to train and evaluate on remote data.

    Attributes:
        name: The name of the algorithm.
        model: The model to train and evaluate on remote data.

    :::note

    The metrics cannot currently be specified by the user.

    :::
    """

    def modeller(self, **kwargs: Any) -> _ModellerSide:
        """Returns the modeller side of the ModelTrainingAndEvaluation algorithm."""
        model = self._get_model_from_reference()
        return _ModellerSide(model=model, **kwargs)

    def worker(self, hub: BitfountHub, **kwargs: Any) -> _WorkerSide:
        """Returns the worker side of the ModelTrainingAndEvaluation algorithm.

        Args:
            hub: `BitfountHub` object to use for communication with the hub.
        """
        model = self._get_model_from_reference(hub=hub)
        return _WorkerSide(model=model, **kwargs)
