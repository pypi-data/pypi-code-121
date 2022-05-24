"""NLP-specific data format checking class and artifacts."""
import gzip
import json
from pathlib import Path
from typing import IO, Any, Iterable, List, Optional

from schema import Schema, SchemaError
from tqdm import tqdm

from rime_sdk.data_format_check.data_format_checker import DataFormatChecker

# NLP Tasks
TEXT_CLASSIFICATION = "Text Classification"
NAMED_ENTITY_RECOGNITION = "Named Entity Recognition"
NLP_TASKS = {TEXT_CLASSIFICATION, NAMED_ENTITY_RECOGNITION}

# NLP JSON data schemas
# Text Classification
TC_SCHEMA_DEFAULT = Schema({"text": str}, ignore_extra_keys=True)
TC_SCHEMA_PREDS = Schema({"probabilities": [float]}, ignore_extra_keys=True)
TC_SCHEMA_MASTER = Schema(
    {"text": str, "label": int, "probabilities": [float]}, ignore_extra_keys=True
)
# Named Entity Recognition Schemas
NER_SCHEMA_DEFAULT = Schema({"text": str}, ignore_extra_keys=True)
# NER has dicts, which need their own schemas
NER_SCHEMA_MENTION = Schema(
    {"start_offset": int, "end_offset": int}, ignore_extra_keys=True
)
NER_SCHEMA_ENTITY = Schema(
    {"mentions": [NER_SCHEMA_MENTION], "type": str}, ignore_extra_keys=True
)
NER_SCHEMA_PREDS = Schema(
    {"predicted_entities": [NER_SCHEMA_ENTITY]}, ignore_extra_keys=True
)
NER_SCHEMA_MASTER = Schema(
    {
        "text": str,
        "entities": [NER_SCHEMA_ENTITY],
        "predicted_entities": [NER_SCHEMA_ENTITY],
    },
    ignore_extra_keys=True,
)

DEFAULT = "default"
PREDS = "preds"
MASTER = "master"
SCHEMA_BANK = {
    TEXT_CLASSIFICATION: {
        DEFAULT: TC_SCHEMA_DEFAULT,
        PREDS: TC_SCHEMA_PREDS,
        MASTER: TC_SCHEMA_MASTER,
    },
    NAMED_ENTITY_RECOGNITION: {
        DEFAULT: NER_SCHEMA_DEFAULT,
        PREDS: NER_SCHEMA_PREDS,
        MASTER: NER_SCHEMA_MASTER,
    },
}

# Validations can happen on these types of input
INPUT_PREDS_INCLUDED = "input_preds_included"
INPUT_PREDS_SEPARATE = "input_preds_separate"
PREDS = "preds"
INPUT_TYPES = set([INPUT_PREDS_INCLUDED, INPUT_PREDS_SEPARATE, PREDS])

ERROR_UNKNOWN_TASK = "Unrecognized NLP task: '{task}'. Task must be one of {tasks}"
ERROR_UNKNOWN_INPUT = (
    "Unrecognized input type: '{input_type}'. Input type must be one of {accepted}"
)

# NLP Data loading methods
def _load_data_from_file_object(file_object: IO, file_name: str) -> Iterable[dict]:
    path = Path(file_name)
    try:
        if path.suffix == ".json":
            yield from json.load(file_object)
        elif path.suffix == ".jsonl":
            for line in file_object:
                yield json.loads(line)
        else:
            raise ValueError(
                f"Only .json and .jsonl files supported. Got {path.suffix}"
            )
    finally:
        if not file_object.closed:
            file_object.close()


def _load_data_multi_ext(base_path: Path) -> Iterable[dict]:
    _gz_suffix = ".gz"
    if base_path.suffix == _gz_suffix:
        decompressed_name = str(base_path)[: -len(_gz_suffix)]
        file_object = gzip.open(str(base_path), "rt", encoding="utf-8")
        return _load_data_from_file_object(file_object, decompressed_name)
    else:
        file_object = base_path.open("r", encoding="utf-8")
        return _load_data_from_file_object(file_object, str(base_path))


def _load_data(data_path: Path) -> List[dict]:
    data = list(_load_data_multi_ext(data_path))
    return data


def check_json_nlp_data(
    file_path: Path, schema: Schema = None, task: str = "", input_type: str = None
) -> None:
    """Validate that all objects in the loaded JSON data match the given Schema.

    If no schema is provided, it will be inferred based on the task, first data point,
    and input_type.
    """

    if schema is None and (task is None or input_type is None):
        raise ValueError(
            "If schema is not provided, both task and input_type "
            "must be provided to enable schema inference."
        )
    elif schema is None and (task is not None and input_type is not None):
        if task not in NLP_TASKS:
            raise ValueError(ERROR_UNKNOWN_TASK.format(task=task, tasks=NLP_TASKS))
        if input_type not in INPUT_TYPES:
            raise ValueError(
                ERROR_UNKNOWN_INPUT.format(input_type=input_type, accepted=INPUT_TYPES)
            )

    list_data = _load_data(file_path)

    if list_data is None or len(list_data) == 0:
        raise ValueError(
            f"No objects parsed from '{file_path}'. Please verify "
            "presence and format of input data and retry."
        )

    # If schema is not provided, select or generate an appropriate one based
    # on first data point and task/presence of predictions
    if schema is None:
        if input_type == PREDS:
            schema = SCHEMA_BANK[task][PREDS]
        elif input_type == INPUT_PREDS_SEPARATE:
            schema = infer_schema_from_datapoint(
                task, list_data[0], set(SCHEMA_BANK[task][PREDS].schema.keys())
            )
        elif input_type == INPUT_PREDS_INCLUDED:
            schema = infer_schema_from_datapoint(task, list_data[0])
        else:
            raise ValueError(
                ERROR_UNKNOWN_INPUT.format(input_type=input_type, accepted=INPUT_TYPES)
            )

    print(f"\nInspecting '{file_path}':")
    for i in tqdm(range(0, len(list_data))):
        try:
            # TODO add manual non-null/non-empty check?
            schema.validate(list_data[i])
        except SchemaError as e:
            schema_str_trimmed = str(schema).replace("Schema(", "").replace(")", "")
            schema_msg = (
                f"\n\n---\n\nInputs for task '{task}' must adhere to the "
                f"following structure:\n\n{schema_str_trimmed}"
            )
            e.args = (
                f"File '{file_path}', Index {i}:\n\n",
                *e.args,
                schema_msg,
            )
            raise


def infer_schema_from_datapoint(
    task: str, datapoint: dict, excluded_keys: Optional[Iterable] = None
) -> Schema:
    """Generate a custom schema using the given task and datapoint.

    Start with the default schema (contains only required keys), and add keys as they
    are observed in the datapoint.

    Use only those keys that are present in the "master schema", unless they've been
    explicitly excluded via excluded_keys.
    """
    generated_schema = Schema(
        schema=SCHEMA_BANK[task][DEFAULT].schema.copy(),
        ignore_extra_keys=SCHEMA_BANK[task][DEFAULT].ignore_extra_keys,
    )
    master_schema = SCHEMA_BANK[task][MASTER]

    datapoint_keys = list(datapoint.keys())
    master_schema_keys = set(master_schema.schema.keys())

    for key in datapoint_keys:
        if excluded_keys is not None:
            if key in master_schema_keys and key not in excluded_keys:
                generated_schema.schema.update({key: master_schema.schema.get(key)})
        elif key in master_schema_keys:
            generated_schema.schema.update({key: master_schema.schema.get(key)})

    return generated_schema


class NlpDataFormatChecker(DataFormatChecker):
    """Checker for NLP tasks."""

    accepted_file_types = [".json", ".jsonl", ".json.gz", ".jsonl.gz"]

    def check(
        self,
        ref_path: Path,
        eval_path: Path,
        task: str = "",
        preds_ref_path: Path = None,
        preds_eval_path: Path = None,
        **kwargs: Any,
    ) -> None:
        """Execute NLP data checks based on provided inputs.

        Uses rules defined in the global NLP data schemas.
        """

        self.check_file_format(ref_path)
        self.check_file_format(eval_path)

        # Assume predictions are included unless observed otherwise
        ref_input_type = INPUT_PREDS_INCLUDED
        if preds_ref_path is not None:
            self.check_file_format(preds_ref_path)
            check_json_nlp_data(preds_ref_path, None, task, PREDS)
            ref_input_type = INPUT_PREDS_SEPARATE

        eval_input_type = INPUT_PREDS_INCLUDED
        if preds_eval_path is not None:
            self.check_file_format(preds_eval_path)
            check_json_nlp_data(preds_eval_path, None, task, PREDS)
            eval_input_type = INPUT_PREDS_SEPARATE

        check_json_nlp_data(ref_path, None, task, ref_input_type)

        check_json_nlp_data(eval_path, None, task, eval_input_type)

        print("\n---\n")
        print(self.success_msg)
