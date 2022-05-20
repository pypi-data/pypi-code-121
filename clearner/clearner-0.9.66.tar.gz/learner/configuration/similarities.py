# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

from learner.data_worker.data_loader import get_value


class SimilaritiesConfiguration:
    """Parse all input variables related to creating a similarity matrix from the input data. Learner provides a wrapper
    around scipy distance package. Therefore, all methods supported by scipy is supported here as well."""

    def __init__(self, json_config):
        self._json_config = json_config
        self.metric = get_value(self._json_config, "jaccard", "similarities", "metric")
