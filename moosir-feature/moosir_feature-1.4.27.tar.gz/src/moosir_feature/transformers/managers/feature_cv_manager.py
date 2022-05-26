import pandas as pd

from moosir_feature.transformers.features_cv.feature_cv_manager import FeatureCVSettings, calculate_confidence_level
from moosir_feature.transformers.managers.feature_manager import FeatureCreatorManager, FeatureSelectorManager


class FeatureConfidenceLevelManager:
    def __init__(self, feature_cv_settings: FeatureCVSettings,
                 feature_creator_mgr: FeatureCreatorManager,
                 feature_selector_mgr: FeatureSelectorManager):
        self.feature_cv_settings = feature_cv_settings
        self.feature_creator_mgr = feature_creator_mgr
        self.feature_selector_mgr = feature_selector_mgr

    def calculate_cv(self, instances: pd.DataFrame):
        return calculate_confidence_level(instances=instances,
                                                feature_creator_manager=self.feature_creator_mgr,
                                                feature_selector_manager=self.feature_selector_mgr,
                                                feature_cv_settings=self.feature_cv_settings)