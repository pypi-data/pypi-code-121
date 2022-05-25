from argparse import ArgumentParser, Namespace
from logging import Logger

from text_selection_cli.argparse_helper import (parse_existing_file, parse_path,
                                                parse_positive_float, parse_positive_integer)
from text_selection_cli.default_args import add_dataset_argument, add_file_arguments
from text_selection_cli.io_handling import (try_load_data_weights, try_load_dataset, try_load_file,
                                            try_save_data_weights)
from text_selection_core.globals import ExecutionResult
from text_selection_core.validation import ValidationErrBase
from text_selection_core.weights.calculation import (divide_weights, get_count_weights,
                                                     get_uniform_weights)


def get_uniform_weights_creation_parser(parser: ArgumentParser):
  parser.description = "Creates uniform weights (i.e., each line get the same weight)."
  add_dataset_argument(parser)
  parser.add_argument("--val", type=parse_positive_integer, help="uniform value", default=1)
  parser.add_argument("output", type=parse_path, metavar="OUTPUT-PATH",
                      help="output path to save the weights")
  return create_uniform_weights_ns


def create_uniform_weights_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  dataset = try_load_dataset(ns.dataset, logger)
  if isinstance(dataset, ValidationErrBase):
    return dataset

  logger.info("Creating weights...")
  weights = get_uniform_weights(dataset.get_line_nrs(), ns.val, flogger)

  if error := try_save_data_weights(ns.output, weights, logger):
    return error

  return None


def get_word_count_weights_creation_parser(parser: ArgumentParser):
  parser.description = "Create weights containing the amount of unit per line."
  add_dataset_argument(parser)
  add_file_arguments(parser, True)
  parser.add_argument("output", type=parse_path, metavar="OUTPUT-PATH",
                      help="output path to save the weights (.npy)")
  return create_word_count_weights_ns


def create_word_count_weights_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  lines = try_load_file(ns.file, ns.encoding, ns.lsep, logger)
  if isinstance(lines, ValidationErrBase):
    return lines

  logger.info("Calculating weights...")
  weights = get_count_weights(lines, ns.sep, flogger)

  if error := try_save_data_weights(ns.output, weights, logger):
    return error

  return None


def get_weights_division_parser(parser: ArgumentParser):
  # TODO could be nargs
  parser.description = "Divide existing weights."
  add_dataset_argument(parser)
  parser.add_argument("weights", type=parse_existing_file, metavar="WEIGHTS-PATH",
                      help="path to the weights")
  parser.add_argument("divisor", type=parse_positive_float, metavar="DIVISOR",
                      help="divisor")
  return create_weights_division_ns


def create_weights_division_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  weights = try_load_data_weights(ns.weights, logger)
  if isinstance(weights, ValidationErrBase):
    return weights

  logger.info("Dividing weights...")
  weights = divide_weights(weights, ns.divisor, flogger)

  if error := try_save_data_weights(ns.weights, weights, logger):
    return error

  return None
