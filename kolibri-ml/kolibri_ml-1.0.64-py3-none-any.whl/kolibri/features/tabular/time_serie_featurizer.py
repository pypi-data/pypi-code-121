import os
import time
from typing import Any, Dict, Text

import joblib
import pickle
from kdmt.dict import update
from kdmt.objects import import_or_install
import_or_install('tsfresh')

from tsfresh.feature_extraction import extract_features
from tsfresh.feature_extraction import settings
from tsfresh.utilities.dataframe_functions import impute

from kolibri.features.basefeaturizer import BaseFeaturizer
from kolibri.logger import get_logger


logger = get_logger(__name__)


class TSFeaturizer(BaseFeaturizer):
    """
    Build Time series featues
    """

    provides = ["ts_features"]

    defaults = {
            "fixed": {
                "nb-features": "effecient", #"comprehensive" or "minimal"
                "column-id": "id",
                "column-sort": "time",
                "nested": False
            },

            "tunable": {

            }
        }


    def __init__(self, hyperparameters=None):
        """Construct a new count vectorizer using the sklearn framework."""

        super().__init__(hyperparameters)
        self.ts_settings=settings.EfficientFCParameters()

        if self.get_parameter("nb-features")=="comprehensive":
            self.ts_settings=settings.ComprehensiveFCParameters()
        elif self.get_parameter("nb-features")=="minimal":
            self.ts_settings=settings.MinimalFCParameters()



    def fit(self, X, y):

        return self.transform(X)

    def transform(self, X):
        return extract_features(X, column_id='id', column_sort='time',
                                default_fc_parameters=self.ts_settings,
                                # we impute = remove all NaN features automatically
                                impute_function=impute)
