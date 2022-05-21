from moosir_feature.transformers.indicators.tech_indicators import *
from moosir_feature.transformers.indicators.contexts import OPERATORS_IND
import moosir_feature.transformers.tsfresh_features.feature_calculator  as tsf
import moosir_feature.transformers.signal_features.feature_calculator  as sig


class Settings:
    pass


###############
# features
###############

class FeatureSettings:
    pass


class TsfreshFeatureSettings(FeatureSettings):
    def __init__(self, win_lens, feature_names):
        self.win_lens = win_lens
        if "all" in feature_names:
            self.feature_names = list(tsf.FEATURES_SCHEMA_DICS.keys())
        else:
            self.feature_names = feature_names


class IndicatorFeatureSettings(FeatureSettings):
    def __init__(self, win_lens, feature_names):
        self.win_lens = win_lens  # [80]
        # todo: shameful
        if "all" in feature_names:
            self.feature_names = list(OPERATORS_IND.keys())
        else:
            self.feature_names = feature_names  # [VilliamrOperator.__name__]


class BasicFeatureSettings(FeatureSettings):
    def __init__(self, feature_names):
        self.feature_names = feature_names  # ["Hour"]

class SignalFeatureSettings(FeatureSettings):
    def __init__(self, win_lens, feature_names):
        self.win_lens = win_lens
        if "all" in feature_names:
            self.feature_names = list(sig.FEATURES_SCHEMA_DICS.keys())
        else:
            self.feature_names = feature_names

###############
# lags
###############
class LagSettings(FeatureSettings):
    pass


class TsfreshLagSettings(TsfreshFeatureSettings, LagSettings):
    def __init__(self, feature_parameters, lag_lens):
        super(TsfreshLagSettings, self).__init__(**feature_parameters)
        self.lag_lens = lag_lens


class IndicatorLagSettings(IndicatorFeatureSettings, LagSettings):
    def __init__(self, feature_parameters, lag_lens):
        super(IndicatorLagSettings, self).__init__(**feature_parameters)
        self.lag_lens = lag_lens

class SignalLagSettings(SignalFeatureSettings, LagSettings):
    def __init__(self, feature_parameters, lag_lens):
        super(SignalLagSettings, self).__init__(**feature_parameters)
        self.lag_lens = lag_lens

###############
# targets
###############

class TargetSettings:
    def __init__(self):
        pass


class TsfreshTargetSettings(TargetSettings):
    def __init__(self, win_len,
                 lookahead_len,
                 feature_name,
                 target_col_feature_type,
                 target_col_feature_subtype):
        self.win_len = win_len
        self.lookahead_len = lookahead_len
        self.feature_name = feature_name
        self.target_col_feature_type = target_col_feature_type
        self.target_col_feature_subtype = target_col_feature_subtype


class IndicatorTargetSettings(TargetSettings):
    def __init__(self, win_len,
                 lookahead_len,
                 feature_name,
                 target_col_feature_type,
                 target_col_feature_subtype):
        self.win_len = win_len
        self.lookahead_len = lookahead_len
        self.feature_name = feature_name
        self.target_col_feature_type = target_col_feature_type
        self.target_col_feature_subtype = target_col_feature_subtype

class SignalTargetSettings(TargetSettings):
    def __init__(self, win_len,
                 lookahead_len,
                 feature_name,
                 target_col_feature_type,
                 target_col_feature_subtype):
        self.win_len = win_len
        self.lookahead_len = lookahead_len
        self.feature_name = feature_name
        self.target_col_feature_type = target_col_feature_type
        self.target_col_feature_subtype = target_col_feature_subtype


##############
# feature selector
##############

class FeatureSelectorSettings(TargetSettings):
    def __init__(self, features_to_select_perc):
        self.features_to_select_perc = features_to_select_perc
