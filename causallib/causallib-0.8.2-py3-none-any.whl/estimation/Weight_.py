"""
(C) IBM Corp, 2016, All rights reserved
Created on August 23, 2017

@author: Pierre Thodoroff
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from past.utils import old_div

import numpy as np
import sklearn.metrics as metrics
from pandas import DataFrame as pdDataFrame, Series as pdSeries  # for docstring purposes

from .Estimators_ import CounterfactualEstimator, toNdArray


class WEstimator(CounterfactualEstimator):
    """
    classdocs
    """
    # TODO: HIGHLY SIMILAR TO IPW!
    def __init__(self, treatmentLearner,method='IPW', effectTypes=None, useStabilized=True, fit_params=None):
        """
        Constructor
        Args:
            treatmentLearner (Learner): Learning models whose outputs' type is same as the treatment variable (or the
                                         censoring masking, if used to learn informative censoring).
            effectTypes (str | list[str]): The types of causal effect. e.g. difference between average causal effect or
                                            the ratio. Possible values are defined in ????
            useStabilized (bool): Whether to re-weigh the learned weights with the prevalence of the treatment.
                                   See Also: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4351790/#S6title
            fit_params (dict): Keyword-param pairs to be passed to the learner as kwargs. Must match that scikit-leaner
                               parameters.
        """
        if effectTypes is None:
            effectTypes = ['diff']
        if fit_params is None:
            fit_params = {}
        super(WEstimator, self).__init__(effectTypes)
        self.treatmentLearner = treatmentLearner
        self.useStabilizied = useStabilized
        self.lastWeights = []  # TODO: why not initiate None, calling before initiation? so why not consistent with empty ndarray? in addition, maybe final_weights better?
        self.fit_params = fit_params
        self.method = method

    def estimateCounterfactuals(self, Y, A, X, C=None):
        """
        Estimate counter-factual outcomes using weights accounting for both treatment assignment and informative (bias-
        causing) censoring.

        Args:
            Y (np.ndarray | pdSeries): A vector of length N of the measured outcome. Coercible to np.ndarray
            A (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            X (np.ndarray | pdDataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray
            C (np.ndarray | pdSeries): A binary vector of length N indicating censored individuals.
                                       Coercible to np.ndarray:

        Returns:

        """
        if C is None:
            res = self.computeWeights(X, A)
        else:
            XA = np.column_stack((X,A))
            resC = self.computeWeights( XA, C==0, label="censoring")    # TODO: better treat it as boolean rather than 1 and 0?
            resA = self.computeWeights(X, A)
            wC = resC['weights']
            wA = resA['weights']
            res = {'weights': wC * wA, 'modelC': resC['models'], 'modelA': resA['models'], 'weightsC':wC, 'weightsA':wA}
            
        weights = res['weights']


        self.lastWeights = weights
        Y = toNdArray(Y)
        if C is None:
            res['EY1'] = np.average(Y[A == 1], axis=0, weights=weights[A == 1])
            res['EY0'] = np.average(Y[A == 0], axis=0, weights=weights[A == 0])
        else:
            res['EY1'] = np.average(Y[(A == 1) & (C==0)], axis=0, weights=weights[(A == 1) & (C==0)])
            res['EY0'] = np.average(Y[(A == 0) & (C==0)], axis=0, weights=weights[(A == 0) & (C==0)])
            
        return res

    def computeWeights(self, X, A, label=None):
        """
        Estimate propensity scores and inverse it into weights.

        Args:
            X (np.ndarray | pdDataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray
            A (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            label (str):

        Returns:
            dict: two-item dictionary:

                * *weights* (np.ndarray): An N-sized vector with weight for each sample in X
                * *models* (Model): A fitted learning models.
        """
        model = None
        if self.method == 'balance_weight': # if the flag is balance_weight run adversarial method
            model = self.treatmentLearner.train(X, A, **self.fit_params)
            w =  model.model.named_steps['adv'].w
        elif self.method == 'IPW' : # if the flag is IPW then run the IPW method
            model = self.treatmentLearner.train(X, A, **self.fit_params)
            p = model.predictTrain(X)
            aucVal = metrics.roc_auc_score(A, p)
            
            epsilon = 1e-5
            p[p > 1-epsilon] = 1 - epsilon
            p[p < epsilon] = epsilon

            w = np.empty(p.shape)
            w[:] = np.NaN
            w[A == 1] = old_div(1, p[A == 1])
            w[A == 0] = old_div(1, (1 - p[A == 0]))
            if self.useStabilizied:
                pA = old_div(sum(A == 1), float(len(A)))
                w[A == 1] *= pA
                w[A == 0] *= (1 - pA)
        else:
            print("Wrong method keyword")           # TODO: no, should raise, not continue.
            w = np.ones(p.shape)

        # numeric issues - check!!!
        MM = 1e2
        mm = 1e-6
        w[w > MM] = MM
        w[w < mm] = mm

        res = {'weights': w, 'models': model}
        return res


    def getLastWeights(self):
        """
        Returns:
            np.ndarray | list: Last calculated weights
        """
        # TODO: maybe make to internal last_Weights? one for treatment and one for censoring?
        return self.lastWeights
