from argparse import ArgumentParser, Namespace
from logging import Logger

from text_selection_cli.argparse_helper import (ConvertToOrderedSetAction,
                                                parse_non_empty_or_whitespace, parse_path)
from text_selection_cli.default_args import add_dataset_argument, add_file_arguments
from text_selection_cli.globals import ExecutionResult
from text_selection_cli.io_handling import try_load_dataset, try_load_file, try_save_text
from text_selection_core.exporting.symbols_exporting import export_subset
from text_selection_core.validation import ValidationErrBase


def get_export_txt_parser(parser: ArgumentParser):
  parser.description = "This command exports a subset of the file."
  add_dataset_argument(parser)
  parser.add_argument("subsets", type=parse_non_empty_or_whitespace, metavar="SUBSET", nargs="+",
                      help="subsets which should be exported", action=ConvertToOrderedSetAction)
  add_file_arguments(parser)
  parser.add_argument("path", type=parse_path, metavar="OUTPUT-PATH",
                      help="path to the exported text-file")
  return export_txt_ns


def export_txt_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  dataset = try_load_dataset(ns.dataset, logger)
  if isinstance(dataset, ValidationErrBase):
    return dataset

  lines = try_load_file(ns.file, ns.encoding, ns.lsep, logger)
  if isinstance(lines, ValidationErrBase):
    return lines

  logger.debug("Exporting...")
  text = export_subset(dataset, ns.subsets, lines, ns.lsep, flogger)
  if isinstance(text, ValidationErrBase):
    return text

  #logger.debug(f"Export line count: {text.count(ns.lsep) + 1}")
  if error := try_save_text(ns.path, text, ns.encoding, logger):
    return error

  return None
