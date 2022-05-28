import logging
import os
import typing

import pandas as pd

from mlfoundry.enums import FileFormat
from mlfoundry.exceptions import MlFoundryException

logger = logging.getLogger(__name__)


def save_dataframe(
    local_dir: str,
    entity_name: str,
    dataframe: pd.DataFrame,
) -> typing.Tuple[str, FileFormat]:
    file_format = FileFormat.PARQUET
    file_name = f"{entity_name}.{file_format.value}"
    file_path = os.path.join(local_dir, file_name)
    try:
        dataframe.to_parquet(file_path, index=False)
        return file_name, file_format
    except Exception as ex:
        logger.info(
            f"failed to log {entity_name} as {FileFormat.PARQUET} "
            f"due to {ex}, trying with {FileFormat.CSV}"
        )

    file_format = FileFormat.CSV
    file_name = f"{entity_name}.{file_format.value}"
    file_path = os.path.join(local_dir, file_name)
    dataframe.to_csv(file_path, index=False)

    return file_name, file_format


def load_dataframe(local_file_path: str) -> pd.DataFrame:
    _, file_ext = os.path.splitext(local_file_path)
    if len(file_ext) <= 1:
        raise MlFoundryException(
            f"cannot recognize file format, '{file_ext}' is not valid"
        )
    # ".csv" -> "csv"
    file_ext = file_ext[1:]
    file_format = FileFormat(file_ext)

    if file_format is FileFormat.CSV:
        return pd.read_csv(local_file_path)
    elif file_format is FileFormat.PARQUET:
        return pd.read_parquet(local_file_path)
    else:
        raise MlFoundryException(
            f"cannot load dataframe from {file_format} file format"
        )


def save_series(
    local_dir: str,
    entity_name: str,
    series: pd.Series,
) -> typing.Tuple[str, FileFormat]:
    dataframe = series.to_frame(name=series.name or entity_name)
    return save_dataframe(
        local_dir=local_dir,
        entity_name=entity_name,
        dataframe=dataframe,
    )


def load_series(local_file_path: str) -> pd.Series:
    dataframe = load_dataframe(local_file_path)
    return dataframe.iloc[:, 0]
