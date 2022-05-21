import pandas as pd
import numpy as np

from statsmodels.stats.proportion import multinomial_proportions_confint
import moosir_feature.transformers.feature_cleaning.feature_cleaner as f_cleaner
import moosir_feature.transformers.tsfresh_features.feature_manager as f_tsfresh
import moosir_feature.transformers.basic_features.feature_calculator as f_basic
import moosir_feature.transformers.indicators.feature_manager as f_indicator
import moosir_feature.transformers.feature_selections.feature_selector as f_selector
import moosir_feature.transformers.features_common.calculator as f_common
import moosir_feature.transformers.managers.feature_manager as f_manager


def create_features(instances: pd.DataFrame,
                    feature_creator_manager: f_manager.FeatureCreatorManager
                    ):
    features_all, targets_all, _ = feature_creator_manager.create_features_and_targets(instances=instances)

    features_all = f_common.remove_ohlc_columns_if_exists(data=features_all)

    return dict(features_all=features_all, targets_all=targets_all)


def select_features(features_all: pd.DataFrame,
                    targets_all: pd.DataFrame,
                    feature_selector_manager: f_manager.FeatureSelectorManager,
                    ):
    features, targets, _ = f_common.drop_na(features=features_all, targets=targets_all)

    features_selected, targets_selected = feature_selector_manager.select_features(features=features, targets=targets)

    return dict(features_selected=features_selected, targets_selected=targets_selected)


###############
# feature selection stat significant
##################
def initial_feature_counters(features_all: pd.DataFrame):
    counters = np.zeros(len(features_all.columns))
    feature_keys = features_all.columns
    counter_dic = dict(zip(feature_keys, counters))
    return counter_dic


def update_feature_counters(features_selected: pd.DataFrame, counter_dic: dict):
    for key in features_selected.columns:
        counter_dic[key] += 1
    return counter_dic


class FeatureCVSettings:
    def __init__(self, f_confidence_win_step_perc: float,
                 f_confidence_win_len: int,
                 sample_selection_rand_threshold=1,
                 step_count=-1):
        assert 0 < f_confidence_win_step_perc < 1, "needs to be between 0 and 1"
        assert 0 < sample_selection_rand_threshold <= 1, "needs to be between 0 and 1"
        # assert f_confidence_win_len is int

        self.f_confidence_win_step_perc = f_confidence_win_step_perc
        self.f_confidence_win_len = f_confidence_win_len
        self.sample_selection_rand_threshold = sample_selection_rand_threshold
        self.step_count = step_count


def _remove_small_counter_keys(counter_dics: dict, freq_threshold: int):
    removed = {}
    res = {}
    for key in counter_dics:
        if counter_dics[key] >= freq_threshold:
            res[key] = counter_dics[key]
        else:
            removed[key] = counter_dics[key]

    return res, removed


def calculate_confidence_level(instances: pd.DataFrame,
                               feature_creator_manager: f_manager.FeatureCreatorManager,
                               feature_selector_manager: f_manager.FeatureSelectorManager,
                               feature_cv_settings: FeatureCVSettings):
    step_len = int(feature_cv_settings.f_confidence_win_len * feature_cv_settings.f_confidence_win_step_perc)

    step_count = int(len(instances) / step_len)
    if feature_cv_settings.step_count != -1:
        step_count = feature_cv_settings.step_count
        print(f"step_count overwritten by {step_count}")

    sample_rand_threshold = feature_cv_settings.sample_selection_rand_threshold

    dummy_features = create_features(instances=instances.iloc[:feature_cv_settings.f_confidence_win_len],
                                     feature_creator_manager=feature_creator_manager)

    dummy_features = dummy_features["features_all"]

    counters = initial_feature_counters(features_all=dummy_features)

    # todo: revert it" range(2)
    # for step in range(step_count-1):
    for step in range(step_count - 1):

        # should pick this window?
        rand = np.random.uniform(0, 1)
        if rand > sample_rand_threshold:
            print("sample skipped")
            continue

        start = step * step_len
        end = start + feature_cv_settings.f_confidence_win_len

        if end > len(instances):
            break
        # print('-' * 50)
        # print(f"{start}: {end}")
        active_instances = instances.iloc[start:end]

        all_result = create_features(instances=active_instances,
                                     feature_creator_manager=feature_creator_manager)

        features_all = all_result["features_all"]
        targets_all = all_result["targets_all"]

        s_result = select_features(features_all=features_all,
                                   targets_all=targets_all,
                                   feature_selector_manager=feature_selector_manager
                                   )

        features_selected = s_result["features_selected"]

        counters = update_feature_counters(features_selected=features_selected, counter_dic=counters)

    counters, removed = _remove_small_counter_keys(counter_dics=counters, freq_threshold=1)

    print("removed features for cv: ")
    print(removed)

    # calculate confidence level
    counters_values = np.array(list(counters.values()))

    ## confidence interval
    ci_selected = multinomial_proportions_confint(counters_values, alpha=0.05, method='sison-glaz')

    # prepare output
    features_cdf = pd.DataFrame({"Feature": np.array(list(counters.keys())), "Counter": counters_values})
    features_cvdf = pd.DataFrame(ci_selected, columns=["Min_cv", "Max_cv"])
    features_cvs = features_cdf.join(features_cvdf)

    print('+' * 50)
    print(features_cvs)
    print('+' * 50)
    return features_cvs
