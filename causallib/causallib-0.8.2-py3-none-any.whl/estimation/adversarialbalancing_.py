"""
(C) IBM Corp, 2016, All rights reserved
Created on August 23, 2017

@author: Pierre Thodoroff
"""
from __future__ import division
from builtins import object, range
from past.utils import old_div

import copy

import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_predict
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight

"""
The goal of this method is to find weights such that the reweighted population under any treatment A, looks like the true population.
The main idea is that for each treatment A the algorithm find weights such that a specified classifier can not distinguish between 
the all population and the weighted population under treatment a. In a similar fashion to adaboost at each step we will change the weights
of the population under treatment A such as to "fool" the models/discriminator. For example the examples that the classifier correctly predicted
will be assigned a smaller weights and the one were it failed a larger one. At each step we update the weights using the gradient of the exponential
loss function. It yields a similar update to adaboost.
"""


class AdversarialBalancing(object):
    # TODO: maybe inherent from sklearn.base.BaseEstimator, since it provides fit.
    def __init__(self, model, iterations=15, lr=0.15, cv=5, decay=0.3):
        """
        Constructor

        Args:
            model (classifier): object implementing fit and predict(scikit-learn classifier for example)
                                It will be used to discriminate between the population under treatment a and the
                                global population
            iterations (int): The number of iterations to adjust the weights of each sample
            lr (float): Learning rate used to update the weights
            cv (int): Number of folds used to get the predicted values at each iteration
            decay (float):  Parameter to decay the learning rate through the iterations
        """
        self.model = model
        self.lr = lr
        self.iterations = iterations
        self.cv = cv                    # TODO: change to n_splits? to match with sklearn notation
        self.decay = decay
        self.w = None

    """ 
    Find the weights that adjust the population under all treatments a to resemble the true population 
    with respect to a class of classifier
    """

    def fit(self, X, A):
        """
        Calculate balancing weights
        Args:
            X (np.array): A covariate matrix
            A (np.array): A treatment assignment vector

        Returns:
            np.array: Weights. A weight for each sample.
        """
        # TODO: maybe check sizes between X and A?
        w = np.ones((X.shape[0]))  # Weights to be returned
        for a in range(np.unique(A).shape[0]):  # For all the treatment assignment possible
            """
            Create an artificial classification problem where the samples with label 1 are the true population
            and the samples with label -1 are the biased population under treatment a.
            We use the label 1 and -1 because this is needed with the exponential loss function
            """
            X_augm = np.concatenate((X, X[np.where(A == a)]))  # create the augmented dataset
            y = np.ones((X_augm.shape[0]))
            y[X.shape[0]:] *= -1
            idx_neg = np.where(y == -1)
            """
            To simplify the task(learning weights) we will make sure both classes have the same importance by reweighting 
            classes by their frequency
            """
            le = LabelEncoder()
            class_weight = compute_class_weight('balanced', np.unique(y), y)[
                le.fit_transform(y)]  # get the class weight of each sample

            sample_weight = np.ones((X_augm.shape[0]))
            lr = copy.copy(self.lr)             # TODO: redundant copy (in case lr is indeed float)
            # TODO: maybe split into smaller methods

            for i in range(self.iterations):
                pred = cross_val_predict(self.model, X_augm, y, cv=StratifiedKFold(n_splits=self.cv, shuffle=True),
                                         fit_params={'sample_weight': sample_weight * class_weight}).reshape(
                    (-1))  # get the prediction of the classifer on each fold
                sample_weight[idx_neg] *= np.exp(-lr * y[idx_neg] * pred[
                    idx_neg])  # Update the weights to minimize the loss of the generator and "fool" the classifier
                sample_weight[idx_neg] *= old_div(sample_weight[idx_neg].shape[0], np.sum(
                    sample_weight[idx_neg]))  # normalize the weights with mean 1
                lr = self.lr * (old_div(1.0, (1 + (self.decay * i))))  # decay the learning rate

            w[np.where(A == a)] = sample_weight[idx_neg]
        self.w = w
