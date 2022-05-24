"""
Created on Mar 19, 2017

(c) IBM Corp, 2017, All rights reserved
"""
from builtins import object

from pandas import DataFrame, Series  # For type hinting purposes
import numpy as np
import sklearn.base
import sklearn.ensemble
from sklearn.ensemble.forest import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model.logistic import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing.imputation import Imputer

from .adversarialbalancing_ import AdversarialBalancing
from ..preprocessing.filters import ConstantFilter, StatisticalFilter
from ..preprocessing.transformers import HrlScaler


# TODO: add: from sklearn.utils.validation import ensure_is_fitted


# from estimators.filters import ConstantFilter, StatisticalFilter
# from estimators.transformers import HrlScaler
# TODO: better explain the logic behind both Learner and Base (why are they even divided?)
# noinspection PyPep8Naming
class Learner(object):
    """
    Wraps an sklearn estimator
    """

    def __init__(self, learner):
        """
        Args:
            learner (sklearn.base.BaseEstimator): The learner object
        """
        self.learner = learner

    def train(self, X, Y, fit_params=None):
        """

        Args:
            X (DataFrame | np.ndarray): Data to fit the models with. Training samples.
            Y (Series | np.ndarray): Target values (response)
            fit_params (dict): parameters for fit

        Returns:
            Model: An sklearn wrapped models (Model) fitted on the train data.
        """
        if fit_params is None:
            fit_params = {}
        assert Y.ndim == 1 or Y.shape[1] == 1  # make sure 1d vec       # TODO: ndim should be enough (both pd and np)
        nUniqueVals = sum(~np.isnan(np.unique(Y)))      # TODO: if there's a nan, then it will fail afterwards, so why ignore it now?

        if nUniqueVals < 2:
            raise ValueError('number of unique values in Y:%g' % nUniqueVals)

        model = sklearn.base.clone(self.learner)
        if hasattr(X, 'values'):               # TODO: is it a pandas/ndarray thing? why not work directly with pandas?
            X_values = X.values
        else:
            X_values = X
        model.fit(X_values, Y, **fit_params)

        isBinaryY = nUniqueVals == 2
        return Model(model, isBinaryY)


# =====================================================================

# noinspection PyPep8Naming
class Model(object):       # TODO: maybe inherent from some sklearn object since it demands predict/predict_proba method
    """

    """
    def __init__(self, model, isBinaryY):
        """

        Args:
            model (RandomForestClassifier | RandomForestRegressor | LogisticRegression | Pipeline): A fitted models
            isBinaryY (bool): Whether the response is binary or not
        """
        # TODO: add the following to check that the models is fitted: ensure_is_fitted(models, attributes=["predict"])
        self.model = model
        self.isBinaryY = isBinaryY  # TODO: is binary but not multi-class? or is it classification vs regression?

    def predict(self, X):
        """
        Predict responses for samples in X.
        Args:
            X (DataFrame | np.ndarray): Data to fit the models with. Training samples.

        Returns:
            np.array: Predicted response.
        """
        if hasattr(X, 'values'):        # TODO: is it a pandas/ndarray thing? why not work directly with pandas?
            X_values = X.values
        else:
            X_values = X
        if self.isBinaryY:              # TODO: maybe add a parameter that specify either predict or predict_proba?
            return self.model.predict_proba(X_values)[:, 1]
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_values)
        else:  # for regression models that don't support predict_proba
            return self.model.predict(X_values)

    def predictTrain(self, X):
        """

        Args:
            X (DataFrame | np.ndarray): Data to fit the models with. Training samples.

        Returns:
            np.array: Predicted response.
        """
        # TODO: what is this function good for? why not part of the predict if-else?
        finalModel = self.getFinalModel()
        if isinstance(finalModel, sklearn.ensemble.RandomForestClassifier):
            return finalModel.oob_decision_function_[:, 1]      # TODO: this does not predict X

        # if isinstance(finalModel, sklearn.ensemble.RandomForestRegressor):
        #     return finalModel.oob_prediction_

        return self.predict(X)

    def getFinalModel(self):
        """
        Get the prediction models. If a Pipeline, then return the last models (the one that does the actual prediction).
        Returns:
            RandomForestClassifier | RandomForestRegressor | LogisticRegression | Pipeline: The final prediction models.
        """
        if self.isPipeline():
            return self.model.steps[-1][1]      # Last step in a list of tuples: ('model_name', models)

        return self.model

    def isPipeline(self):                       # TODO: this has only one call above, might be redundant.
        """
        Returns:
            bool: Whether the prediction models is a Pipeline (sklearn.pipeline.Pipeline) or not.
        """
        return isinstance(self.model, Pipeline)


# noinspection PyPep8Naming
def getLearner(params, preprocessors=None):
    """
    Factory method for the
    Args:
        params (dict): Parameters for the desired Learner. Parameters are for both the prediction models and the
                       preprocessing objects.
        preprocessors (np.ndarray[BaseEstimator]): preprocessor steps to run before the final fit of the models runs

    Returns:
        Learner: A Learner object wrapping a Pipeline of preprocessing steps and a final predictor.
    """
    learnerDict = {
        'logistic': lambda x: getLogisticRegression(x),
        'rfcls': lambda x: getRandomForestClassifier(x),
        'rfreg': lambda x: getRandomForestRegressor(x),
        'adv': lambda x: getAdversarialBalancing(x)
    }           # TODO: change x to p or params, so it will be clearer that the tunneled input is params and not data.
    # TODO: params is not consistent, for the learner is has "models"->"model_name" and for preprocess is "preprocess_name"->"intialized_preprocess_object" and the other params are "param_name"->"param".
    if preprocessors is None:
        preprocessors = getPreprocessors(params)
    steps = preprocessors + [(params['models'], learnerDict[params['models']](params))]
    # TODO: don't access dictionary with [] but with .get() - so in case missing you control how informative the error
    return Learner(Pipeline(steps))  # TODO: this way all Learner are forced to be Pipeline


# noinspection PyPep8Naming
def getAdversarialBalancing(params=None):
    """
    Factory helper function. Retrieves an Adversarial Balancer
    Args:
        params (dict): dictionary with {"discr": initialized_discriminator_model}
                       in case using a LogisticRegression can specify a "penalty".

    Returns:
        AdversarialBalancing: Initialized AdversarialBalancing models.
    """
    if params is None:
        params = {}
    penalty = params.get('penalty', 'l2')   # TODO: in practice, this method only needs an initialized discriminator. (penalty is somewhat redundant it is used only when fallback to the default LR, so just pass the intialized LR)
    model = params.get('discr', LogisticRegression(penalty=penalty))
    learner = AdversarialBalancing(model=model)
    return learner


# noinspection PyPep8Naming
def getLogisticRegression(params=None):
    """
    Factory helper function. Retrieves a LogisticRegression
    Args:
        params: dictionary with parameters matching the scikit learn's LogisticRegression:
                http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

    Returns:
        LogisticRegression: Initialized LogisticRegression models
    """
    if params is None:
        params = {}
    # TODO: this way you can't specify other paameters (e.g. threshold) and these values match sklearn default values. consider just passing **params into LogisticRegression
    multi_class = params.get('multi_class', 'ovr')
    penalty = params.get('penalty', 'l2')
    fit_intercept = params.get('fit_intercept', True)
    max_iter = params.get('max_iter', 100)
    C = params.get('C', 1)
    learner = LogisticRegression(
        penalty=penalty, multi_class=multi_class, solver='lbfgs', verbose=1, fit_intercept=fit_intercept,
        max_iter=max_iter, C=C)
    return learner


# noinspection PyPep8Naming
def getRandomForestClassifier(params=None):
    """
    Factory helper function. Retrieves a RandomForestClassifier
    Args:
        params: dictionary with parameters matching the scikit learn's RandomForestClassifier:
                http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html

    Returns:
        RandomForestClassifier: Initialized RandomForestClassifier models.
    """
    if params is None:
        params = {}
    # TODO: for default parameters see note in getLogisticRegression
    nTrees = params.get('nTrees', 501)
    learner = RandomForestClassifier(n_estimators=nTrees, oob_score=True, n_jobs=-1)
    return learner


# noinspection PyPep8Naming
def getRandomForestRegressor(params=None):
    """
    Factory helper function. Retrieves a RandomForestRegressor
    Args:
        params: dictionary with parameters matching the scikit learn's RandomForestRegressor:
                http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html

    Returns:
        RandomForestRegressor: Initialized RandomForestRegressor models.
    """
    if params is None:
        params = {}
    nTrees = params.get('nTrees', 501)
    learner = RandomForestRegressor(n_estimators=nTrees, oob_score=True, n_jobs=-1)
    return learner


# TODO: Discuss with Yishai, hard coded values instead of params, 1.0 for correlation
# noinspection PyPep8Naming
def getPreprocessors(params):
    """

    Args:
        params (dict): A dictionary of {preprocessors_name: preprocessor_object}, where the preprocessor_object is
                       already initialized.

    Returns:
        list[tuple[str, sklearn.base.BaseEstimator]]: list of two-tuples:
                                                      (preprocessors_name, initialized_preprocessor_object).
                                        To fit the Pipeline object:
                                        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html
    """
    # TODO: does not use params at all, should there be defaulted? maybe allow user to have no preprocess
    preprocessors = [('const-filter', ConstantFilter(.99)),
                     ('imputer', Imputer()),
                     ('scaler', HrlScaler()),
                     ('xy-corr-filter', StatisticalFilter(True, 1.0))]

    # preprocessors = []
    return preprocessors
