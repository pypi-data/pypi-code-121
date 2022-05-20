# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

from learner.data_worker.data_loader import get_value


class RecommenderConfiguration:
    """Parse all input variables related to recommender engine including the minimum and maximum length for a basket
    of a product."""

    def __init__(self, json_config):
        self._json_config = json_config
        self.support_cutoff = get_value(self._json_config, 0.2, "recommender", "support_cutoff")
        self.min_length = get_value(self._json_config, 1, "recommender", "min_length")
        self.max_length = get_value(self._json_config, 10, "recommender", "max_length")
        self.max_num_category = get_value(self._json_config, 100, "recommender", "max_num_category")
        self.activate = get_value(self._json_config, True, "recommender", "extend_params", "activate")
        self.num_recs = get_value(self._json_config, 5, "recommender", "extend_params", "num_recs")

