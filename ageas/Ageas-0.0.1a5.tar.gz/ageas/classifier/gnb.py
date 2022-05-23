#!/usr/bin/env python3
"""
Ageas Reborn
Scikit-Learn Gaussian Naive Bayes based classifier
related classes and functions

author: jy, nkmtmsys
"""


import itertools
import ageas.classifier as classifier
from sklearn.naive_bayes import GaussianNB



class GNB(classifier.Sklearn_Template):
    """
    Build up GNB classifier based on given parameters
    Note:
    Multinomial and Complement cannot do with negative values
    So we still need Gaussian Naive Bayes in this case
    """
    # Set clf to default level
    def initial(self):
        self.model_type = 'GNB'
        self.clf = GaussianNB(**self.param)



class Make(classifier.Make_Template):
    """
    Analysis the performances of Gaussian Naive Bayes based approaches
    with different hyperparameters
    Find the top settings to build GNB
    """

    # Perform classifier training process for given times
    def train(self, dataSets, test_split_set):
        for id in self.configs:
            # Initialize SVM model
            model = GNB(id, self.configs[id]['config'])
            model.train(dataSets.dataTrain, dataSets.labelTrain)
            accuracy = self._evaluate_sklearn(model,
                                                dataSets.dataTest,
                                                dataSets.labelTest,
                                                test_split_set)
            self.models.append([model, accuracy])
