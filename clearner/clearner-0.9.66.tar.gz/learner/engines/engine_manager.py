# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import os
from datetime import datetime

from learner.setup.parser import get_config_file
from learner.setup.setup import Setup


class EngineHandler:
    """A handler class to instantiate and run appropriate engines depending on user input and other settings."""

    def __init__(self, conf):
        self._conf = conf

        self.handle_engine()

    def handle_engine(self):
        if self._conf.engine == "Recommender" and self._conf.segmenter.activate:
            from learner.engines.recommender import RecommenderSegment
            engine = RecommenderSegment(self._conf)
        elif self._conf.engine == "Recommender":
            from learner.engines.recommender import Recommender
            engine = Recommender(self._conf)
        elif self._conf.segmenter.activate:
            from learner.engines.standard_engines import StandardEngineSegment
            engine = StandardEngineSegment(self._conf)
        elif self._conf.engine in ("Classifier", "Regressor"):
            from learner.engines.standard_engines import StandardEngine
            engine = StandardEngine(self._conf)
        elif self._conf.engine == "DeepClassifier":
            from learner.engines.deep_classifier import DeepClassifier
            engine = DeepClassifier(self._conf)
        elif self._conf.engine == "DeepRegressor":
            from learner.engines.deep_regressor import DeepRegressor
            engine = DeepRegressor(self._conf)
        elif self._conf.engine == "ImageClassifier":
            from learner.engines.image_classifier import ImageClassifier
            engine = ImageClassifier(self._conf)
        engine.run_engine()
