#!/usr/bin/env python3
"""
Ageas Reborn
Scikit-Learn Support Vector Machine based classifier
related classes and functions

author: jy, nkmtmsys
"""


import itertools
import ageas.classifier as classifier
from sklearn import svm



class SVM(classifier.Sklearn_Template):
    """
    Build up SVM classifier based on given parameters
    Note:
    kerenl = {‘linear’, ‘poly’, ‘rbf’, ‘sigmoid’, ‘precomputed’}
    https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html
    """
    # Set clf to default level
    def initial(self):
        self.model_type = 'SVM'
        self.clf = svm.SVC(**self.param)



class Make(classifier.Make_Template):
    """
    Analysis the performances of SVM based approaches
    with different hyperparameters
    Find the top settings to build SVM
    """

    # Perform classifier training process for given times
    def train(self, dataSets, test_split_set):
        for id in self.configs:
            # Initialize SVM model
            model = SVM(id, self.configs[id]['config'])
            model.train(dataSets.dataTrain, dataSets.labelTrain)
            accuracy = self._evaluate_sklearn(model,
                                                dataSets.dataTest,
                                                dataSets.labelTest,
                                                test_split_set)
            self.models.append([model, accuracy])
