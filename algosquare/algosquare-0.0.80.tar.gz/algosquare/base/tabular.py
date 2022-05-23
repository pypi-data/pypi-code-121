"""Tabular algos and auxiliary functions."""

from abc import ABC, abstractmethod
from .algo import Algo
from .predictor import Predictor
from .types import Metatype, PredictionMethod, is_classification_metatype, is_prediction_method
from .errors import ValidationError

INPUT_METATYPES = {Metatype.NUMERICAL, Metatype.CATEGORICAL, Metatype.BINARY,
            Metatype.DATETIME, Metatype.TIMESTAMP, Metatype.DELIM_PIPE, Metatype.DELIM_SEMICOLON}

class TabularClassifier(Predictor, ABC):
    """
    Base class for tabular classification model.

    Note:
        'predict_proba' and 'decision_function' are optional, but should be implemented if possible.
    """
    @staticmethod
    @abstractmethod
    def prediction_methods():
        """
        Describes the prediction_methods that the classifier supports.
        
        Returns: 
            Set of PredictionMethods.
        """
        pass

    @abstractmethod
    def predict(self, X):
        """
        Makes prediction for given data.
        
        Args:
            X: DataFrame with shape (n_samples, n_features).

        Returns:
            DataFrame with index of X and columns of y.
        """
        pass

    def predict_proba(self, X):
        """
        Outputs class probabilities for given data.
        
        Args:
            X: DataFrame with shape (n_samples, n_features).

        Returns:
            DataFrame with index of X and columns of classes in y, or list thereof for multivariate problems.

        Raises:
            NotImplementedError.
        """
        raise NotImplementedError

    def decision_function(self, X):
        """
        Outputs decision function for given data.
        
        Args:
            X: DataFrame with shape (n_samples, n_features).

        Returns:
            DataFrame with index of X and columns of classes in y, or list thereof for multivariate problems.
        
        Raises:
            NotImplementedError.
        """
        return self.predict_proba(X)

class TabularClassificationAutoML(Algo, TabularClassifier, ABC):
    """Base class for tabular classification learning algorithm."""
    @abstractmethod
    def fit(self, timeout, metric, X, y, X_metatypes, y_metatypes, X_unlabelled = None):
        """
        Fits model on data.

        Args:
            timeout: time in seconds to fit the model.
            metric: Metric.
            X: DataFrame with shape (n_samples, n_features) and dtype=str.
            y: DataFrame with shape (n_samples, n_outputs) and dtype=str.
            X_metatypes: list of n_features Metatypes.
            y_metatypes: list of n_outputs Metatypes.
            X_unlabelled: DataFrame with shape (n_samples_unlabelled, n_features).
        """
        pass

    @staticmethod
    @abstractmethod
    def input_metatypes():
        """
        Describes the X_metatypes that the algo supports.
        
        Returns: 
            Set of Metatypes.
        """
        pass

    @staticmethod
    @abstractmethod
    def target_metatype():
        """
        Describes the y_metatype that the algo supports.
        
        Returns: 
            Metatype.
        """
        pass

    @staticmethod
    @abstractmethod
    def is_multioutput():
        """
        Returns true if the algo supports mulitple outputs.
        
        Returns: 
            Boolean.
        """
        pass

class TabularRegressor(Predictor, ABC):
    """Base class for tabular regression model."""
    @abstractmethod
    def predict(self, X):
        """
        Makes prediction for given data.
        
        Args:
            X: DataFrame with shape (n_samples, n_features).

        Returns:
            DataFrame with index of X and columns of y.
        """
        pass

class TabularRegressionAutoML(Algo, TabularRegressor, ABC):
    """Base class for tabular regression learning algorithm."""
    @abstractmethod
    def fit(self, timeout, metric, X, y, X_metatypes, y_metatypes, X_unlabelled = None):
        """
        Fits model on data.

        Args:
            timeout: time in seconds to fit the model.
            metric: Metric.
            X: DataFrame with shape (n_samples, n_features) and dtype=str.
            y: DataFrame with shape (n_samples, n_outputs) and dtype=str.
            X_metatypes: list of n_features Metatypes.
            y_metatypes: list of n_outputs Metatypes.
            X_unlabelled: DataFrame with shape (n_samples_unlabelled, n_features).
        """
        pass

    @staticmethod
    @abstractmethod
    def input_metatypes():
        """
        Describes the X_metatypes that the algo supports.
        
        Returns: 
            Set of Metatypes.
        """
        pass

    @staticmethod
    @abstractmethod
    def is_multioutput():
        """
        Returns true if the algo supports mulitple outputs.
        
        Returns: 
            Boolean.
        """
        pass

def is_input_metatype(metatype, strict = False):
    """Checks if metatype is valid input metatype.

    Args:
        metatype: Metatype or int.
        strict: checks if metatype is Metatype.

    Returns: 
        bool.
    """
    if strict and not isinstance(metatype, Metatype):
        return False

    try:
        metatype = Metatype(metatype)
        return metatype in INPUT_METATYPES
    except ValueError:
        return False

def extract_statics(obj):
    statics = dict()

    if issubclass(obj, TabularClassificationAutoML) or issubclass(obj, TabularRegressionAutoML):
        input_metatypes = obj.input_metatypes()
        if not isinstance(input_metatypes, set) or not input_metatypes:
            raise ValidationError('input_metatypes must be a non-empty set')

        for metatype in input_metatypes:
            if not is_input_metatype(metatype, True):
                raise ValidationError('invalid input metatype')

        statics['input_metatypes'] = sorted(list(input_metatypes), key=lambda x: x.name)

        is_multioutput = obj.is_multioutput()
        if not isinstance(is_multioutput, bool):
            raise ValidationError('is_multioutput should return bool')

        statics['is_multioutput'] = is_multioutput

        if issubclass(obj, TabularClassificationAutoML):
            target_metatype = obj.target_metatype()
            if not is_classification_metatype(target_metatype):
                raise ValidationError('invalid classification metatype')

            statics['target_metatype'] = target_metatype


    if issubclass(obj, TabularClassifier):
        prediction_methods = obj.prediction_methods()
        if not isinstance(prediction_methods, set) or not prediction_methods:
            raise ValidationError('prediction_methods must be a non-empty set')

        for prediction_method in prediction_methods:
            if not is_prediction_method(prediction_method, True):
                raise ValidationError('invalid prediction method')

        if PredictionMethod.PREDICT not in prediction_methods:
            raise ValidationError('predict missing from prediction method')

        if PredictionMethod.PREDICT_PROBA in prediction_methods and PredictionMethod.DECISION_FUNCTION not in prediction_methods:
            raise ValidationError('if predict_proba is in prediction_methods, then decision_function should also be')

    else:
        prediction_methods = { PredictionMethod.PREDICT }

    statics['prediction_methods'] = sorted([prediction_method.name.lower() for prediction_method in prediction_methods])

    return statics

    