"""
Created on Mar 19, 2017

(c) IBM Corp, 2017, All rights reserved
"""

from builtins import range
from builtins import str

import numpy as np
from pandas import DataFrame as pdDataFrame, Series as pdSeries  # for docstring purposes

from .Estimators_ import CounterfactualEstimator
from .Learner_ import Learner  # For docstring purposes


class StdEstimator(CounterfactualEstimator):
    """
    Implements causal effect estimation via standardization, i.e.outcome prediction.
    """

    def __init__(self, outcome_learner, effect_types=None):
        """
        Args:
            outcome_learner (Learner): Learning models whose outputs' type is same as the outcome variable.
            effect_types (str | list[str]): The types of causal effect. e.g. difference between average causal effect or
                                            the ratio. Possible values are defined in ????
        """
        if effect_types is None:
            effect_types = ["diff"]         # TODO: redundant since it already happens in CounterFactualEstimator init.
        super(StdEstimator, self).__init__(effect_types)
        self.outcome_learner = outcome_learner

# TODO: specify what is exactly return. Maybe write a class of results instead a dictionary.

    def estimateCounterfactuals(self, Y, A, X):
        """
        Estimate counter-factual outcomes using standardization (outcome prediction).

        Args:
            Y (np.ndarray | pdSeries): A vector of length N of the measured outcome. Coercible to np.ndarray
            A (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            X (np.ndarray | pdDataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray

        Returns:
            dict: A dictionary with the different results (estimations).
        """
        # train models E(Y|A,X)
        AX = np.concatenate((np.row_stack(A), X), axis=1)
        model = self.outcome_learner.train(AX, Y)

        # impute
        res = dict()
        res['models'] = model
        treatments = np.unique(A)
        for tr in treatments:
            Y_tr = model.predictTrain(np.concatenate((tr*np.ones((A.shape[0], 1)), X), axis=1))
            res['EY'+str(tr)] = np.nanmean(Y_tr)
            res['Y'+str(tr)] = Y_tr

        if len(treatments) == 2:
            # the following line is the individual effect estimates
            for i in range(len(res['Y'+str(treatments[0])])):
                res[i] = res['Y'+str(treatments[1])][i]-res['Y'+str(treatments[0])][i]
            res['TreatedEffect'] = np.nanmean(res['Y'+str(treatments[1])][A.values == 1] -
                                              res['Y'+str(treatments[0])][A.values == 1])
            res['TreatedEffect'] = np.nanmean(res['Y'+str(treatments[1])][A == 1] - res['Y'+str(treatments[0])][A == 1])
        return res

    def estimateCounterfactualsForCompetition(self, Y, A, X):
        """

        Args:
            Y (np.ndarray | pdSeries): A vector of length N of the measured outcome. Coercible to np.ndarray
            A (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            X (np.ndarray | pdDataFrame): A matrix of dimension N-by-M of the covariates. Coercible to np.ndarray

        Returns:
            dict: A results dictionary holding the propensity ['P], the individual estimated effects ['Y0', 'Y1'],
                  the estimated average effects ['EY0', 'EY1'] the trained models ['models'] and the trained
                  propensity models ['p_model'].
        """
        # TODO: maybe delete since it is related only to the estimatorWrapper and this one is only called from within the comptetion code.
        # train models E(Y|A,X)
        AX = np.concatenate((np.row_stack(A), X), axis=1)
        model = self.outcome_learner.train(AX, Y)

        # impute
        Ya1 = model.predictTrain(np.concatenate((np.ones((A.shape[0], 1)), X), axis=1))
        Ya0 = model.predictTrain(np.concatenate((np.zeros((A.shape[0], 1)), X), axis=1))

        # compute mean counterfactual
        res = {}
        #res['models'] = models
        for i in range(len(Ya0)):
            res[str(i)] = Ya0[i]-Ya1[i]
        #res['Y0'] = Ya0
        #res['Y1'] = Ya1
        #res['EY0'] = np.nanmean(Ya0)
        #res['EY1'] = np.nanmean(Ya1)
        # we want to estimate the average effect on the treated, i.e. take a subset where Z=1 and compute mean(Y1-Y0)
        #res['TreatedEffect'] = np.nanmean(Ya1[A.values==1]-Ya0[A.values==1])
        res['TreatedEffect'] = np.nanmean(Ya1[A == 1]-Ya0[A == 1])
        return res

    def estimatorWrapper(self, D):
        # TODO: called from the competition main. Maybe should be deleted, or passed to the competition code.
        # D is a data frame, func is the estimator function.
        # It is assumed that D contains columns A for the treatment, Y for the outcome and others as covariates

        # we assume the treatment indicator is at column 0 and the outcome at column 1
        return self.estimateCounterfactualsForCompetition(Y=D[:, 1], A=D[:, 0], X=D[:, 2:])['TreatedEffect']
