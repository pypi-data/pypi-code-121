import numpy as np

from kolibri.core.component import Component
from kdmt.dict import update
import pickle

class BaseFeaturizer(Component):

    component_type="transformer"

    defaults = {
            "fixed": {

                # list of stop words
                "stop-words": None,  # string {'en'}, list, or None (default)
                # limit vocabulary size

                # if convert all characters to lowercase
                "case-sensitive": True,  # bool
                "use-bigram-model": False,
                "filter-stopwords": True,
            },

            "tunable": {
                "do-lower-case": {
                    "description": "If True all text will be converted to lower case",
                    "value": True,
                    "type": "boolean",
                    "values": [True, False],
                },
                "max-features": {
                    "description": "keeps only to 'max-features'",
                    "value": 2000,
                    "type": "integer",
                    "values": [1000, 10000],
                },
            }
        }

    def __init__(self, config):

        super().__init__(config)
        self.vectorizer = None

    def update_default_hyper_parameters(self):
        self.defaults=update(self.defaults, BaseFeaturizer.defaults)
        super().update_default_hyper_parameters()


