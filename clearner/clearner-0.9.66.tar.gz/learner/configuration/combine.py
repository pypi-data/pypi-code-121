# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import logging

from learner.data_worker.data_loader import get_value
from learner.validator.input_validator import validate_subset_list
from learner.configuration.supported_items import SUPPORTED_ENGINES_FOR_TRIAD_COMBINE, SUPPORTED_SCORE_TYPES, \
    SUPPORTED_MEAN_COMBINE_TYPES, SUPPORTED_ENGINES_FOR_MEAN_COMBINE


class CombineConfiguration:
    """Parse all input variables related to combining the predictions of multiple models."""

    def __init__(self, json_config, model, sep_timetag, output, engine, data):
        self._json_config = json_config
        self._model = model
        self.sep_timetag = sep_timetag
        self._output = output
        self._engine = engine
        self._data = data
        self.mean_activate = self.get_mean_activate()
        self.mean_type = self.get_mean_type()

        self.triad_activate = self.get_triad_activate()
        self.triad_score_type = self.get_triad_score_type()
        self.triad_models_step_size = get_value(self._json_config, 0.01, "combine", "triad_params", "models_step_size")
        self.triad_models_max_iter = get_value(self._json_config, 1000, "combine", "triad_params", "models_max_iter")
        self.triad_triads_step_size = get_value(self._json_config, 0.001, "combine", "triad_params", "triads_step_size")
        self.triad_triads_max_iter = get_value(self._json_config, 10000, "combine", "triad_params", "triads_max_iter")

    def get_mean_activate(self):
        try:
            activate = self._json_config["combine"]["mean_params"]["activate"]
            # if we only have one model, activating combine won't make sense.
            if activate:
                validate_subset_list(parent_list=SUPPORTED_ENGINES_FOR_MEAN_COMBINE,
                                     parent_name="acceptable engines for mean combining method",
                                     subset_list=[self._engine],
                                     subset_name="the defined engine")

                if self._model.train_models and self._model.num_models == 1:
                    logging.critical("Combine functionality was activated but only one model is defined. Please "
                                     "update your configuration file and try again. Exiting...")
                    sys.exit(1)
            return activate
        except KeyError:
            return False

    def get_mean_type(self):
        try:
            mean_type = self._json_config["combine"]["mean_params"]["type"]
            validate_subset_list(parent_list=SUPPORTED_MEAN_COMBINE_TYPES,
                                 parent_name="supported mean types for combining the models",
                                 subset_list=[mean_type],
                                 subset_name="the defined mean type")
            return mean_type
        except KeyError:
            return "arithmetic"

    def get_triad_activate(self):
        try:
            activate = self._json_config["combine"]["triad_params"]["activate"]
            if activate:
                validate_subset_list(parent_list=SUPPORTED_ENGINES_FOR_TRIAD_COMBINE,
                                     parent_name="acceptable engines for triad combining method",
                                     subset_list=[self._engine],
                                     subset_name="the defined engine")

                # we need to activate scoring_params is we are training the models and doing triad combine
                if self._model.train_models and not self._data.validation_score_activate:
                    self._data.validation_score_activate = True

                # if we only have one model, activating combine won't make sense.
                # (n & (n - 1)) == 0 is bit manipulation to check if n is a power of 2
                if self._model.num_models == 1 or not (self._model.num_models & (self._model.num_models - 1)) == 0:
                    logging.critical(f"The number of models should be a multiple of 2 when activating triad combine "
                                     f"functionality but you defined {self._model.num_models} models. Please "
                                     f"update your configuration file and try again. Exiting...")
                    sys.exit(1)
            return activate
        except KeyError:
            return False

    def get_triad_score_type(self):
        try:
            score_type = self._json_config["combine"]["triad_params"]["score_type"]
            if self.triad_activate:
                if score_type not in SUPPORTED_SCORE_TYPES[self._engine]:
                    logging.error("The score_type defined in triad_params is invalid, supported score types for %s engine "
                                  "are %s. Exiting...", self._engine, sorted(SUPPORTED_SCORE_TYPES[self._engine]))
                    sys.exit(1)
            return score_type
        except KeyError:
            return "root_mean_squared_error"
