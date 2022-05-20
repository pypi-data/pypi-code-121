# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements the DeepRegressor module. Please note that the majority of the functionality is implemented
in the base class"""

import sys
import logging

from learner.configuration.configuration import Configuration
from learner.utilities.timer import timeit
from learner.model_manager.scoring_manager import RegressorScorer
from learner.combine.combining_manager import MeanRegressorCombiner
from learner.engines.base_deep_engine import BaseDeep
from learner.combine.combining_manager import TriadCombiner


class DeepRegressor(BaseDeep):
    def __init__(self, conf: Configuration):
        """Take a conf object (from the Configuration class) to run a deep_regressor engine.

        :param conf: a conf object
        """
        super().__init__(conf)

    @timeit("compute the predictions scores")
    def score_prediction(self):
        """Score the predictions of the models.

        :return: None
        """
        if self._conf.data.validation_score_activate:
            logging.info("Computing the prediction scores...")
            scorer = RegressorScorer(self.conf, self.models_dict)
            scorer.score()


