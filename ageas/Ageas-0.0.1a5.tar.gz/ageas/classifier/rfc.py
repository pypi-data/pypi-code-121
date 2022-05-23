#!/usr/bin/env python3
"""
Ageas Reborn
Scikit-Learn Random Forest based classifier
related classes and functions

author: jy, nkmtmsys
"""


import itertools
import ageas.classifier as classifier
from sklearn.ensemble import RandomForestClassifier



class RFC(classifier.Sklearn_Template):
    """
    Build up Random Forest classifier based on given parameters
    Note:
    Shall we even try decision tree?
    """
    # Set clf to default level
    def initial(self):
        self.model_type = 'RFC'
        self.clf = RandomForestClassifier(**self.param)



class Make(classifier.Make_Template):
    """
    Analysis the performances of Random Forest based approaches
    with different hyperparameters
    Find the top settings to build RFC
    """

    # Perform classifier training process for given times
    def train(self, dataSets, test_split_set):
        for id in self.configs:
            # Initialize RFC model
            model = RFC(id, self.configs[id]['config'])
            model.train(dataSets.dataTrain, dataSets.labelTrain)
            accuracy = self._evaluate_sklearn(model,
                                                dataSets.dataTest,
                                                dataSets.labelTest,
                                                test_split_set)
            self.models.append([model, accuracy])
