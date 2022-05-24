"""
Created on Mar 19, 2017

(c) IBM Corp, 2017, All rights reserved
"""
from __future__ import division
from builtins import str
from past.utils import old_div

import numpy as np
import pandas as pd

from .Estimators_ import CounterfactualEstimator


class IPWEstimator(CounterfactualEstimator):
    """
    Implements causal effect estimation via inverse probability weighting (of treatment).
    """
    def __init__(self, treatment_learner, effect_types=None, use_stabilized=True, fit_params=None):
        """

        Args:
            treatment_learner (Learner): Learning models whose outputs' type is same as the treatment variable (or the
                                         censoring masking, if used to learn informative censoring).
            effect_types (str | list[str]): The types of causal effect. e.g. difference between average causal effect or
                                            the ratio. Possible values are defined in ????
            use_stabilized (bool): Whether to re-weigh the learned weights with the prevalence of the treatment.
                                   See Also: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4351790/#S6title
            fit_params (dict): Keyword-param pairs to be passed to the learner as kwargs. Must match that scikit-leaner
                               parameters.
        """
        if effect_types is None:
            effect_types = ['diff']
        if fit_params is None:
            fit_params = {}
        super(IPWEstimator, self).__init__(effect_types)
        self.treatment_learner = treatment_learner
        self.use_stabilized = use_stabilized
        self.last_weights = []  # TODO: why not initiate None, calling before initiation? so why not consistent with empty ndarray? in addition, maybe final_weights better?
        self.fit_params = fit_params

    def estimateCounterfactuals(self, Y, A, X):
        """
        Estimate counter-factual outcomes using the learned weights.

        Args:
            Y (np.ndarray | pd.Series): A vector of length N of the measured outcome. Coercible to np.ndarray
            A (np.ndarray | pd.Series): A vector of length N of the treatment assignments. Coercible to np.ndarray
            X (np.ndarray | pd.DataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray

        Returns:
            dict: A dictionary with the different results (estimations).

        """
        res = self.computeWeights(X, A)
        weights = res['weights']
        self.last_weights = weights

        treatments = np.unique(A)
        for tr in treatments:
            res['EY'+str(tr)] = np.average(Y[A == tr], axis=0, weights=weights[A == tr])
        return res

    def computeWeights(self, X, A):
        """
        Estimate propensity scores and inverse it into weights.

        Args:
            X (np.ndarray | pdDataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray
            A (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray

        Returns:
            dict: two-item dictionary:

                * *weights* (np.ndarray): An N-sized vector with weight for each sample in X
                * *models* (Model): A fitted learning models.
        """
        # train models Pr(A|X)
        model = self.treatment_learner.train(X, A, **self.fit_params)
        p = model.predictTrain(X)
        # avoid numerical issues with probabilities that are too close to 0 or 1
        epsilon = 1e-5                      # TODO: define EPSILON as global, let users define it through the module.
        p[p > 1-epsilon] = 1 - epsilon      # TODO: use np.clip?
        p[p < epsilon] = epsilon
        # calc weights
        w = pd.Series(data=None, index=A.index)
        treatments = np.unique(A)
        for tr in treatments:
            w[A == tr] = old_div(1, p[A == tr, tr])

        if self.use_stabilized:
            for tr in treatments:
                p_tr = old_div(np.sum(A == tr), float(A.index.size))
                w[A == tr] *= p_tr

        # numeric issues - check!!!
        MM = 1e2                            # TODO: move to a global as well
        mm = 1e-6                           # TODO: why not same value as above? move it to a global as well.
        w[w > MM] = MM                      # TODO: use np.clip?
        w[w < mm] = mm

        res = {'weights': w, 'models': model}    # TODO: maybe simply return a tuple?
        return res

    def getLastWeights(self):
        """
        Returns:
            np.ndarray | list: The last weights calculated.
        """
        return self.last_weights
