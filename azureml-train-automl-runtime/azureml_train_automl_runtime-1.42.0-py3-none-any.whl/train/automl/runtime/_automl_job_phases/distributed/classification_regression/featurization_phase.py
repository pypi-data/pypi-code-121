# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os
import uuid
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd
import dask
import numpy as np

from azureml.automl.core.shared import constants, logging_utilities
from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.core.constants import FeatureType
from azureml.automl.runtime.column_purpose_detection import ColumnPurposeDetector
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.core import Run
from azureml.data import TabularDataset
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._automl_job_phases.utilities import PhaseUtil
from azureml.train.automl.runtime._worker_initiator import EXPERIMENT_STATE_PLUGIN, get_worker_variables
from azureml.training.tabular.featurization._azureml_transformer import AzureMLTransformer
from azureml.training.tabular.featurization.categorical.prefitted_labelencoder_transformer import \
    PrefittedLabelEncoderTransformer
from azureml.training.tabular.featurization.numeric.prefitted_standard_scaler import PrefittedStandardScaler
from dask.distributed import get_worker
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


def get_numeric_pipeline(mean, std):
    return PrefittedStandardScaler(mean, std)


def get_categorical_pipeline(uniques):
    return PrefittedLabelEncoderTransformer(uniques)


def transform_one_partition(df, fitted_transformer):
    worker = get_worker()
    experiment_state_plugin = worker.plugins[EXPERIMENT_STATE_PLUGIN]
    default_datastore_for_worker, workspace_for_worker, expr_store_for_worker = get_worker_variables(
        experiment_state_plugin.workspace_getter, experiment_state_plugin.parent_run_id)

    transformed = fitted_transformer.transform(df)
    path = 'file-{}.npy'.format(str(uuid.uuid4()))

    np.save(path, transformed)
    expr_store_for_worker.data.partitioned.write_file(path, os.path.join(experiment_state_plugin.parent_run_id, path))
    return True


class ClassificationRegressionDistributedFeaturizationPhase:
    """AutoML job phase that prepares the data."""

    @staticmethod
    def run(workspace_getter: Callable[..., Any],
            current_run: Run,
            parent_run_id: str,
            automl_settings: AzureAutoMLSettings,
            training_dataset: TabularDataset,
            validation_dataset: TabularDataset) -> None:

        PhaseUtil.log_with_memory("Beginning distributed featurization")

        # get sampled dataframe and dask dataframe for use in various points of the workflow
        sampled_training_df = training_dataset.take(10000).to_pandas_dataframe()
        training_ddf = training_dataset.to_dask_dataframe()

        # step 1 - get column purposes
        with logging_utilities.log_activity(logger=logger, activity_name='get_column_purposes'):
            column_purpose_to_setofcolumns = get_column_purposes(sampled_training_df)

        # step 2 - get suggestions for transformers
        with logging_utilities.log_activity(logger=logger, activity_name='suggest_transformers'):
            all_transformers = suggest_transformers(column_purpose_to_setofcolumns, training_ddf)

        # step 3 - build the prefitted pipleine
        with logging_utilities.log_activity(logger=logger, activity_name='build_prefitted_pipeline'):
            featurization_pipeline = build_prefitted_pipeline(training_dataset, all_transformers)
            PhaseUtil.log_with_memory("Built pipeline")

        # step 4 - kick of distributed featurization
        with logging_utilities.log_activity(logger=logger, activity_name='transform_data_distributed'):
            transform_data_distributed(training_ddf, featurization_pipeline)
            PhaseUtil.log_with_memory("Ending distributed preparation.")

        # step 5 - create a dataset for later use
        with logging_utilities.log_activity(logger=logger, activity_name='save_transformer_and_dataset'):
            expr_store = ExperimentStore.get_instance()
            expr_store.transformers.set_transformers(
                {constants.Transformers.X_TRANSFORMER: featurization_pipeline})


def build_prefitted_pipeline(training_dataset: TabularDataset,
                             all_transformers: List[Tuple[str, AzureMLTransformer, List[str]]]) -> Pipeline:
    # all transformers are all prefitted or need no learning
    # hence take few samples and fit it, just to make sure the pipeline is fitted
    featurization_pipeline = Pipeline(steps=[("featurizer", ColumnTransformer(transformers=all_transformers))])
    featurization_pipeline.fit(training_dataset.take(10).to_pandas_dataframe())

    return featurization_pipeline


def transform_data_distributed(training_ddf: dask.dataframe, featurization_pipeline: Pipeline) -> None:
    # kick off distributed transformation using the fitted transformer
    training_ddf.map_partitions(transform_one_partition, featurization_pipeline, meta=bool).compute()


def get_column_purposes(sampled_training_df: pd.DataFrame) -> Dict[str, List[str]]:
    stats_and_column_purposes = ColumnPurposeDetector.get_raw_stats_and_column_purposes(sampled_training_df)
    column_purpose_to_setofcolumns = {}  # type: Dict[str, List[str]]
    for _, column_purpose, column in stats_and_column_purposes:
        column_purpose_to_setofcolumns.setdefault(column_purpose, []).append(column)

    return column_purpose_to_setofcolumns


def suggest_transformers(column_purpose_to_setofcolumns: Dict[str, List[str]],
                         training_ddf: dask.dataframe) -> List[AzureMLTransformer]:
    all_transformers = []
    if FeatureType.Numeric in column_purpose_to_setofcolumns.keys() or \
            FeatureType.Categorical in column_purpose_to_setofcolumns.keys() or \
            FeatureType.CategoricalHash in column_purpose_to_setofcolumns.keys():

        distributed_operations = []
        categorical_columns = []
        if FeatureType.Categorical in column_purpose_to_setofcolumns.keys():
            categorical_columns += column_purpose_to_setofcolumns[FeatureType.Categorical]
        if FeatureType.CategoricalHash in column_purpose_to_setofcolumns.keys():
            categorical_columns += column_purpose_to_setofcolumns[FeatureType.Hashes]
        if categorical_columns:
            distributed_operations += [training_ddf[col].unique() for col in categorical_columns]

        numerical_columns = []
        if FeatureType.Numeric in column_purpose_to_setofcolumns.keys():
            numerical_columns = column_purpose_to_setofcolumns[FeatureType.Numeric]
            numerical_ddf = training_ddf[numerical_columns]
            distributed_operations.append(numerical_ddf.describe())

        all_statistics = dask.compute(*distributed_operations)  # type: List[Any]
        PhaseUtil.log_with_memory("Finished calculating uniques and described")

        uniques_for_categorical = []  # type: List[Any]
        describes_for_numerical = {}  # type: Dict[str, Any]
        if numerical_columns and categorical_columns:
            uniques_for_categorical = all_statistics[:-1]
            describes_for_numerical = all_statistics[-1]
        elif numerical_columns and not categorical_columns:
            describes_for_numerical = all_statistics[0]
        else:
            uniques_for_categorical = all_statistics

        if numerical_columns:
            all_transformers += [(col, get_numeric_pipeline(describes_for_numerical[col]['mean'],
                                                            describes_for_numerical[col]['std']), [col])
                                 for col in numerical_columns]
        if categorical_columns:
            all_transformers += [(col, get_categorical_pipeline(np.sort(np.asarray(uniques))), [col])
                                 for col, uniques in zip(categorical_columns, uniques_for_categorical)]

    return all_transformers
