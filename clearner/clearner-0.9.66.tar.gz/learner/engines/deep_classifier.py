# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements the DeepClassifier engine. Please note that the majority of the functionality is implemented
in the base class"""

import logging

from learner.configuration.configuration import Configuration
from learner.utilities.timer import timeit
from learner.model_manager.scoring_manager import ClassifierScorer
from learner.combine.combining_manager import MeanClassifierCombiner
from learner.engines.base_deep_engine import BaseDeep


class DeepClassifier(BaseDeep):
    def __init__(self, conf: Configuration):
        """Take a conf object (from the Configuration class) to run a deep_classifier engine.

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
            scorer = ClassifierScorer(self.conf, self.models_dict, self.processor)
            scorer.score()
