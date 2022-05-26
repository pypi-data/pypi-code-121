import logging
import os
import posixpath
import tempfile
import time
import typing
import uuid

import pandas as pd
from mlflow.entities import RunLog
from mlflow.tracking import MlflowClient
from whylogs import DatasetProfile

from mlfoundry import log_types
from mlfoundry.dataset.serde_utils import (
    load_dataframe,
    load_series,
    save_dataframe,
    save_series,
)
from mlfoundry.dataset.types import DatasetSchema, DatasetStats, Profiles
from mlfoundry.exceptions import MlFoundryException

DATASET_PREFIX = posixpath.join("mlf", "run-logs", "dataset")
logger = logging.getLogger(__name__)


class TabularDatasetSerDe:
    _FEATURE_ENTITY_NAME = "features"
    _PREDICTIONS_ENTITY_NAME = "predictions"
    _ACTUALS_ENTITY_NAME = "actuals"
    _SCHEMA_FILE_NAME = "schema.json"
    _STATS_FILE_NAME = "stats.json"
    _FEATURES_PROFILE_FILE_NAME = "features_profile.pb.bin"
    _PREDICTIONS_PROFILE_FILE_NAME = "predictions_profile.pb.bin"
    _ACTUALS_PROFILE_FILE_NAME = "actuals_profile.pb.bin"

    def __init__(self, mlflow_client: MlflowClient):
        self.mlflow_client: MlflowClient = mlflow_client
        self.dataset_prefix = DATASET_PREFIX

    def _load_file(
        self,
        run_id: str,
        artifact_path: str,
        deserializer: typing.Callable,
    ):
        with tempfile.TemporaryDirectory() as local_dir:
            local_path = self.mlflow_client.download_artifacts(
                run_id, artifact_path, local_dir
            )
            return deserializer(local_path)

    def _get_run_log(
        self, run_id: str, dataset_name: str, log_type: str
    ) -> typing.Optional[RunLog]:
        run_logs = self.mlflow_client.list_run_logs(
            run_uuid=run_id, key=dataset_name, log_type=log_type
        )
        if len(run_logs) == 0:
            return None
        return run_logs[0]

    def validate_dataset_is_not_already_logged(self, run_id, dataset_name):
        run_log = self._get_run_log(
            run_id=run_id,
            dataset_name=dataset_name,
            log_type=log_types.DatasetArtifact.get_log_type(),
        )
        if run_log is None:
            return
        raise MlFoundryException(f"dataset {dataset_name} is already logged")

    def save_dataset(
        self,
        run_id: str,
        dataset_name: str,
        features: pd.DataFrame,
        predictions: typing.Optional[pd.Series],
        actuals: typing.Optional[pd.Series],
        schema: DatasetSchema,
        stats: DatasetStats,
        profiles: Profiles,
        only_stats: bool,
    ) -> str:
        artifact_path = posixpath.join(
            self.dataset_prefix, dataset_name, str(uuid.uuid4())
        )
        timestamp = int(time.time() * 1000)
        run_logs = [
            log_types.DatasetArtifact(artifact_path=artifact_path).to_run_log(
                key=dataset_name, timestamp=timestamp
            )
        ]
        with tempfile.TemporaryDirectory() as local_dir:
            if not only_stats:
                file_name, file_format = save_dataframe(
                    local_dir=local_dir,
                    entity_name=TabularDatasetSerDe._FEATURE_ENTITY_NAME,
                    dataframe=features,
                )
                run_logs.append(
                    log_types.DatasetArtifactFeatures(
                        artifact_path=posixpath.join(artifact_path, file_name),
                        format=file_format,
                    ).to_run_log(key=dataset_name, timestamp=timestamp)
                )

                if predictions is not None:
                    file_name, file_format = save_series(
                        local_dir=local_dir,
                        entity_name=TabularDatasetSerDe._PREDICTIONS_ENTITY_NAME,
                        series=predictions,
                    )
                    run_logs.append(
                        log_types.DatasetArtifactPredictions(
                            artifact_path=posixpath.join(artifact_path, file_name),
                            format=file_format,
                        ).to_run_log(key=dataset_name, timestamp=timestamp)
                    )
                if actuals is not None:
                    file_name, file_format = save_series(
                        local_dir=local_dir,
                        entity_name=TabularDatasetSerDe._ACTUALS_ENTITY_NAME,
                        series=actuals,
                    )
                    run_logs.append(
                        log_types.DatasetArtifactActuals(
                            artifact_path=posixpath.join(artifact_path, file_name),
                            format=file_format,
                        ).to_run_log(key=dataset_name, timestamp=timestamp)
                    )

            run_logs.append(
                schema.to_log().to_run_log_as_artifact(
                    key=dataset_name,
                    run_id=run_id,
                    mlflow_client=self.mlflow_client,
                    file_name=TabularDatasetSerDe._SCHEMA_FILE_NAME,
                    artifact_path=artifact_path,
                )
            )
            run_logs.append(
                stats.to_log().to_run_log_as_artifact(
                    key=dataset_name,
                    run_id=run_id,
                    mlflow_client=self.mlflow_client,
                    file_name=TabularDatasetSerDe._STATS_FILE_NAME,
                    artifact_path=artifact_path,
                )
            )

            features_profile_path = os.path.join(
                local_dir, TabularDatasetSerDe._FEATURES_PROFILE_FILE_NAME
            )
            profiles.features.write_protobuf(features_profile_path)
            run_logs.append(
                log_types.DatasetArtifactFeaturesProfile(
                    artifact_path=posixpath.join(
                        artifact_path, TabularDatasetSerDe._FEATURES_PROFILE_FILE_NAME
                    )
                ).to_run_log(key=dataset_name, timestamp=timestamp)
            )

            if profiles.predictions is not None:
                predictions_profile_path = os.path.join(
                    local_dir, TabularDatasetSerDe._PREDICTIONS_PROFILE_FILE_NAME
                )
                profiles.predictions.write_protobuf(predictions_profile_path)
                run_logs.append(
                    log_types.DatasetArtifactPredictionsProfile(
                        artifact_path=posixpath.join(
                            artifact_path,
                            TabularDatasetSerDe._PREDICTIONS_PROFILE_FILE_NAME,
                        )
                    ).to_run_log(key=dataset_name, timestamp=timestamp)
                )

            if profiles.actuals is not None:
                actuals_profile_path = os.path.join(
                    local_dir, TabularDatasetSerDe._ACTUALS_PROFILE_FILE_NAME
                )
                profiles.actuals.write_protobuf(actuals_profile_path)
                run_logs.append(
                    log_types.DatasetArtifactActualsProfile(
                        artifact_path=posixpath.join(
                            artifact_path,
                            TabularDatasetSerDe._ACTUALS_PROFILE_FILE_NAME,
                        )
                    ).to_run_log(key=dataset_name, timestamp=timestamp)
                )

            self.mlflow_client.log_artifacts(
                run_id=run_id, local_dir=local_dir, artifact_path=artifact_path
            )
            self.mlflow_client.insert_run_logs(run_uuid=run_id, run_logs=run_logs)

    def load_schema(self, run_id: str, dataset_name: str) -> DatasetSchema:
        run_log = self.mlflow_client.get_latest_run_log(
            run_uuid=run_id,
            key=dataset_name,
            log_type=log_types.DatasetSchemaRunLog.get_log_type(),
        )
        return DatasetSchema.parse_obj(
            log_types.DatasetSchemaRunLog.from_run_log(run_log=run_log).value
        )

    def load_stats(self, run_id: str, dataset_name: str) -> DatasetStats:
        run_log = self.mlflow_client.get_latest_run_log(
            run_uuid=run_id,
            key=dataset_name,
            log_type=log_types.DatasetStatsRunLog.get_log_type(),
        )
        return DatasetStats.parse_obj(
            log_types.DatasetStatsRunLog.from_run_log(run_log=run_log).value
        )

    def _load_features_profile(self, run_id: str, dataset_name: str):
        run_log = self.mlflow_client.get_latest_run_log(
            run_uuid=run_id,
            key=dataset_name,
            log_type=log_types.DatasetArtifactFeaturesProfile.get_log_type(),
        )
        artifact_path = log_types.DatasetArtifactFeaturesProfile.from_run_log(
            run_log
        ).artifact_path
        return self._load_file(
            run_id=run_id,
            artifact_path=artifact_path,
            deserializer=DatasetProfile.read_protobuf,
        )

    def _load_predictions_profile(self, run_id: str, dataset_name: str):
        run_log = self._get_run_log(
            run_id=run_id,
            dataset_name=dataset_name,
            log_type=log_types.DatasetArtifactPredictionsProfile.get_log_type(),
        )
        if run_log is None:
            logger.info(f"prediction profile for {dataset_name} not found")
            return None

        artifact_path = log_types.DatasetArtifactPredictionsProfile.from_run_log(
            run_log
        ).artifact_path
        return self._load_file(
            run_id=run_id,
            artifact_path=artifact_path,
            deserializer=DatasetProfile.read_protobuf,
        )

    def _load_actuals_profile(self, run_id: str, dataset_name: str):
        run_log = self._get_run_log(
            run_id=run_id,
            dataset_name=dataset_name,
            log_type=log_types.DatasetArtifactActualsProfile.get_log_type(),
        )
        if run_log is None:
            logger.info(f"actuals profile for {dataset_name} not found")
            return None

        artifact_path = log_types.DatasetArtifactActualsProfile.from_run_log(
            run_log
        ).artifact_path
        return self._load_file(
            run_id=run_id,
            artifact_path=artifact_path,
            deserializer=DatasetProfile.read_protobuf,
        )

    def load_profiles(self, run_id: str, dataset_name: str) -> Profiles:
        features_profile = self._load_features_profile(run_id, dataset_name)
        actuals_profile = self._load_actuals_profile(run_id, dataset_name)
        predictions_profile = self._load_predictions_profile(run_id, dataset_name)
        return Profiles(
            features=features_profile,
            actuals=actuals_profile,
            predictions=predictions_profile,
        )

    def load_features(
        self, run_id: str, dataset_name: str
    ) -> typing.Optional[pd.DataFrame]:
        run_log = self._get_run_log(
            run_id=run_id,
            dataset_name=dataset_name,
            log_type=log_types.DatasetArtifactFeatures.get_log_type(),
        )
        if run_log is None:
            logger.info(f"feature of dataset {dataset_name} not found")
            return None

        artifact_path = log_types.DatasetArtifactFeatures.from_run_log(
            run_log
        ).artifact_path
        return self._load_file(
            run_id=run_id, artifact_path=artifact_path, deserializer=load_dataframe
        )

    def load_actuals(
        self, run_id: str, dataset_name: str
    ) -> typing.Optional[pd.DataFrame]:
        run_log = self._get_run_log(
            run_id=run_id,
            dataset_name=dataset_name,
            log_type=log_types.DatasetArtifactActuals.get_log_type(),
        )
        if run_log is None:
            logger.info(f"actuals of dataset {dataset_name} not found")
            return None

        artifact_path = log_types.DatasetArtifactActuals.from_run_log(
            run_log
        ).artifact_path
        return self._load_file(
            run_id=run_id, artifact_path=artifact_path, deserializer=load_series
        )

    def load_predictions(
        self, run_id: str, dataset_name: str
    ) -> typing.Optional[pd.DataFrame]:
        run_log = self._get_run_log(
            run_id=run_id,
            dataset_name=dataset_name,
            log_type=log_types.DatasetArtifactPredictions.get_log_type(),
        )
        if run_log is None:
            logger.info(f"actuals of dataset {dataset_name} not found")
            return None

        artifact_path = log_types.DatasetArtifactPredictions.from_run_log(
            run_log
        ).artifact_path
        return self._load_file(
            run_id=run_id, artifact_path=artifact_path, deserializer=load_series
        )
