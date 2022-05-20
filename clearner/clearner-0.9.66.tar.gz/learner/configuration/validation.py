# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import warnings


class ValidationConfiguration:

    def __init__(self, json_config):
        self._json_config = json_config

        self.validate = self.get_validate()

    def get_validate(self):
        try:
            validate = self._json_config["validation"]["validate"]
            if not validate:
                warnings.warn("Validation flag is set to false, this can lead to errors or unexpected results",
                              UserWarning)
            return validate
        except KeyError:
            return True
