from argparse import ArgumentParser, Namespace
from logging import Logger

from text_selection_cli.argparse_helper import parse_non_empty_or_whitespace, parse_path
from text_selection_cli.default_args import add_file_arguments
from text_selection_cli.globals import ExecutionResult
from text_selection_cli.io_handling import try_load_file, try_save_dataset
from text_selection_core.types import Dataset
from text_selection_core.validation import ValidationErrBase


def get_init_parser(parser: ArgumentParser):
  parser.description = "This command reads the lines of a text file and initializes a dataset from it."
  add_file_arguments(parser)
  parser.add_argument("name", type=parse_non_empty_or_whitespace, metavar="SUBSET",
                      help="name of the initial subset containing all line numbers")
  parser.add_argument("dataset", type=parse_path, metavar="DATASET-PATH",
                      help="output dataset file")
  return create_dataset_from_text_ns


def create_dataset_from_text_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  # TODO maybe just count ns.lsep occurrences + 1
  lines = try_load_file(ns.file, ns.encoding, ns.lsep, logger)
  if isinstance(lines, ValidationErrBase):
    return lines

  if len(lines) == 0:
    logger.error("File has no content!")
    return None

  logger.info("Creating dataset...")
  dataset = Dataset(len(lines), ns.name)

  if error := try_save_dataset(ns.dataset, dataset, logger):
    return error

  return None
