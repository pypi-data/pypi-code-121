import typing

import pandas as pd
from mlflow.tracking import MlflowClient

from mlfoundry.dataset.schema import build_schema
from mlfoundry.dataset.serde import TabularDatasetSerDe
from mlfoundry.dataset.stats import build_stats
from mlfoundry.dataset.types import DataSet, DatasetSchema, DatasetStats, Profiles
from mlfoundry.dataset.validation import validate_dataset, validate_dataset_name
from mlfoundry.exceptions import MlFoundryException


def pre_process_features(features) -> pd.DataFrame:
    try:
        features_df = pd.DataFrame(features).reset_index(drop=True)
        features_df.columns = features_df.columns.map(str)
        return features_df
    except Exception as ex:
        raise MlFoundryException("could not convert features to a DataFrame") from ex


def pre_process_actuals(actuals) -> pd.Series:
    try:
        return pd.Series(actuals).reset_index(drop=True)
    except Exception as ex:
        raise MlFoundryException("could not convert actuals to a Series") from ex


def pre_process_predictions(predictions) -> pd.Series:
    try:
        return pd.Series(predictions).reset_index(drop=True)
    except Exception as ex:
        raise MlFoundryException("could not convert predictions to a Series") from ex


class TabularDatasetDriver:
    """TabularDataset."""

    def __init__(self, mlflow_client: MlflowClient, run_id: str):
        self.mlflow_client: MlflowClient = mlflow_client
        self._serde: TabularDatasetSerDe = TabularDatasetSerDe(self.mlflow_client)
        self._run_id: str = run_id

    def log_dataset(
        self,
        dataset_name: str,
        features,
        predictions=None,
        actuals=None,
        only_stats: bool = False,
    ):
        """
        Log a dataset associated with a run. A dataset is a collection of features,
        predictions and actuals. Datasets are uniquely identified by the dataset_name
        under a run. They are immutable, once successfully logged, overwriting it is not allowed.

        Mixed types are not allowed in features, actuals and predictions. However, there can be
        missing data in the form of None, NaN, NA.

        :param dataset_name:    Name of the dataset. Dataset name should only contain letters,
                                numbers, underscores and hyphens.
        :type dataset_name: str
        :param features:        Features associated with this dataset.
                                This should be either pandas DataFrame or should be of a
                                data type which can be convered to a DataFrame.
        :param predictions:     Predictions associated with this dataset and run. This
                                should be either pandas Series or should be of a data type which
                                can be convered to a DataFrame. This is an optional argument.
        :param actuals:         Actuals associated with this dataset and run. This
                                should be either pandas Series or should be of a data type which
                                can be convered to a DataFrame. This is an optional argument.
        :param only_stats:      If True, then the dataset (features, predictions, actuals) is
                                not saved. Only statistics and the dataset schema will be
                                persisted. Default is False.
        :type only_stats: bool
        """
        validate_dataset_name(dataset_name)
        self._serde.validate_dataset_is_not_already_logged(
            run_id=self._run_id, dataset_name=dataset_name
        )

        features = pre_process_features(features)
        predictions = (
            predictions if predictions is None else pre_process_predictions(predictions)
        )
        actuals = actuals if actuals is None else pre_process_actuals(actuals)

        schema = build_schema(
            features=features, predictions=predictions, actuals=actuals
        )
        validate_dataset(
            features=features, predictions=predictions, actuals=actuals, schema=schema
        )
        dataset_stats, profiles = build_stats(
            features=features, predictions=predictions, actuals=actuals
        )
        self._serde.save_dataset(
            run_id=self._run_id,
            dataset_name=dataset_name,
            features=features,
            predictions=predictions,
            actuals=actuals,
            schema=schema,
            stats=dataset_stats,
            profiles=profiles,
            only_stats=only_stats,
        )

    def get_dataset(self, dataset_name: str) -> typing.Optional[DataSet]:
        """
        Returns the features, predictions, actuals associated with the dataset.
        If only_stats was set to True while logging the dataset,
        this will return None.

        :param dataset_name: Name of the dataset.
        :type dataset_name: str
        :rtype: typing.Optional[DataSet]
        """
        features = self.get_features(dataset_name)
        if features is None:
            return None
        return DataSet(
            dataset_name=dataset_name,
            features=features,
            actuals=self.get_actuals(dataset_name),
            predictions=self.get_predictions(dataset_name),
        )

    def get_features(self, dataset_name: str) -> typing.Optional[pd.DataFrame]:
        """
        Returns the features associated with the dataset.

        :param dataset_name: Name of the dataset.
        :type dataset_name: str
        :rtype: typing.Optional[pd.DataFrame]
        """
        return self._serde.load_features(run_id=self._run_id, dataset_name=dataset_name)

    def get_predictions(self, dataset_name: str) -> typing.Optional[pd.Series]:
        """
        Returns the predictions associated with the dataset.

        :param dataset_name: Name of the dataset.
        :type dataset_name: str
        :rtype: typing.Optional[pd.Series]
        """
        return self._serde.load_predictions(
            run_id=self._run_id, dataset_name=dataset_name
        )

    def get_actuals(self, dataset_name: str) -> typing.Optional[pd.Series]:
        """
        Returns the actuals associated with the dataset.

        :param dataset_name: Name of the dataset.
        :type dataset_name: str
        :rtype: typing.Optional[pd.Series]
        """
        return self._serde.load_actuals(run_id=self._run_id, dataset_name=dataset_name)

    def get_schema(self, dataset_name: str) -> DatasetSchema:
        """
        Returns the schema generated from the dataset.

        :param dataset_name: Name of the dataset.
        :type dataset_name: str
        :rtype: DatasetSchema
        """
        return self._serde.load_schema(run_id=self._run_id, dataset_name=dataset_name)

    def get_stats(self, dataset_name: str) -> DatasetStats:
        """
        Returns the statistics generated from the dataset.

        :param dataset_name: Name of the dataset.
        :type dataset_name: str
        :rtype: DatasetStats
        """
        return self._serde.load_stats(run_id=self._run_id, dataset_name=dataset_name)

    def get_profiles(self, dataset_name: str) -> Profiles:
        """
        Returns the Whylogs DatasetProfile generated from the dataset.
        There will be seperate DatasetProfiles for features, predictions and actuals

        :param dataset_name: Name of the dataset.
        :type dataset_name: str
        :rtype: Profiles
        """
        return self._serde.load_profiles(run_id=self._run_id, dataset_name=dataset_name)
