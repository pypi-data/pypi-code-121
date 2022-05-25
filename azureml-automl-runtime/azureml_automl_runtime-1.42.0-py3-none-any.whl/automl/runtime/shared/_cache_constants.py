# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Constants for automl cache store."""


class Keys:
    FEATURIZATION_DATA_NAMESPACE = "featurization/data/"
    DEFAULT_NAMESPACE = "_automl_internal/"
    INDICES_DIR = "indices"
    X_TRAIN = "X"
    Y_TRAIN = "y"
    SW_TRAIN = "sample_weight"

    X_VALID = "X_valid"
    Y_VALID = "y_valid"
    SW_VALID = "sample_weight_valid"

    X_RAW = "X_raw"
    Y_RAW = "y_raw"

    X_RAW_VALID = "X_raw_valid"
    Y_RAW_VALID = "y_raw_valid"

    X_TEST = "X_test"
    Y_TEST = "y_test"
    SW_TEST = "sample_weight_test"

    SPLIT_KEYS = "split_keys"

    FULL_TRAIN = "full_training_dataset"
    FULL_TEST = "full_test_dataset"
    FULL_VALIDATION = "full_validation_dataset"

    EXPERIMENT_DATA_PARTITIONED = "ExperimentData_partitioned"
    EXPERIMENT_DATA_LAZY = "ExperimentData_lazy"
    EXPERIMENT_DATA_MATERIALIZED = "ExperimentData_materialized"

    # Unique column id to avoid with possible conflicts.
    Y_COLUMN = "automl_y"
    SW_COLUMN = "automl_weights"

    # Data Transformers
    EXP_TRANSFORMERS_CACHE_DIR = "featurization/pipeline"
    EXP_TRANSFORMERS = EXP_TRANSFORMERS_CACHE_DIR + "/ExperimentTransformers"
