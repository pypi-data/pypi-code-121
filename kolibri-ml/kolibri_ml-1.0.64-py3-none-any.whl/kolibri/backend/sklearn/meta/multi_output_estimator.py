import copy as cp
import warnings
from inspect import signature
import numpy as np

from sklearn.base import BaseEstimator
from sklearn.linear_model import SGDClassifier

from kolibri.indexers.label_indexer import LabelIndexer


_CLASSIFIER_TYPE = "classifier"
_REGRESSOR_TYPE = "regressor"


class MultiTargetEstimator(BaseEstimator):
    """ Multi-Target Estimator for classification or regression.
    Use this meta learner to make single output predictors capable of learning
    a multi output problem, by applying them individually to each output. In
    the classification context, this is the "binary relevance" estimator.

    A Multi-Target Estimator model_type learns to predict multiple outputs for each
    instance. The outputs may either be discrete (i.e., classification),
    or continuous (i.e., regression). This estimator takes any base learner
    (which by default is LogisticRegression) and builds a separate model_type
    for each output, and will distribute each instance to each model_type
    for individual learning and prediction.
    """

    def __init__(self, base_estimator=SGDClassifier(max_iter=100), indexer=None):
        super().__init__()
        self.base_estimator = base_estimator
        self._check_estimator_type()
        self.ensemble = None
        self.n_targets = None
        if indexer:
            self.indexer = indexer
        else:
            self.indexer = LabelIndexer(multi_label=True)

    def _check_estimator_type(self):
        if hasattr(self, "_estimator_type"):
            if self.base_estimator._estimator_type == _CLASSIFIER_TYPE:
                self._estimator_type = _CLASSIFIER_TYPE
                return
            elif self.base_estimator._estimator_type == _REGRESSOR_TYPE:
                self._estimator_type = _REGRESSOR_TYPE
                return
        warnings.warn("Unknown base-estimator type, default is classification.", RuntimeWarning)
        self._estimator_type = _CLASSIFIER_TYPE

    def __configure(self):
        self.ensemble = [cp.deepcopy(self.base_estimator) for _ in range(self.n_targets)]

    def fit(self, X, y, sample_weight=None):
        """ Fit the model_type.

        Fit n-estimators, one for each learning task.

        Parameters
        ----------
        X : numpy.ndarray of shape (n_samples, n_features)
            The features to train the model_type.

        y: numpy.ndarray of shape (n_samples, n_targets)
            An array-like with the label values of all samples in data.

        classes:  numpy.ndarray, optional (default=None)
            Array with all possible/known class y_values. Usage varies depending on the base estimator.
            Not used for regression.

        sample_weight: numpy.ndarray of shape (n_samples), optional (default=None)
            Samples weight. If not provided, uniform weights are assumed. Usage varies depending on the base estimator.

        Returns
        -------
        MultiTargetEstimator
            self

        """

        N, L = y.shape
        self.n_targets = L
        self.__configure()

        for j in range(self.n_targets):
            if 'sample_weight' and 'classes' in signature(self.ensemble[j].fit).parameters:
                self.ensemble[j].fit(X, y[:, j], sample_weight=sample_weight)
            elif 'sample_weight' in signature(self.ensemble[j].fit).parameters:
                self.ensemble[j].fit(X, y[:, j], sample_weight=sample_weight)
            else:
                self.ensemble[j].fit(X, y[:, j])
        return self

    def partial_fit(self, X, y, classes=None, sample_weight=None):
        """ Partially (incrementally) fit the model_type.

        Partially fit each of the estimators on the data matrix and the
        corresponding y matrix.

        Parameters
        ----------
        X : numpy.ndarray of shape (n_samples, n_features)
            The features to train the model_type.

        y: numpy.ndarray of shape (n_samples, n_targets)
            An array-like with the label values of all samples in data.

        classes: numpy.ndarray, optional (default=None)
            Array with all possible/known class y_values. This is an optional parameter, except
            for the first partial_fit call where it is compulsory. Not used for regression.

        sample_weight: numpy.ndarray of shape (n_samples), optional (default=None)
            Samples weight. If not provided, uniform weights are assumed. Usage varies depending on the base estimator.


        Returns
        -------
        MultiTargetEstimator
            self

        """
        if self.n_targets is None:
            # This is the first time that the model_type is fit
            self.fit(X=X, y=y, sample_weight=sample_weight)
            return self

        y = np.array(y)

        N, self.n_targets = y.shape

        if self.ensemble is None:
            self.__configure()

        for j in range(self.n_targets):
            if 'sample_weight' and 'classes' in signature(self.ensemble[j].partial_fit).parameters:
                self.ensemble[j].partial_fit(X, y[:, j], classes=classes, sample_weight=sample_weight)
            elif 'sample_weight' in signature(self.ensemble[j].partial_fit).parameters:
                self.ensemble[j].partial_fit(X, y[:, j], sample_weight=sample_weight)
            else:
                self.ensemble[j].partial_fit(X, y[:, j])

        return self

    def predict(self, X):
        """ Predict label values for the passed texts.

        Iterates over all the estimators, predicting with each one, to obtain
        the multi output prediction.
        
        Parameters
        ----------
        X : numpy.ndarray of shape (n_samples, n_features)
            The set of texts samples to predict the label values for.
            
        Returns
        -------
        numpy.ndarray
            numpy.ndarray of shape (n_samples, n_targets)
            All the predictions for the samples in data.
        """

        N, D = X.shape
        predictions = np.zeros((N, self.n_targets))
        for j in range(self.n_targets):
            predictions[:, j] = self.ensemble[j].predict(X)

        return predictions

    def predict_proba(self, X):
        """ Estimates the probability of each sample in data belonging to each of
        the existing y_values for each of the classification tasks.
        
        It's a simple call to all of the classifier's predict_proba function, 
        return the probabilities for all the classification problems.

        Not applicable for regression tasks.

        Parameters
        ----------
        X : numpy.ndarray of shape (n_samples, n_features)
            The set of texts samples to predict the class y_values for.

        Returns
        -------
        numpy.ndarray
            An array of shape (n_samples, n_classification_tasks, n_labels), in which 
            we store the probability that each sample in data belongs to each of the y_values,
            in each of the classification tasks.
        
        """
        N, D = X.shape
        proba = np.zeros((N, self.n_targets))
        for j in range(self.n_targets):
            try:
                proba[:, j] = self.ensemble[j].predict_proba(X)[:, 1]
            except NotImplementedError or AttributeError:
                raise AttributeError("Estimator {} has no predict_proba method".format(
                    type(self.base_estimator)))
        return proba

    def reset(self):
        self.ensemble = None
        self.n_targets = None

    def _more_tags(self):
        return {'multioutput': True,
                'multioutput_only': True}
