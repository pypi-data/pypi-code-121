"""Models using LightGBM as the backend."""
from __future__ import annotations

from typing import Any

from bitfount.backends.lightgbm.models.base_models import BaseLGBMRandomForest
from bitfount.models.base_models import ClassifierMixIn, RegressorMixIn


class LGBMRandomForestClassifier(ClassifierMixIn, BaseLGBMRandomForest):
    """LGBM Classifier for Random Forests and GBMs.

    Currently only supports binary classification.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._set_objective()
        self._set_training_metrics()

    def _set_objective(self) -> None:
        """Set training objective."""
        self.objective: str = "binary"

    def _set_training_metrics(self) -> None:
        """Set training metrics."""
        self.training_metrics = ["binary_logloss", "auc"]


class LGBMRandomForestRegressor(RegressorMixIn, BaseLGBMRandomForest):
    """LGBM Regressor for Random Forests and GBMs."""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._set_objective()
        self._set_training_metrics()

    def _set_objective(self) -> None:
        """Set training objective."""
        self.objective = "regression"

    def _set_training_metrics(self) -> None:
        """Set training metrics."""
        self.training_metrics = ["mae", "mse", "rmse"]
