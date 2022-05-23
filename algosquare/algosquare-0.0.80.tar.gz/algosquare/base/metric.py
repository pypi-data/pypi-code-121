"""Metric base class."""
from abc import ABC, abstractmethod
from .types import Metatype, is_target_metatype

class Metric(ABC):
    """Base class for all Metrics."""
    @abstractmethod 
    def __init__(self, name, metatypes, prediction_method, greater_is_better):
        """
        Metric base class.

        Args:
            name: string representation.
            metatypes: Metatype or set thereof.
            prediction_method: predict, predict_proba, decision_function.
            greater_is_better: whether Metric is a score function (higher is better), or loss function (lower is better).
        """
        if not isinstance(name, str):
            raise TypeError('name must be a string')
        self._name = name

        if isinstance(metatypes, Metatype):
            metatypes = {metatypes}

        if not isinstance(metatypes, set):
            raise TypeError('metatypes must be a set')

        for metatype in metatypes:
            if not is_target_metatype(metatype, strict = True):
                raise ValueError('metatypes must be a set of Metatypes')

        if prediction_method not in ('predict', 'predict_proba', 'decision_function'):
            raise ValueError('invalid prediction_method')

        if Metatype.NUMERICAL in metatypes and prediction_method != 'predict':
            raise ValueError('prediction_method must be predict for numreical-metatype')

        self._metatypes = metatypes
        self._prediction_method = prediction_method
        self._sign = -1 if greater_is_better else 1

    @abstractmethod
    def score(self, y, pred):
        """
        Invokes underlying score function.

        Args:
            y: targets.
            pred: model predictions.

        Returns:
            float.
        """
        pass

    def __str__(self):
        """Name of Metric."""
        return self._name

    def to_dict(self):
        metatypes = [metatype.name.lower() for metatype in self._metatypes]
        return dict(name = self._name, prediction_method = self._prediction_method, sign = self._sign, metatypes = metatypes)

    def loss(self, y, pred):
        """
        Loss based on underlying score function where lower is better.

        Args:
            y: targets.
            pred: model predictions.

        Returns:
            float.
        """
        return self.score_to_loss(self.score(y, pred))

    def score_to_loss(self, score):
        """
        Converts score to loss.

        Args:
            score: float.

        Returns:
            float.
        """
        return self._sign * score

    def prediction_score(self, model, X, y):
        """
        Combined prediction and scoring.

        Args:
            model: estimator with prediction method.
            X: inputs.
            y: targets.

        Returns:
            float.
        """
        return self.score(y, self.prediction(model, X))

    def prediction_loss(self, model, X, y):
        """
        Combined prediction and loss.

        Args:
            model: estimator with prediction method.
            X: inputs.
            y: targets.

        Returns:
            float.
        """
        return self.loss(y, self.prediction(model, X))

    def prediction(self, model, *args, **kwargs):
        """
        Returns prediction of model.

        Args:
            model: implements prediction method.
            *args: arguments to prediction method
            **kwargs: keyword arguments to prediction method

        Returns:
            model prediction.
        """
        return getattr(model, self._prediction_method)(*args, **kwargs)

    def supports_metatype(self, metatype):
        """
        Checks if metric supports a given metatype.

        Args:
            metatype: Metatype

        Returns:
            bool.
        """
        return metatype in self._metatypes
