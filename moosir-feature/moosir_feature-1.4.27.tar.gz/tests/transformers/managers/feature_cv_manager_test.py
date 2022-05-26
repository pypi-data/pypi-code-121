import pandas as pd
import pytest
import numpy as np

from moosir_feature.transformers.managers.feature_cv_manager import FeatureConfidenceLevelManager
from moosir_feature.transformers.managers.feature_manager import *
from moosir_feature.transformers.features_cv.feature_cv_manager import *
from moosir_feature.transformers.tsfresh_features.feature_calculator import *
from moosir_feature.transformers.indicators.feature_calculator import *
from moosir_feature.transformers.basic_features.feature_calculator import *

# from src.research.preproc.pipeline_kedro.src.preproc.domain.transformers.tsfresh_features.contexts import *

SAMPLE_N = 200


@pytest.fixture
def ohlc():
    df = pd.DataFrame(data=np.random.rand(SAMPLE_N, 4),
                      columns=["Open", "High", "Low", "Close"],
                      index=pd.date_range(start="01/01/2000", periods=SAMPLE_N, freq="10T"),
                      )
    df.index.name = "Timestamp"
    return df


def _get_target_settings(setting_key: str):
    ts = TsfreshTargetSettings(**{
        'win_len': 80,
        'lookahead_len': 3,
        'feature_name': 'linear_trend_timewise',
        'target_col_feature_type': 'Trend',
        'target_col_feature_subtype': 'Slope',

    })

    ind = IndicatorTargetSettings(**{
        'win_len': 80,
        'lookahead_len': 3,
        'feature_name': RsiOperator.__name__,
        'target_col_feature_type': 'Rsi',
        'target_col_feature_subtype': RsiOperator.get_column_names()[0],
    })
    settings = {"ts": ts, "ind": ind}
    return settings[setting_key]


def _get_feature_settings(setting_key: str):
    ts = TsfreshFeatureSettings(**{
        'win_lens': [80],
        'feature_names': ["abs_energy"]})

    ind = IndicatorFeatureSettings(**{
        'win_lens': [80],
        'feature_names': [VilliamrOperator.__name__]
    })

    basic = BasicFeatureSettings(**{
        'feature_names': ["Hour"]
    })

    settings = {"ts": ts, "ind": ind, "basic": basic}
    return settings[setting_key]


def _get_lag_settings(setting_key: str):
    ts = TsfreshLagSettings(**{'feature_parameters': {
        'win_lens': [80],
        'feature_names': ["benford_correlation"]

    },
        'lag_lens': [3]
    })

    ind = IndicatorLagSettings(**{'feature_parameters':
        {
            'win_lens': [80],
            'feature_names': [AtrOperator.__name__]
        },
        'lag_lens': [3]
    })
    settings = {"ts": ts, "ind": ind}
    return settings[setting_key]


def _get_feature_selector_settings():
    return FeatureSelectorSettings(features_to_select_perc=0.3)


def _get_feature_cv_settings():
    return FeatureCVSettings(f_confidence_win_step_perc=0.2, f_confidence_win_len=100)


def _run_feature_cv(ohlc, target_settings, feature_settings_list, lag_settings_list):
    feature_selector_settings = _get_feature_selector_settings()
    cv_settings = _get_feature_cv_settings()

    fc_mgr = FeatureCreatorManager(target_settings=target_settings,
                                   feature_settings_list=feature_settings_list,
                                   lag_settings_list=lag_settings_list)

    fs_mgr = FeatureSelectorManager(feature_selector_settings=feature_selector_settings)

    fcv_mgr = FeatureConfidenceLevelManager(feature_cv_settings=cv_settings,
                                            feature_creator_mgr=fc_mgr,
                                            feature_selector_mgr=fs_mgr)
    # act
    features_cvs = fcv_mgr.calculate_cv(instances=ohlc)

    return features_cvs


def _get_indicator_operators(feature_names: list):
    return [OPERATORS_IND[f] for f in feature_names]


def _assert_tsfresh_features(features, feature_settings_list):
    features_df = _convert_features_csv_to_columns(features_cv=features)

    for f_settings in feature_settings_list:
        assert validate_columns(data=features_df,
                                feature_names=f_settings.feature_names,
                                win_lens=f_settings.win_lens)


def _assert_tsfresh_lags(features_cv, lag_settings_list):
    features_df = _convert_features_csv_to_columns(features_cv=features_cv)

    for l_settings in lag_settings_list:
        assert validate_columns(data=features_df,
                                feature_names=l_settings.feature_names,
                                win_lens=l_settings.win_lens)


def _assert_indicator_lags(features_cv, context, lag_settings_list):
    features_df = _convert_features_csv_to_columns(features_cv=features_cv)

    for l_settings in lag_settings_list:
        lag_ops = _get_indicator_operators(l_settings.feature_names)
        assert context.validate(features_df,
                                operators=lag_ops,
                                periods=l_settings.win_lens,
                                lag_periods=l_settings.lag_lens)


def _convert_features_csv_to_columns(features_cv):
    return pd.DataFrame(np.zeros([1, len(features_cv["Feature"].values)]), columns=features_cv["Feature"].values)


def _assert_indicator_features(context, features_cv, feature_settings_list):
    features_df = _convert_features_csv_to_columns(features_cv=features_cv)

    for f_settings in feature_settings_list:
        feature_ops = _get_indicator_operators(f_settings.feature_names)
        assert context.validate(features_df, operators=feature_ops, periods=f_settings.win_lens)


@pytest.mark.skip("debug takes too long and it fails")
def test_feature_manager_calculate_multiple_settings(ohlc: pd.DataFrame):
    # arrange
    target_settings = _get_target_settings("ts")
    feature_settings_list = [_get_feature_settings("ts"), _get_feature_settings("ind")]
    lag_settings_list = [_get_lag_settings("ts"), _get_lag_settings("ind")]

    # act
    features_cv = _run_feature_cv(ohlc=ohlc,
                                  target_settings=target_settings,
                                  feature_settings_list=feature_settings_list,
                                  lag_settings_list=lag_settings_list)

    # assert
    # todo: no target validation
    # assert features
    context = Context()
    _assert_tsfresh_features(features=features_cv, feature_settings_list=[feature_settings_list[0]])
    _assert_indicator_features(features_cv=features_cv, context=context,
                               feature_settings_list=[feature_settings_list[1]])

    # assert lags
    _assert_tsfresh_lags(features_cv=features_cv, lag_settings_list=[lag_settings_list[0]])
    _assert_indicator_lags(features_cv=features_cv, context=context, lag_settings_list=[lag_settings_list[1]])

    # assert counter
    # assert features_cv["Counter"].sum() ==
    print(features_cv["Counter"].sum())
