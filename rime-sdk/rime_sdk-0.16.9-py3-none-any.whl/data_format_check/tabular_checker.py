"""Tabular-specific data format checking class and artifacts."""
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from rime_sdk.data_format_check.data_format_checker import DataFormatChecker

# Tabular Tasks
# TODO add Ranking
BINARY_CLASSIFICATION = "Binary Classification"
REGRESSION = "Regression"
MULTI_CLASS_CLASSIFICATION = "Multi-class Classification"
TABULAR_TASKS = {BINARY_CLASSIFICATION, REGRESSION, MULTI_CLASS_CLASSIFICATION}

# Accepted formats for the "timestamp" column
FORMAT_SECONDS = "%Y-%m-%d %H:%M:%S"
FORMAT_DAYS = "%Y-%m-%d"

WARNING_NO_PRED_COL = (
    "WARNING: No prediction column is provided. Although you can still run RIME "
    "without predictions, it will not be as powerful as if you run it WITH "
    "predictions.\n"
)
WARNING_NO_LABEL_COL = (
    "WARNING: No label column is provided. Although you can still run RIME without "
    "labels, it will not be as powerful as if you run it WITH labels.\n"
)
ERROR_UNKNOWN_TASK = "Unrecognized Tabular task: '{task}'. Task must be one of {tasks}"


class TabularDataFormatChecker(DataFormatChecker):
    """Checker for ML tasks involving Tabular data."""

    accepted_file_types = [".csv", ".parquet"]

    def check(
        self,
        ref_path: Path,
        eval_path: Path,
        task: str,
        label_col_name: Optional[str] = None,
        pred_col_name: Optional[str] = None,
        timestamp_col_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Run all data checks."""

        self.check_file_format(ref_path)
        self.check_file_format(eval_path)

        for file_path in [ref_path, eval_path]:
            print(f"\nInspecting '{file_path}'")
            self.check_data_file(file_path, task, label_col_name, pred_col_name)
            print("Done!")

        print("")
        if pred_col_name is None:
            print(WARNING_NO_PRED_COL)
        if label_col_name is None:
            print(WARNING_NO_LABEL_COL)

        if timestamp_col_name is not None:
            print(
                f"Timestamp column provided: '{timestamp_col_name}'. Inspecting both "
                f"datasets for format of timestamps ('{FORMAT_SECONDS}' or "
                f"'{FORMAT_DAYS}')"
            )

        print("\n---\n")
        print(self.success_msg)

    def check_data_file(
        self,
        filename: Path,
        task: str,
        label_col_name: Optional[str],
        pred_col_name: Optional[str],
        timestamp_col_name: Optional[str] = None,
    ) -> None:
        """Perform multiple checks against the given file."""
        if not filename.exists():
            raise ValueError(f"File {filename} does not exist")

        # TODO decide if this should be wrapped and re-thrown, for clarity?
        if filename.suffix == ".csv":
            df = pd.read_csv(filename)
        elif filename.suffix == ".parquet":
            df = pd.read_parquet(filename)
        else:
            raise ValueError(
                f"Invalid file type '{filename.suffix}'. File must be one of "
                f"{self.accepted_file_types}"
            )

        if label_col_name is not None:
            if label_col_name not in df:
                raise ValueError(
                    f"Label column ({label_col_name}) not found in data "
                    f"({filename}). If a label column exists in one "
                    "dataset, it MUST exist in the other."
                )
            else:
                self.check_labels(df[label_col_name], task)

        if pred_col_name is not None:
            if pred_col_name not in df:
                raise ValueError(
                    f"Prediction column ({pred_col_name}) not found in data "
                    f"({filename}). If a prediction column exists in one dataset, "
                    f"it MUST exist in the other."
                )
            else:
                self.check_predictions(df[pred_col_name], task)

        if timestamp_col_name is not None:
            self.check_timestamps(df[timestamp_col_name], timestamp_col_name)

    def check_labels(self, ser: pd.Series, task: str) -> None:
        """Perform checks for the label data, based on the model type."""
        if ser.isnull().any():
            raise ValueError(
                "Found nulls in label series, there should not be any nulls."
            )
        if task == REGRESSION:
            if ser.dtype == object:
                raise ValueError("Labels for regression should be numeric.")
        elif task == BINARY_CLASSIFICATION:
            if not ((ser == 1) | (ser == 0)).all():
                raise ValueError(
                    "Labels for Binary Classification should be numeric, all 0s or 1s."
                )
        elif task == MULTI_CLASS_CLASSIFICATION:
            if not (ser == ser.astype(int)).all():
                raise ValueError(
                    "Labels for Multi-class Classification should be all integer "
                    "values."
                )
        else:
            raise ValueError(ERROR_UNKNOWN_TASK.format(task=task, tasks=TABULAR_TASKS))

    def check_predictions(self, ser: pd.Series, task: str) -> None:
        """Perform checks for the prediction data, based on the model type."""
        if ser.isnull().any():
            raise ValueError(
                "Found nulls in prediction series, there should not be any nulls."
            )
        if task == REGRESSION:
            if ser.dtype == object:
                raise ValueError("Predictions for regression should be numeric.")
        elif task == BINARY_CLASSIFICATION:
            if not ((ser <= 1) & (ser >= 0)).all():
                raise ValueError(
                    "Predictions for Binary Classification should be probabilities "
                    "between 0 and 1."
                )
        elif task == MULTI_CLASS_CLASSIFICATION:
            raise ValueError(
                "Prediction column for Multi-class Classification is not supported in"
                " usual way, please contact Robust Intelligence for instructions."
            )
        else:
            raise ValueError(ERROR_UNKNOWN_TASK.format(task=task, tasks=TABULAR_TASKS))

    def check_timestamps(
        self, timestamps: pd.Series, timestamp_col_name: Optional[str] = None
    ) -> None:
        """Validate format of timestamps."""
        try:
            timestamps = timestamps.astype(str)
            # Note: providing a subset of values (e.g. just year and month) is valid
            timestamps = pd.to_datetime(timestamps, format=FORMAT_SECONDS)
        except ValueError as e:
            # pd.to_datetime doesn't throw specific error type for this case,
            # must parse manually
            if "doesn't match format" in str(e):
                try:
                    timestamps = pd.to_datetime(timestamps, format=FORMAT_DAYS)
                except ValueError as new_error:
                    raise ValueError(
                        f"{timestamp_col_name} contains invalid formats."
                        f" Acceptable timestamp formats are {FORMAT_DAYS}"
                        f" and {FORMAT_SECONDS}.\n\n{new_error}"
                    )
            else:
                raise e

        if pd.isnull(timestamps).any():
            null_pos = np.where(pd.isnull(timestamps))[0]
            null_idxs = timestamps.index[null_pos].tolist()
            raise ValueError(
                f"{timestamp_col_name} must not contain nulls."
                f" Found null values at indexes: {null_idxs}"
            )

        if timestamps.nunique() < len(timestamps):
            print(f"WARNING: {timestamp_col_name} contains duplicate values!")
