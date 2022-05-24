"""
Created on Mar 19, 2017

(c) IBM Corp, 2017, All rights reserved
"""
from __future__ import division
from __future__ import print_function

import abc

import numpy as np
import pandas as pd
from builtins import object, range
from past.utils import old_div


class CounterfactualEstimator(object):
    """
    Class defining the properties of learner (estimator) of counter-factuals outcomes.
    """
    # TODO: Consider adding __metaclass__ = abc.ABCMeta https://docs.python.org/3/library/abc.html (or the Python 2 one)

    def __init__(self, effectTypes=None):
        """
        Args:
            effectTypes (str | list[str]): The types of causal effect. e.g. difference between average causal effect or
                                           the ratio. Possible values are defined in ????
        """
        if effectTypes is None:             # TODO: change naming conventions.
            effectTypes = ['diff']          # TODO: allow for string as well, and if it is - wrap a single string with list
        self.effectTypes = effectTypes

    def getName(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def estimateCounterfactuals(self, Y, A, X):
        """
        Abstract method defining the signature for estimating counter-factuals.
        Args:
            Y (np.ndarray | pd.Series): A vector of length N of the measured outcome. Coercible to np.ndarray
            A (np.ndarray | pd.Series): A vector of length N of the treatment assignments. Coercible to np.ndarray
            X (np.ndarray | pd.DataFrame): A matrix of dimension M-by-N of the covariates. Coercible to np.ndarray

        Returns:
            dict: A dictionary with the different results (estimations).
        """

    def estimate(self, Y, A, X):
        """
        Estimates
        Args:
            Y (Any): A vector of length N of the measured outcome. This is not used and here for interface consistency.
            A (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            X (Any): A matrix of dimension N-by-M of covariates. This is not used and here for interface consistency.

        Returns:
            list[tuple[str, float]]: effect name and the estimated effect.
        """
        resCounterfactuals = self.estimateCounterfactuals(Y, np.ravel(A), X)
        EY1 = resCounterfactuals['EY1']         # TODO: make more general than explicitly EY1 and EY0?
        EY0 = resCounterfactuals['EY0']
        resEffects = computeEffects(EY1, EY0, self.effectTypes)
        #res = [('EY1', EY1), ('EY0', EY0), ('TreatedEffect',resCounterfactuals['TreatedEffect'])] + resEffects
        res= []
        for k in sorted(resCounterfactuals.keys()):
            if (k in ['EY1', 'EY0', 'TreatedEffect']) or (type(k) == type(0)):      # TODO: k isinstance int???
                res = res + [(k, resCounterfactuals[k])]        # TODO use append, this + is just confusing.
        res = res + resEffects
        # res =np.column_stack((EY1, EY0, resEffects))
        return res


class UncorrectedEstimator(CounterfactualEstimator):
    """

    """
    def __init__(self, effectTypes=None):
        if effectTypes is None:
            effectTypes = ['diff']
        super(UncorrectedEstimator, self).__init__(effectTypes)

    def estimateCounterfactuals(self, Y, A, X):
        res = {}
        res['EY1'] = np.average(Y[A == 1,], axis=0)
        res['EY0'] = np.average(Y[A == 0,], axis=0)
        return res

# TODO: it seems that APrevalenceEstimator shares some interface with CounterfactualEstimator, so shouldn't they inherit from a common Estimator?
class APrevalenceEstimator(object):
    """
    Simple estimator estimating treatment prevalence
    """
    # TODO: not adjusted for multiple treatments
    def getEstimationNames(self):
        return ['P(A=1)', 'P(A=0)', 'n(A=1)', 'n(A=0)']

    def getName(self):
        return self.__class__.__name__

    def estimate(self, Y, A, X):
        """
        Estimate treatment prevalence (what proportion of the population has that treatment) and the number of samples
        treated.
        Args:
            Y (Any): A vector of length N of the measured outcome. This is not used and here for interface consistency.
            A (np.ndarray | pdSeries): A vector of length N of the treatment assignments. Coercible to np.ndarray
            X (Any): A matrix of dimension N-by-M of covariates. This is not used and here for interface consistency.

        Returns:
            list[tuple[str, float]]: prevalence and counts of positive/negative treatment.
        """
        nA = float(np.sum(A == 1))      # TODO: generalize for multiple treatments?
        pA = old_div(nA, len(A))
        res = [('P(A=1)', pA), ('P(A=0)', 1 - pA), ('n(A=1)', nA), ('P(A=0)', len(A) - nA)]  # TODO: typo last one n(A=0)
        # TODO: why suddenly a list of tuples and not a dictionary like the others?
        return res

# TODO: have these following methods be part of Estimator class as mentioned above.
def printEstimations(name, labeledMu, sigma=None):
    """
    Pretty print of estimations.

    Args:
        name (str): Name of the estimation.
        labeledMu (list[tuple[str, float]]): list of tuples of estimation and its average effect.
        sigma (list[float]): list the same size as labeledMu, with corresponding standard deviations around the mean of
                             the estimation. Serves as confidence intervals.
    """
    print(("***** ", name))
    m = len(labeledMu)
    if sigma is None:
        sigma = np.ones(m) * np.NaN
    assert (len(sigma) == m)

    for i in range(m):
        a = labeledMu[i]
        label = a[0]
        mu = a[1]
        print((label, ":", mu, "+-", sigma[i]))


def computeEffects(EY1, EY0, effectNames):
    """

    Args:
        EY1 (float): Mean effect under intervention.
        EY0 (float): Mean effect under no intervention.
        effectNames (list[str]): The type of effects to calculate (either difference, ratio, etc.)

    Returns:
        list[tuple[str, float]]: each effect types from effectNames and the actual size of the effect.
    """
    res = []
    for effectName in effectNames:
        res += [(effectName, computeEffect(EY1, EY0, effectName))]  # TODO: use append. break down to two-steps for readability
    return res


def computeEffect(EY1, EY0, effectName):
    """
    Computes a wnated effect from two potential outcomes.
    Args:
        EY1 (np.ndarray | pd.DataFrame | float | int): Outcome under treatment.
                                                       Vector for individual outcome, scalar for average outcome.
        EY0 (np.ndarray | pd.DataFrame | float | int): Outcome under no treatment.
                                                       Vector for individual outcome, scalar for average outcome.
        effectName (str): type of effect to calculate.

    Returns:
        np.ndarray | pd.DataFrame | float | int: individual or population effect
                                                 (depending if input is vector (individual) or float( population))
    """
    # TODO: Should work for both floats and vectors (population and individual effect) so rename the EYi to Yi ?
    switchDict = {
        'diff': lambda x, y: x - y,
        'ratio': lambda x, y: old_div(x, y),
        'or': lambda x, y: old_div((old_div(x, 1) - x), (old_div(y, 1) - y))
    }
    return switchDict[effectName.lower()](EY1, EY0)


def toNdArray(X):
    """
    Convert pandas' types to numpy's
    Args:
        X (pd.DataFrame | pd.Series):

    Returns:
        np.ndarray: the numpy array representation of X.
    """
    if isinstance(X, pd.DataFrame):     # TODO: would be good for series as well.
        return X.values
    return X
