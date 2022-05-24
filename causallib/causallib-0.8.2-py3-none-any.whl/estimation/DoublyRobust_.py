"""
(C) IBM Corp, 2017, All rights reserved
Created on Apr 28, 2017

@author: Yishai Shimoni
"""
from __future__ import division

from warnings import warn

import numpy as np
from builtins import range
from pandas import DataFrame as pdDataFrame, Series as pdSeries  # for docstring purposes
from past.utils import old_div

from .Estimators_ import CounterfactualEstimator
from .Standardization_ import StdEstimator
from .Learner_ import Learner


class DoublyRobust(CounterfactualEstimator):
    """
    Implements the doubly robust method. Requires fitting one models for the propensity and one for the effect,
    and so, it requires all the parameters that they require.
    """
    def __init__(self, treatment_learner, outcome_learner, effect_types=None, propensity_params=None,
                 outcome_params=None, fallback_estimator=None, method='vanilla'):
        """
        Constructor

        Args:
            treatment_learner (Learner): The models that learns the propensity score (the probability to treat).
            outcome_learner (Learner): The models that learns and estimates the potential outcomes.
            effect_types (list[str]): The types of causal effect. e.g. difference between average causal effect or
                                      the ratio. Possible values are defined in ????
            propensity_params (dict): Keyword-param pairs to be passed to the propensity learner.
            outcome_params (dict): Keyword-param pairs to be passed to the outcome learner.
            fallback_estimator (CounterfactualEstimator): An estimator that will be used in case the propensity cannot
                                                          be estimated.
            method (str): Different versions of Doubly Robust estimators.
        """

        if effect_types is None:
            effect_types = ['diff']         # TODO: redundant since it already happens in CounterFactualEstimator init.
        if propensity_params is None:
            propensity_params = {}
        if outcome_params is None:
            outcome_params = {}
        super(DoublyRobust, self).__init__(effectTypes=effect_types)
        self.treatment_learner = treatment_learner
        self.outcome_learner = outcome_learner
        self.effectTypes = effect_types
        # self.use_stabilized = use_stabilized
        self.fit_params = propensity_params
        self.outcome_params = outcome_params
        if fallback_estimator is None:
            self.fallback_estimator = StdEstimator(self.outcome_learner, self.effectTypes)
        else:
            self.fallback_estimator = fallback_estimator
        self.method = method

    # noinspection PyPep8Naming
    def estimateCounterfactuals(self, Y, A, X):
        """
        Given the measured outcome Y, the assignment A, and the coefficients X calculate a doubly-robust estimator
        of the effect of treatment

        Args:
            Y (np.ndarray | pdSeries): A vector of length N of the measured outcome. Coercible to np.ndarray
            A (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            X (np.ndarray | pdDataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray

        Returns:
            dict: A dictionary with the different results (estimations).
        """
        # TODO: specify what is exactly return. Maybe write a class of results instead a dictionary.
        try:        # TODO: move into dictionary? this way it will be easier to follow.
            if self.method == 'vanilla':
                return self.estimate_counterfactuals_vanilla(Y, A, X)
            if self.method == 'joffe':
                return self.estimate_counterfactuals_joffe(Y, A, X)
            if self.method == 'ip_feature':
                return self.estimate_counterfactuals_ip_feature(Y, A, X)
            assert False, 'method %s not implemented' % self.method
        except AssertionError:                      # TODO: change the try-assert-except to else-warn.
            warn('Using fallback outcome models.')
        return self.fallback_estimator.estimateCounterfactuals(Y, A, X)

    def estimate_counterfactuals_vanilla(self, y, z, x):
        """
        Given the measured outcome Y, the assignment Y, and the coefficients X calculate a doubly-robust estimator
        of the effect of treatment

        If e(X) is the estimated propensity score and m(X, A) is the estimated effect by an estimator then the
        individual estimates are:

        | Y + (A-e(X))*(Y-m(X,1)) / e(X) if A==1, and
        | Y + (e(X)-A)*(Y-m(X,0)) / (1-e(X)) if A==0

        These expressions show that when e(X) is an unbiased estimator of A, or when m is an unbiased estimator of Y
        then the resulting estimator is unbiased. Note that the term for A==0 is derived from (1-A)-(1-e(X))

        Another way of writing these equation is:

        | m(X,1) + A*(Y-m(X,1))/e(X), and
        | m(X,0) + (1-A)*(Y-m(X,0))/(1-e(X))

        Args:
            y (np.ndarray | pdSeries): A vector of length N of the measured outcome. Coercible to np.ndarray
            z (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            x (np.ndarray | pdDataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray

        Returns:
            dict: A results dictionary holding the propensity ['P], the individual estimated effects ['Y0', 'Y1'],
                  the estimated average effects ['EY0', 'EY1'] the trained models ['models'] and the trained
                  propensity models ['p_model']
        """
        # TODO: refactor var names to match estimateCounterfactuals
        y = np.array(y)
        z = np.array(z)
        x = np.array(x)
        # estimate the outcomes
        outcome_model = self.outcome_learner.train(np.hstack((z[:, np.newaxis], x)), y, **self.outcome_params)
        m_0 = outcome_model.predictTrain(np.hstack((np.zeros((z.shape[0], 1)), x)))
        m_1 = outcome_model.predictTrain(np.hstack((np.ones((z.shape[0], 1)), x)))

        # estimate the propensity scores
        propensity_model = self.treatment_learner.train(x, z, **self.fit_params)
        truncate = 0.05
        e_1 = np.minimum(1 - truncate, np.maximum(truncate, propensity_model.predictTrain(x)))
        # estimate values for average effect
        Y_0 = m_0 + (1 - z) * (y - m_0) / (1 - e_1)
        Y_1 = m_1 + z * (y - m_1) / e_1
        # estimate the individual counterfactuals
        m_0[z == 0] = y[z == 0]  # m_0[z == 1] is already equal to Y_0[z == 1]
        m_1[z == 1] = y[z == 1]
        res = dict(P=e_1,
                   Y0=m_0,
                   Y1=m_1,
                   EY0=np.nanmean(Y_0),
                   EY1=np.nanmean(Y_1),
                   model=outcome_model,
                   # TreatedEffect=np.nanmean(Y_1[z == 1]) - np.nanmean(Y_0[z == 0]),
                   TreatedEffect=np.nanmean(Y_1[z == 1] - Y_0[z == 1]),
                   p_model=propensity_model)
        for i in range(len(Y_0)):
            res[i] = m_1[i] - m_0[i]
        return res

    def estimate_counterfactuals_joffe(self, y, z, x):
        """
        Given the measured outcome Y, the assignment A, and the coefficients X calculate a doubly-robust estimator
        of the effect of treatment

        In this version, the propensity scores are used as weights for fitting the outcome models

        Args:
            y (np.ndarray | pdSeries): A vector of length N of the measured outcome. Coercible to np.ndarray
            z (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            x (np.ndarray | pdDataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray

        Returns:
            dict: A results dictionary holding the propensity ['P], the individual estimated effects ['Y0', 'Y1'],
                  the estimated average effects ['EY0', 'EY1'] the trained models ['models'] and the trained
                  propensity models ['p_model']
        """
        # TODO: refactor var names to match estimateCounterfactuals
        y = np.array(y)
        z = np.array(z)
        x = np.array(x)

        # estimate the propensity scores
        propensity_model = self.treatment_learner.train(x, z, **self.fit_params)
        truncate = 1e-2
        e_1 = np.minimum(1 - truncate, np.maximum(truncate, propensity_model.predictTrain(x)))
        e_0 = 1 - e_1

        # estimate the outcomes using the propensity as another feature
        new_z = z[:, np.newaxis]
        learner_name = self.outcome_learner.learner.steps[-1][0]
        self.outcome_params[learner_name + '__sample_weight'] = old_div(1, e_1)
        outcome_model = self.outcome_learner.train(np.hstack((new_z, x)), y, fit_params=self.outcome_params)
        m_0 = outcome_model.predictTrain(np.hstack((np.zeros((z.shape[0], 1)), x)))
        m_1 = outcome_model.predictTrain(np.hstack((np.ones((z.shape[0], 1)), x)))
        res = {'P': e_1,
               'Y0': m_0,
               'Y1': m_1,
               'EY0': np.nanmean(m_0),
               'EY1': np.nanmean(m_1),
               'models': outcome_model,
               'p_model': propensity_model,
               'TreatedEffect': np.nanmean(m_1[z == 1] - m_0[z == 1])}
        return res

    def estimate_counterfactuals_ip_feature(self, y, z, x):
        """
        Given the measured outcome Y, the assignment A, and the coefficients X calculate a doubly-robust estimator
        of the effect of treatment

        In this version, the IP-weighted assignment is added as a feature to the models

        Args:
            y (np.ndarray | pdSeries): A vector of length N of the measured outcome. Coercible to np.ndarray
            z (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            x (np.ndarray | pdDataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray

        Returns:
            dict: A results dictionary holding the propensity ['P], the individual estimated effects ['Y0', 'Y1'],
                  the estimated average effects ['EY0', 'EY1'] the trained models ['models'] and the trained
                  propensity models ['p_model']
        """
        # TODO: refactor var names to match estimateCounterfactuals
        y = np.array(y)
        z = np.array(z)
        x = np.array(x)

        # estimate the propensity scores
        propensity_model = self.treatment_learner.train(x, z, **self.fit_params)
        truncate = 1e-2
        e_1 = np.minimum(1 - truncate, np.maximum(truncate, propensity_model.predictTrain(x)))

        # estimate the outcomes using the propensity as another feature
        new_z = z[:, np.newaxis]
        outcome_model_1 = self.outcome_learner.train(np.hstack((new_z, (old_div(z, e_1))[:, np.newaxis], x)), y,
                                                     fit_params=self.outcome_params)
        outcome_model_0 = self.outcome_learner.train(
            np.hstack((new_z, (old_div((1 - z), (1 - e_1)))[:, np.newaxis], x)), y,
            fit_params=self.outcome_params)
        m_0 = outcome_model_0.predictTrain(
            np.hstack((np.zeros((z.shape[0], 1)), old_div(1, (1 - e_1[:, np.newaxis])), x)))
        m_1 = outcome_model_1.predictTrain(np.hstack((np.ones((z.shape[0], 1)), old_div(1, e_1[:, np.newaxis]), x)))
        res = {'P': e_1,
               'Y0': m_0,
               'Y1': m_1,
               'EY0': np.nanmean(m_0),
               'EY1': np.nanmean(m_1),
               'models': outcome_model_1,
               'model0': outcome_model_0,
               'p_model': propensity_model,
               'TreatedEffect': np.nanmean(m_1[z == 1] - m_0[z == 1])}
        for i in range(len(m_0)):
            res[i] = m_1[i] - m_0[i]
        return res

    def estimatorWrapper(self, D):
        # TODO: called from the competition main. Maybe should be deleted, or passed to the competition code.
        # D is a data frame, func is the estimator function.
        # It is assumed that D contains columns A for the treatment, Y for the outcome and others as covariates

        # we assume the treatment indicator is at column 0 and the outcome at column 1
        return self.estimateCounterfactuals(Y=D[:, 1], A=D[:, 0], X=D[:, 2:])['TreatedEffect']
