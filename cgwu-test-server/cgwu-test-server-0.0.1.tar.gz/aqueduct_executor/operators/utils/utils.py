import io
import json
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from aqueduct_executor.operators.utils.enums import InputArtifactType, OutputArtifactType
from aqueduct_executor.operators.utils.storages.storage import Storage

_DEFAULT_ENCODING = "utf8"


# Typing: all the possible artifact types to a function. Should be in sync with `InputArtifactType`.
InputArtifact = Union[pd.DataFrame, float]


def read_artifacts(
    storage: Storage,
    input_paths: List[str],
    input_metadata_paths: List[str],
    artifact_types: List[InputArtifactType],
) -> List[InputArtifact]:
    if len(input_paths) != len(artifact_types):
        raise Exception(
            "Found inconsistent number of input paths (%d) and artifact types (%d)"
            % (
                len(input_paths),
                len(artifact_types),
            )
        )

    inputs: List[InputArtifact] = []
    for (input_path, artifact_type) in zip(input_paths, artifact_types):
        if artifact_type == InputArtifactType.TABLE:
            inputs.append(_read_tabular_input(storage, input_path))
        elif artifact_type == InputArtifactType.FLOAT:
            inputs.append(_read_float_input(storage, input_path))
        else:
            raise Exception("Unexpected input artifact type %s", artifact_type)
    return inputs


# TODO: Can also the input metadata here if we wanted to use it.
def _read_tabular_input(storage: Storage, path: str) -> pd.DataFrame:
    input_bytes = storage.get(path)
    return pd.read_json(io.BytesIO(input_bytes), orient="table")


def _read_float_input(storage: Storage, path: str) -> float:
    input_bytes = storage.get(path)
    return float(input_bytes)


def write_artifacts(
    storage: Storage,
    output_paths: List[str],
    output_metadata_paths: List[str],
    contents: List[Any],
    artifact_types: List[OutputArtifactType],
) -> None:
    if (
        len(contents) != len(output_paths)
        or len(contents) != len(output_metadata_paths)
        or len(contents) != len(artifact_types)
    ):
        raise Exception(
            "Found inconsistent number of outputs (%d), artifact_types (%d), output paths (%d), and output metadata paths (%d)."
            % (
                len(contents),
                len(artifact_types),
                len(output_paths),
                len(output_metadata_paths),
            )
        )

    for (artifact_type, output_path, output_metadata_path, content) in zip(
        artifact_types, output_paths, output_metadata_paths, contents
    ):
        _write_artifact(storage, content, artifact_type, output_path, output_metadata_path)


def _write_artifact(
    storage: Storage,
    content: Any,
    artifact_type: OutputArtifactType,
    output_path: str,
    output_metadata_path: str,
) -> None:
    if artifact_type == OutputArtifactType.TABLE:
        if not isinstance(content, pd.DataFrame):
            raise Exception(
                "Expected output type to be Pandas Dataframe, but instead got %s"
                % type(content).__name__
            )
        _write_tabular_output(storage, output_path, output_metadata_path, content)
    elif artifact_type == OutputArtifactType.FLOAT:
        if not isinstance(content, float):
            raise Exception(
                "Expected output type to be float, instead got %s" % type(content).__name__
            )
        _write_float_output(storage, output_path, output_metadata_path, content)
    elif artifact_type == OutputArtifactType.BOOL:
        if isinstance(content, bool) or isinstance(content, np.bool_):
            _write_bool_output(storage, output_path, output_metadata_path, bool(content))
        elif isinstance(content, pd.Series) and content.dtype == "bool":
            # We only write True if every boolean in the series is True.
            series = pd.Series(content)
            all_true = series.size - series.sum().item() == 0
            _write_bool_output(storage, output_path, output_metadata_path, all_true)
        else:
            raise Exception(
                "Expected output type to either a bool or a series of booleans, "
                "instead got %s" % type(content).__name__
            )
    else:
        raise Exception("Unsupported output artifact type %s" % artifact_type)


def _write_tabular_output(
    storage: Storage,
    output_path: str,
    output_metadata_path: str,
    df: pd.DataFrame,
) -> None:
    output_str = df.to_json(orient="table", date_format="iso", index=False)

    # Create tabular output metadata
    schema = [{col: str(df[col].dtype)} for col in df]
    output_metadata_str = json.dumps(schema)

    storage.put(output_path, bytes(output_str, encoding=_DEFAULT_ENCODING))
    storage.put(output_metadata_path, bytes(output_metadata_str, encoding=_DEFAULT_ENCODING))


def _write_float_output(
    storage: Storage,
    output_path: str,
    output_metadata_path: str,
    val: float,
) -> None:
    """Used for metrics."""
    storage.put(output_path, bytes(str(val), encoding=_DEFAULT_ENCODING))
    storage.put(output_metadata_path, bytes(json.dumps([]), encoding=_DEFAULT_ENCODING))


def _write_bool_output(
    storage: Storage,
    output_path: str,
    output_metadata_path: str,
    val: bool,
) -> None:
    """Used for checks."""
    storage.put(output_path, bytes(str(val), encoding=_DEFAULT_ENCODING))
    storage.put(output_metadata_path, bytes(json.dumps([]), encoding=_DEFAULT_ENCODING))


def write_operator_metadata(
    storage: Storage,
    metadata_path: str,
    err: str,
    logs: Dict[str, str],
) -> None:
    """
    Writes operator execution metadata to storage.
    :param err: Any error message encountered during execution.
    :param logs: Any logs generated by this operator.
    """
    metadata: Dict[str, Any] = {"error": err, "logs": logs}
    storage.put(metadata_path, bytes(json.dumps(metadata), encoding=_DEFAULT_ENCODING))


def write_discover_results(storage: Storage, path: str, tables: List[str]):
    table_names_str = json.dumps(tables)

    storage.put(path, bytes(table_names_str, encoding=_DEFAULT_ENCODING))
