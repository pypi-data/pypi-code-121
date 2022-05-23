#!/usr/bin/env python3
"""
Ageas Reborn
Scikit-Learn Logitsic Regression based classifier
related classes and functions

author: jy, nkmtmsys
"""


import itertools
import ageas.classifier as classifier
from sklearn.linear_model import LogisticRegression



class Logit(classifier.Sklearn_Template):
    """
    Build up Logistic Regression classifier based on given parameters
    Note:
    https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html?highlight=logistic%20regression#sklearn.linear_model.LogisticRegression
    """
    # Set clf to default level
    def initial(self):
        self.model_type = 'Logit'
        self.clf = LogisticRegression(**self.param)



class Make(classifier.Make_Template):
    """
    Analysis the performances of Logistic Regression based approaches
    with different hyperparameters
    Find the top settings to build
    """

    # Perform classifier training process for given times
    def train(self, dataSets, test_split_set):
        for id in self.configs:
            # Initialize SVM model
            model = Logit(id, self.configs[id]['config'])
            model.train(dataSets.dataTrain, dataSets.labelTrain)
            accuracy = self._evaluate_sklearn(model,
                                                dataSets.dataTest,
                                                dataSets.labelTest,
                                                test_split_set)
            self.models.append([model, accuracy])
