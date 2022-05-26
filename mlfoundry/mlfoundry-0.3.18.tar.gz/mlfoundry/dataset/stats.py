import typing

import pandas as pd
import whylogs
from google.protobuf.json_format import MessageToDict

from mlfoundry.dataset.types import DatasetStats, Profiles
from mlfoundry.dataset.whylogs_types import DataFrameSummary


def profile_to_summary(
    profile: whylogs.DatasetProfile, data: pd.DataFrame
) -> DataFrameSummary:
    dict_profile = MessageToDict(profile.to_summary(), preserving_proto_field_name=True)
    summary = DataFrameSummary(**dict_profile)
    for col in summary.columns.keys():
        if summary.columns[col].number_summary is None:
            summary.columns[col].set_value_count_summary(data[col])
    return summary


def build_stats(
    features: pd.DataFrame,
    predictions: typing.Optional[pd.Series],
    actuals: typing.Optional[pd.Series],
) -> typing.Tuple[DatasetStats, Profiles]:
    features_profile = whylogs.DatasetProfile("features")
    features_profile.track_dataframe(features)
    features_summary = profile_to_summary(features_profile, features)

    predictions_profile = None
    predictions_summary = None
    if predictions is not None:
        predictions_df = pd.DataFrame()
        predictions_df["predictions"] = predictions
        predictions_profile = whylogs.DatasetProfile("predictions")
        predictions_profile.track_dataframe(predictions_df)
        predictions_summary = profile_to_summary(predictions_profile, predictions_df)

    actuals_profile = None
    actuals_summary = None
    if actuals is not None:
        actuals_df = pd.DataFrame()
        actuals_df["actuals"] = actuals
        actuals_profile = whylogs.DatasetProfile("actuals")
        actuals_profile.track_dataframe(actuals_df)
        actuals_summary = profile_to_summary(actuals_profile, actuals_df)

    dataset_stats = DatasetStats(
        features=features_summary,
        predictions=predictions_summary,
        actuals=actuals_summary,
    )

    profiles = Profiles(
        features=features_profile,
        actuals=actuals_profile,
        predictions=predictions_profile,
    )
    return dataset_stats, profiles
