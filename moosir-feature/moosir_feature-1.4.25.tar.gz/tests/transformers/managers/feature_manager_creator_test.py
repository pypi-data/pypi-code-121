import pytest

from moosir_feature.transformers.managers.feature_manager import *
from moosir_feature.transformers.tsfresh_features.feature_calculator import *
from moosir_feature.transformers.indicators.feature_calculator import *
from moosir_feature.transformers.basic_features.feature_calculator import *
import moosir_feature.transformers.signal_features.feature_manager as sig_mgr


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

    sig = SignalTargetSettings(**{
        'win_len': 80,
        'lookahead_len': 3,
        'feature_name': "Peaks_All",
        'target_col_feature_type': '',
        'target_col_feature_subtype': 'Peaks_All',
    })

    settings = {"ts": ts, "ind": ind, "sig": sig}
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

    sig = SignalFeatureSettings(**{
        'win_lens': [80],
        'feature_names': ["Peaks_All"]
    })

    settings = {"ts": ts, "ind": ind, "basic": basic, "sig": sig}
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

    sig = SignalLagSettings(**{'feature_parameters':
        {
            'win_lens': [80],
            'feature_names': ["Troughs_All"]
        },
        'lag_lens': [3]
    })

    settings = {"ts": ts, "ind": ind, "sig": sig}

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


def _assert_signal_features(features, feature_settings_list):
    for f_settings in feature_settings_list:
        assert sig_mgr.validate_columns(data=features,
                                        feature_names=f_settings.feature_names,
                                        win_lens=f_settings.win_lens)


def _assert_tsfresh_lags(features, lag_settings_list):
    for l_settings in lag_settings_list:
        assert validate_columns(data=features,
                                feature_names=l_settings.feature_names,
                                win_lens=l_settings.win_lens)


def _assert_signal_lags(features, lag_settings_list):
    for l_settings in lag_settings_list:
        assert sig_mgr.validate_columns(data=features,
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
def test_feature_manager_calculate_basic_features(ohlc: pd.DataFrame):
    # arrange
    target_settings = _get_target_settings("ind")
    feature_settings = _get_feature_settings("basic")
    lag_settings_list = [_get_lag_settings("ind")]

    # act
    features, targets, all = _run_manager(ohlc=ohlc,
                                          target_settings=target_settings,
                                          feature_settings_list=[feature_settings],
                                          lag_settings_list=lag_settings_list)

    _print(features, targets, all)
    # assert
    context = Context()

    # assert features
    assert validate_basic_feature_col(data=features, feature_names=feature_settings.feature_names)

    # assert targets
    fwd_ops = _get_indicator_operators([target_settings.feature_name])
    assert context.validate(targets,
                            operators=fwd_ops,
                            periods=[target_settings.win_len],
                            forward_periods=[target_settings.lookahead_len])

    # assert lags
    _assert_indicator_lags(features=features, context=context, lag_settings_list=lag_settings_list)


def test_feature_manager_calculate_multiple_settings(ohlc: pd.DataFrame):
    # arrange
    target_settings = _get_target_settings("ts")
    feature_settings_list = [_get_feature_settings("ts"), _get_feature_settings("ind")]
    lag_settings_list = [_get_lag_settings("ts"), _get_lag_settings("ind")]

    # act
    features, targets, all = _run_manager(ohlc=ohlc,
                                          target_settings=target_settings,
                                          feature_settings_list=feature_settings_list,
                                          lag_settings_list=lag_settings_list)

    # assert
    # assert features
    context = Context()
    _assert_tsfresh_features(features=features, feature_settings_list=[feature_settings_list[0]])
    _assert_indicator_features(features=features, context=context, feature_settings_list=[feature_settings_list[1]])

    # assert targets
    # todo: cant validate subtype!!!
    # assert validate_columns(data=targets,
    #                         feature_names=[target_settings.feature_name],
    #                         win_lens=[target_settings.win_len])

    # assert lags
    _assert_tsfresh_lags(features=features, lag_settings_list=[lag_settings_list[0]])
    _assert_indicator_lags(features=features, context=context, lag_settings_list=[lag_settings_list[1]])


def test_feature_manager_calculate_tsfresh(ohlc: pd.DataFrame):
    # arrange
    target_settings = _get_target_settings("ts")
    feature_settings_list = [_get_feature_settings("ts")]
    lag_settings_list = [_get_lag_settings("ts")]

    # act
    features, targets, all = _run_manager(ohlc=ohlc,
                                          target_settings=target_settings,
                                          feature_settings_list=feature_settings_list,
                                          lag_settings_list=lag_settings_list)

    # assert
    # assert features
    _assert_tsfresh_features(features=features, feature_settings_list=feature_settings_list)

    # assert targets
    # todo: cant validate subtype!!!
    # assert validate_columns(data=targets,
    #                         feature_names=[target_settings.feature_name],
    #                         win_lens=[target_settings.win_len])

    # assert lags
    _assert_tsfresh_lags(features=features, lag_settings_list=lag_settings_list)


def test_feature_manager_calculate_indicators_tsfresh_mix(ohlc: pd.DataFrame):
    # arrange
    target_settings = _get_target_settings("ind")
    feature_settings_list = [_get_feature_settings("ts")]
    lag_settings_list = [_get_lag_settings("ind")]

    # act
    features, targets, all = _run_manager(ohlc=ohlc,
                                          target_settings=target_settings,
                                          feature_settings_list=feature_settings_list,
                                          lag_settings_list=lag_settings_list)

    # assert
    context = Context()

    # assert len(targets.columns) == 1

    # assert features
    _assert_tsfresh_features(features=features, feature_settings_list=feature_settings_list)

    # assert targets
    fwd_ops = _get_indicator_operators([target_settings.feature_name])
    assert context.validate(targets,
                            operators=fwd_ops,
                            periods=[target_settings.win_len],
                            forward_periods=[target_settings.lookahead_len])

    # assert lags
    _assert_indicator_lags(features=features, context=context, lag_settings_list=lag_settings_list)


# 
def test_feature_manager_calculate_indicators(ohlc: pd.DataFrame):
    # arrange
    target_settings = _get_target_settings("ind")
    feature_settings_list = [_get_feature_settings("ind")]
    lag_settings_list = [_get_lag_settings("ind")]

    # act
    features, targets, all = _run_manager(ohlc=ohlc,
                                          target_settings=target_settings,
                                          feature_settings_list=feature_settings_list,
                                          lag_settings_list=lag_settings_list)

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

    # assert lags
    _assert_indicator_lags(features=features, context=context, lag_settings_list=lag_settings_list)


def test_feature_manager_calculate_signals(ohlc: pd.DataFrame):
    # arrange
    target_settings = _get_target_settings("sig")
    feature_settings_list = [_get_feature_settings("sig")]
    lag_settings_list = [_get_lag_settings("sig")]

    # act
    features, targets, all = _run_manager(ohlc=ohlc,
                                          target_settings=target_settings,
                                          feature_settings_list=feature_settings_list,
                                          lag_settings_list=lag_settings_list)

    _print(features, targets, all)

    # assert
    _assert_signal_features(features=features, feature_settings_list=feature_settings_list)
    _assert_signal_lags(features=features, lag_settings_list=lag_settings_list)

