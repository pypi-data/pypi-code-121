"""CLI interface for the data format checker."""
from argparse import ArgumentParser
from pathlib import Path
from typing import Union

from rime_sdk.data_format_check.nlp_checker import NLP_TASKS, NlpDataFormatChecker
from rime_sdk.data_format_check.tabular_checker import (
    TABULAR_TASKS,
    TabularDataFormatChecker,
)


def pprint_exception(e: Exception) -> None:
    """Neatly prints out contents of exception."""
    args_joined = "".join([str(i) for i in e.args])
    print(f"\n---\n\nError:\n\n{args_joined}\n")


def main() -> None:
    """Parse CLI inputs and executes appropriate methods."""
    parser = ArgumentParser()

    # Data type
    group_types = parser.add_mutually_exclusive_group(required=True)
    group_types.add_argument(
        "-nlp", action="store_true", help="Whether this data is for NLP tasks"
    )
    group_types.add_argument(
        "-tabular", action="store_true", help="Whether this data is tabular"
    )

    # Shared args
    parser.add_argument(
        "--ref-path", type=Path, required=True, help="Path to reference data file."
    )
    parser.add_argument(
        "--eval-path", type=Path, required=True, help="Path to evaluation data file."
    )
    parser.add_argument(
        "--task",
        choices=list(TABULAR_TASKS) + list(NLP_TASKS),
        required=True,
        help="The desired ML task.",
    )

    # NLP args
    parser.add_argument(
        "--preds-ref-path",
        type=Path,
        required=False,
        help="(Optional) The path to the reference predictions, if they are stored"
        " in a separate file.",
    )
    parser.add_argument(
        "--preds-eval-path",
        type=Path,
        required=False,
        help="(Optional) The path to the evaluation predictions, if they are stored"
        " in a separate file.",
    )

    # Tabular args
    parser.add_argument(
        "--label-col-name",
        type=str,
        required=False,
        default=None,
        help="Name of column in inputs that contains labels.",
    )
    parser.add_argument(
        "--pred-col-name",
        type=str,
        required=False,
        default=None,
        help="Name of column in inputs that contains predictions.",
    )
    parser.add_argument(
        "--timestamp-col-name",
        type=str,
        required=False,
        default=None,
        help="Name of column in inputs that contains timestamps. "
        "Only applicable if using RIME Continuous Testing.",
    )

    argps = parser.parse_args()

    if argps.nlp:
        checker: Union[
            TabularDataFormatChecker, NlpDataFormatChecker
        ] = NlpDataFormatChecker()
        try:
            checker.check(
                argps.ref_path,
                argps.eval_path,
                argps.task,
                preds_ref_path=argps.preds_ref_path,
                preds_eval_path=argps.preds_eval_path,
            )
        except Exception as e:  # pylint: disable=broad-except
            pprint_exception(e)
    elif argps.tabular:
        checker = TabularDataFormatChecker()
        try:
            checker.check(
                argps.ref_path,
                argps.eval_path,
                argps.task,
                label_col_name=argps.label_col_name,
                pred_col_name=argps.pred_col_name,
                timestamp_col_name=argps.timestamp_col_name,
            )
        except Exception as e:  # pylint: disable=broad-except
            pprint_exception(e)
