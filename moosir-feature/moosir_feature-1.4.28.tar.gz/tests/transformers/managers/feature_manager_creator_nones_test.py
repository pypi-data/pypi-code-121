import pytest

from moosir_feature.transformers.managers.feature_manager import *
from moosir_feature.transformers.tsfresh_features.feature_calculator import *
from moosir_feature.transformers.indicators.feature_calculator import *
from moosir_feature.transformers.basic_features.feature_calculator import *


@pytest.fixture
def ohlc():
    df = pd.DataFrame(data=np.random.rand(100, 4),
                      columns=["Open", "High", "Low", "Close"],
                      index=pd.date_range(start="01/01/2000", periods=100, freq="10T"),
                      )
    df.index.name = "Timestamp"
    return df


def _print(features, targets, all):
    print(features)
    print(features.columns)
    print('-' * 50)
    print(targets)
    print(targets.columns)
    print('-' * 50)
    print(all)
    print(all.columns)


def _get_target_settings(setting_key: str):
    ind = IndicatorTargetSettings(**{
        'win_len': 80,
        'lookahead_len': 3,
        'feature_name': RsiOperator.__name__,
        'target_col_feature_type': 'Rsi',
        'target_col_feature_subtype': RsiOperator.get_column_names()[0],
    })
    settings = {"ind": ind}
    return settings[setting_key]


def _get_feature_settings(setting_key: str):
    ind = IndicatorFeatureSettings(**{
        'win_lens': [70],
        'feature_names': [ReturnsOperator.__name__]
    })

    settings = {"ind": ind}
    return settings[setting_key]


def _get_lag_settings(setting_key: str):
    ind = IndicatorLagSettings(**{'feature_parameters':
        {
            'win_lens': [30],
            'feature_names': [MaOperator.__name__]
        },
        'lag_lens': [3]
    })
    settings = {"ind": ind}
    return settings[setting_key]


def _run_manager(ohlc, target_settings, feature_settings_list, lag_settings_list):
    mgr = FeatureCreatorManager(target_settings=target_settings,
                                feature_settings_list=feature_settings_list,
                                lag_settings_list=lag_settings_list
                                )

    # act
    features, targets, all = mgr.create_features_and_targets(instances=ohlc)

    return features, targets, all


def _get_indicator_operators(feature_names: list):
    return [OPERATORS_IND[f] for f in feature_names]


def _assert_tsfresh_features(features, feature_settings_list):
    for f_settings in feature_settings_list:
        assert validate_columns(data=features,
                                feature_names=f_settings.feature_names,
                                win_lens=f_settings.win_lens)


def _assert_tsfresh_lags(features, lag_settings_list):
    for l_settings in lag_settings_list:
        assert validate_columns(data=features,
                                feature_names=l_settings.feature_names,
                                win_lens=l_settings.win_lens)


def _assert_indicator_lags(features, context, lag_settings_list):
    for l_settings in lag_settings_list:
        lag_ops = _get_indicator_operators(l_settings.feature_names)
        assert context.validate(features,
                                operators=lag_ops,
                                periods=l_settings.win_lens,
                                lag_periods=l_settings.lag_lens)


def _assert_indicator_features(context, features, feature_settings_list):
    for f_settings in feature_settings_list:
        feature_ops = _get_indicator_operators(f_settings.feature_names)
        assert context.validate(features, operators=feature_ops, periods=f_settings.win_lens)


#
def test_feature_manager_calculate_when_lag_is_empty(ohlc: pd.DataFrame):
    # arrange
    target_settings = _get_target_settings("ind")
    feature_settings_list = [_get_feature_settings("ind")]
    lag_settings_list = []

    # act
    features, targets, all = _run_manager(ohlc=ohlc,
                                          target_settings=target_settings,
                                          feature_settings_list=feature_settings_list,
                                          lag_settings_list=lag_settings_list)

    _print(features, targets, all)
    # assert
    context = Context()

    # assert features
    _assert_indicator_features(features=features, context=context, feature_settings_list=feature_settings_list)

    # assert targets
    fwd_ops = _get_indicator_operators([target_settings.feature_name])
    assert context.validate(targets,
                            operators=fwd_ops,
                            periods=[target_settings.win_len],
                            forward_periods=[target_settings.lookahead_len])


def test_feature_manager_calculate_when_features_is_empty(ohlc: pd.DataFrame):
    # arrange
    target_settings = _get_target_settings("ind")
    feature_settings_list = []
    lag_settings_list = [_get_lag_settings("ind")]

    # act
    features, targets, all = _run_manager(ohlc=ohlc,
                                          target_settings=target_settings,
                                          feature_settings_list=feature_settings_list,
                                          lag_settings_list=lag_settings_list)

    _print(features, targets, all)
    # assert
    context = Context()

    # assert targets
    fwd_ops = _get_indicator_operators([target_settings.feature_name])
    assert context.validate(targets,
                            operators=fwd_ops,
                            periods=[target_settings.win_len],
                            forward_periods=[target_settings.lookahead_len])

    # assert lags
    _assert_indicator_lags(features=features, context=context, lag_settings_list=lag_settings_list)
