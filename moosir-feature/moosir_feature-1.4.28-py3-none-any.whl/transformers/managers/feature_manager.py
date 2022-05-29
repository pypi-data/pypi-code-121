import pandas as pd

import moosir_feature.transformers.feature_cleaning.feature_cleaner as f_cleaner
import moosir_feature.transformers.tsfresh_features.feature_manager as f_tsfresh
import moosir_feature.transformers.basic_features.feature_calculator as f_basic
import moosir_feature.transformers.indicators.feature_manager as f_indicator
import moosir_feature.transformers.feature_selections.feature_selector as f_selector
import moosir_feature.transformers.features_common.calculator as f_common
import moosir_feature.transformers.signal_features.feature_manager as f_sig

from .settings import *


def _create_targets(clean_data: pd.DataFrame,
                    target_settings: TargetSettings
                    ):
    target_eng = []

    if type(target_settings).__name__ == TsfreshTargetSettings.__name__:
        target_eng = f_tsfresh.calculate_forwards(ohlc=clean_data,
                                                  win_lens=[target_settings.win_len],
                                                  feature_names=[target_settings.feature_name],
                                                  forward_lens=[target_settings.lookahead_len])

        target_col = f_tsfresh.get_feature_col_by_subtype_name(feature_name=target_settings.feature_name,
                                                               win_len=target_settings.win_len,
                                                               subtype_name=target_settings.target_col_feature_subtype,
                                                               is_fwd=True,
                                                               fwd_len=target_settings.lookahead_len)

    elif type(target_settings).__name__ == IndicatorTargetSettings.__name__:
        target_eng = f_indicator.calculate_forwards(ohlc=clean_data,
                                                    win_lens=[target_settings.win_len],
                                                    feature_names=[target_settings.feature_name],
                                                    forward_periods=[target_settings.lookahead_len])

        target_col = f_indicator.get_feature_col_by_subtype_name(
            feature_name=target_settings.target_col_feature_subtype,
            columns=target_eng.columns, is_fwd=True)

    elif type(target_settings).__name__ == SignalTargetSettings.__name__:
        target_eng = f_sig.calculate_forwards(ohlc=clean_data,
                                                win_lens=[target_settings.win_len],
                                                feature_names=[target_settings.feature_name],
                                                forward_lens=[target_settings.lookahead_len])

        target_col = f_sig.get_feature_col_by_subtype_name(
            feature_name=target_settings.target_col_feature_subtype,
            columns=target_eng.columns,
            is_fwd=True)

    if len(target_eng) == 0:
        return target_eng

    target_eng = target_eng[[target_col]]

    target_eng = f_cleaner.clip_quantile(target_eng)
    return target_eng


def _create_features(clean_data: pd.DataFrame, feature_settings: FeatureSettings):
    features_eng = clean_data.copy()
    if type(feature_settings).__name__ == TsfreshFeatureSettings.__name__:
        features_eng = f_tsfresh.calculate_features(ohlc=features_eng, win_lens=feature_settings.win_lens,
                                                    feature_names=feature_settings.feature_names)
    elif type(feature_settings).__name__ == IndicatorFeatureSettings.__name__:
        features_eng = f_indicator.calculate_features(ohlc=features_eng, win_lens=feature_settings.win_lens,
                                                      feature_names=feature_settings.feature_names)
    elif type(feature_settings).__name__ == BasicFeatureSettings.__name__:
        features_eng = f_basic.calculate_features(ohlc=features_eng,
                                                  feature_names=feature_settings.feature_names)
    elif type(feature_settings).__name__ == SignalFeatureSettings.__name__:
        features_eng = f_sig.calculate_features(ohlc=features_eng, win_lens=feature_settings.win_lens,
                                                    feature_names=feature_settings.feature_names)

    else:
        raise Exception(f"feature calculator is not implemented: {type(feature_settings).__name__}")

    features_eng = f_cleaner.clip_quantile(features_eng)
    features_eng = f_common.remove_ohlc_columns_if_exists(data=features_eng)
    features = features_eng.copy()

    return features


def _create_lags(ohlc: pd.DataFrame,
                 lag_settings: LagSettings
                 ):
    if type(lag_settings).__name__ == TsfreshLagSettings.__name__:
        feature_lags = f_tsfresh.calculate_lags(ohlc=ohlc, win_lens=lag_settings.win_lens,
                                                lag_lens=lag_settings.lag_lens,
                                                feature_names=lag_settings.feature_names)
    elif type(lag_settings).__name__ == IndicatorLagSettings.__name__:
        feature_lags = f_indicator.calculate_lags(ohlc=ohlc, win_lens=lag_settings.win_lens,
                                                  lag_lens=lag_settings.lag_lens,
                                                  feature_names=lag_settings.feature_names)
    elif type(lag_settings).__name__ == SignalLagSettings.__name__:
        feature_lags = f_sig.calculate_lags(ohlc=ohlc, win_lens=lag_settings.win_lens,
                                                  lag_lens=lag_settings.lag_lens,
                                                  feature_names=lag_settings.feature_names)

    return feature_lags


def _create_features_list(data: pd.DataFrame, feature_settings_list: list):
    features_temps = []
    for f_settings in feature_settings_list:
        features = _create_features(clean_data=data.copy(),
                                    feature_settings=f_settings)
        features_temps.append(features)
    results = f_common.combine_features(features_list=features_temps)

    return results


def _create_lags_list(data: pd.DataFrame, lag_settings_list: list):
    features_temps = []
    for f_settings in lag_settings_list:
        features = _create_lags(ohlc=data.copy(),
                                lag_settings=f_settings)
        features_temps.append(features)
    results = f_common.combine_features(features_list=features_temps)

    return results


class FeatureSelectorManager:
    def __init__(self, feature_selector_settings: FeatureSelectorSettings):
        self.feature_selector_settings = feature_selector_settings

    def select_features(self, features: pd.DataFrame, targets: pd.DataFrame):
        features = f_selector.remove_low_variance_features(features=features)

        assert len(
            features.columns) > 1, f"number of features needs to be more than 1. features n: {len(features.columns)}"
        n_features_to_select = max(2,
                                   int(len(features.columns) * self.feature_selector_settings.features_to_select_perc))

        features = f_selector.remove_features_recursively(features=features, targets=targets,
                                                          n_features_to_select=n_features_to_select)

        return features, targets


def _remove_target_cols(feature_settings_list: FeatureSettings, target_col: str):
    for feature_settings in feature_settings_list:
        f_names = []
        for f in feature_settings.feature_names:
            if f != target_col:
                f_names.append(f)
        feature_settings.feature_names = f_names


class FeatureCreatorManager:
    def __init__(self,
                 target_settings: TargetSettings,
                 feature_settings_list: list,
                 lag_settings_list: list
                 ):
        # basic
        self.resample_freq = "5T"

        # targets
        self.target_settings = target_settings

        # features
        self.feature_settings_list = feature_settings_list

        # lag and lookahead
        self.lag_settings_list = lag_settings_list

    def create_features_and_targets(self, instances: pd.DataFrame):
        features, clean_data = self.create_features(instances=instances)

        targets = _create_targets(clean_data=clean_data.copy(),
                                  target_settings=self.target_settings)

        features, targets, all = f_common.align_features_and_targets(features=features, targets=targets)
        return features, targets, all

    def create_features(self, instances: pd.DataFrame):
        clean_data = f_cleaner.apply_basic_cleaning(instances=instances,
                                              resample_freq=self.resample_freq)

        features = _create_features_list(data=clean_data.copy(),
                                         feature_settings_list=self.feature_settings_list)

        features_lags = _create_lags_list(data=clean_data.copy(),
                                          lag_settings_list=self.lag_settings_list)

        if len(features) != 0 and len(features_lags) != 0:
            assert not bool(set(features.columns) & set(features_lags.columns)), "features and lag features have common features"

        features = f_common.combine_features(features_list=[features_lags, features])

        if len(features) == 0:
            return features, clean_data

        features = f_common.add_ohlc(data=features, ohlc=clean_data)

        return features, clean_data



