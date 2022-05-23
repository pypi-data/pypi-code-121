#!/usr/bin/env python3
"""
Ageas Reborn
XGBoost Gradient Boosting based classifier related classes and functions

author: jy, nkmtmsys
"""

import itertools
from xgboost import XGBClassifier
import ageas.classifier as classifier


class XGB(classifier.Sklearn_Template):
    """
    Build up XGB classifier based on given parameters
    """
    # Set clf to default level
    # Turned off label encoder as official doc recommended
    def initial(self):
        self.model_type = 'XGB_GBM'
        self.clf = XGBClassifier(**self.param, use_label_encoder = False)



class Make(classifier.Make_Template):
    """
    Analysis the performances of XGB based approaches
    with different hyperparameters
    Find the top settings to build XGB
    """
    # Perform classifier training process for given times
    def train(self, dataSets, test_split_set):
        for id in self.configs:
            # Initialize XGB model
            model = XGB(id, self.configs[id]['config'])
            model.train(dataSets.dataTrain, dataSets.labelTrain)
            accuracy = self._evaluate_sklearn(model,
                                                dataSets.dataTest,
                                                dataSets.labelTest,
                                                test_split_set)
            self.models.append([model, accuracy])
