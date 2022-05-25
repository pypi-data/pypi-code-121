import math
from argparse import ArgumentParser, Namespace
from logging import Logger


from text_selection.selection import SelectionMode
from text_selection_cli.argparse_helper import (parse_existing_file, parse_positive_float,
                                                parse_positive_integer)
from text_selection_cli.default_args import (add_dataset_argument, add_dry_argument,
                                             add_file_arguments, add_from_and_to_subsets_arguments,
                                             add_mp_group)
from text_selection_cli.globals import ExecutionResult
from text_selection_cli.io_handling import (try_load_data_weights, try_load_dataset, try_load_file,
                                            try_save_dataset)
from text_selection_core.common import SelectionDefaultParameters, WeightSelectionParameters
from text_selection_core.selection.all_selection import select_all
from text_selection_core.selection.fifo_selection import select_fifo
from text_selection_core.selection.greedy_selection import (GreedySelectionParameters,
                                                            select_greedy, select_greedy_epochs)
from text_selection_core.selection.kld_selection import KldSelectionParameters, select_kld
from text_selection_core.validation import ValidationErrBase


def get_select_all_parser(parser: ArgumentParser):
  parser.description = "Select all lines."
  add_dataset_argument(parser)
  add_from_and_to_subsets_arguments(parser)
  add_dry_argument(parser)
  return select_all_nrs_from_ns


def select_all_nrs_from_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  dataset = try_load_dataset(ns.dataset, logger)
  if isinstance(dataset, ValidationErrBase):
    return dataset

  default_params = SelectionDefaultParameters(dataset, ns.from_subsets, ns.to_subset)
  changed_anything = select_all(default_params, flogger)

  if isinstance(changed_anything, ValidationErrBase):
    return changed_anything

  if changed_anything and not ns.dry:
    if error := try_save_dataset(ns.dataset, dataset, logger):
      return error

  return changed_anything


def get_fifo_selection_parser(parser: ArgumentParser):
  parser.description = "Select lines by FIFO principle."
  add_dataset_argument(parser)
  add_from_and_to_subsets_arguments(parser)
  add_termination_criteria_arguments(parser)
  add_dry_argument(parser)
  return select_fifo_from_ns


def select_fifo_from_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  dataset = try_load_dataset(ns.dataset, logger)
  if isinstance(dataset, ValidationErrBase):
    return dataset

  weights = try_load_data_weights(ns.weights, logger)
  if isinstance(weights, ValidationErrBase):
    return weights

  default_params = SelectionDefaultParameters(dataset, ns.from_subsets, ns.to_subset)
  weights_params = WeightSelectionParameters(
    weights, ns.limit, ns.limit_include_already_selected, ns.limit_percent)
  changed_anything = select_fifo(default_params, weights_params, flogger)
  if isinstance(changed_anything, ValidationErrBase):
    return changed_anything

  if changed_anything and not ns.dry:
    if error := try_save_dataset(ns.dataset, dataset, logger):
      return error

  return changed_anything


def add_termination_criteria_arguments(parser: ArgumentParser) -> None:
  group = parser.add_argument_group("termination criteria arguments")
  group.add_argument("weights", type=parse_existing_file, metavar="WEIGHTS-PATH",
                     help="weights path")
  group.add_argument("--limit", type=parse_positive_float, metavar="FLOAT",
                     help="weights limit", default=math.inf)
  group.add_argument("-i", "--limit-include-already-selected", action="store_true",
                     help="include already selected lines for limit")
  group.add_argument("-p", "--limit-percent", action="store_true",
                     help="limit is percentual; in this case it needs to be in interval (0, 100]")


def get_greedy_selection_parser(parser: ArgumentParser):
  parser.description = "Select lines by greedy principle (iteration-wise)."
  add_dataset_argument(parser)
  add_from_and_to_subsets_arguments(parser)
  add_file_arguments(parser, True)
  parser.add_argument("--cover-per-epoch", type=parse_positive_integer,
                      help="cover each unit with this count in each epoch", default=1)
  parser.add_argument("--include-selected", action="store_true",
                      help="consider already selected for the selection")
  add_termination_criteria_arguments(parser)
  add_mp_group(parser)
  add_dry_argument(parser)
  return greedy_selection_ns


def greedy_selection_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  dataset = try_load_dataset(ns.dataset, logger)
  if isinstance(dataset, ValidationErrBase):
    return dataset

  lines = try_load_file(ns.file, ns.encoding, ns.lsep, logger)
  if isinstance(lines, ValidationErrBase):
    return lines

  weights = try_load_data_weights(ns.weights, logger)
  if isinstance(weights, ValidationErrBase):
    return weights

  default_params = SelectionDefaultParameters(dataset, ns.from_subsets, ns.to_subset)
  params = GreedySelectionParameters(
    lines, ns.sep, ns.include_selected, ns.cover_per_epoch, SelectionMode.FIRST)
  weights_params = WeightSelectionParameters(
    weights, ns.limit, ns.limit_include_already_selected, ns.limit_percent)

  changed_anything = select_greedy(
    default_params, params, weights_params, ns.chunksize, ns.n_jobs, ns.maxtasksperchild, flogger)
  if isinstance(changed_anything, ValidationErrBase):
    return changed_anything

  if changed_anything and not ns.dry:
    if error := try_save_dataset(ns.dataset, dataset, logger):
      return error

  return changed_anything


def get_greedy_selection_epoch_parser(parser: ArgumentParser):
  parser.description = "Select lines by greedy principle (epoch-wise)."
  add_dataset_argument(parser)
  add_from_and_to_subsets_arguments(parser)
  add_file_arguments(parser, True)
  parser.add_argument("epochs", type=parse_positive_integer,
                      metavar="N-EPOCHS", help="number of epochs")
  parser.add_argument("--cover-per-epoch", type=parse_positive_integer,
                      help="cover each unit with this count in each epoch", default=1)
  parser.add_argument("--include-selected", action="store_true",
                      help="consider already selected for the selection")
  add_mp_group(parser)
  # add_termination_criteria_arguments(parser)
  add_dry_argument(parser)
  return greedy_selection_epoch_ns


def greedy_selection_epoch_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  dataset = try_load_dataset(ns.dataset, logger)
  if isinstance(dataset, ValidationErrBase):
    return dataset

  lines = try_load_file(ns.file, ns.encoding, ns.lsep, logger)
  if isinstance(lines, ValidationErrBase):
    return lines

  # weights = try_load_data_weights(ns.weights, logger)
  # if weights is None:
  #   return False, False

  default_params = SelectionDefaultParameters(dataset, ns.from_subsets, ns.to_subset)
  params = GreedySelectionParameters(
    lines, ns.sep, ns.include_selected, ns.cover_per_epoch, SelectionMode.FIRST)

  logger.info("Selecting...")
  changed_anything = select_greedy_epochs(
    default_params, params, ns.epochs, ns.chunksize, ns.n_jobs, ns.maxtasksperchild, flogger)
  if isinstance(changed_anything, ValidationErrBase):
    return changed_anything

  if changed_anything and not ns.dry:
    if error := try_save_dataset(ns.dataset, dataset, logger):
      return error

  return changed_anything


def get_kld_selection_parser(parser: ArgumentParser):
  parser.description = "Select lines in the optimal way to obtain an uniform unit distribution."
  add_dataset_argument(parser)
  add_from_and_to_subsets_arguments(parser)
  add_file_arguments(parser, True)
  parser.add_argument("--include-selected", action="store_true",
                      help="consider already selected for the selection")
  add_termination_criteria_arguments(parser)
  add_mp_group(parser)
  add_dry_argument(parser)
  return kld_selection_ns


def kld_selection_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  dataset = try_load_dataset(ns.dataset, logger)
  if isinstance(dataset, ValidationErrBase):
    return dataset

  lines = try_load_file(ns.file, ns.encoding, ns.lsep, logger)
  if isinstance(lines, ValidationErrBase):
    return lines

  weights = try_load_data_weights(ns.weights, logger)
  if isinstance(weights, ValidationErrBase):
    return weights

  default_params = SelectionDefaultParameters(dataset, ns.from_subsets, ns.to_subset)
  params = KldSelectionParameters(lines, ns.sep, ns.include_selected, SelectionMode.FIRST)
  weights_params = WeightSelectionParameters(
    weights, ns.limit, ns.limit_include_already_selected, ns.limit_percent)

  changed_anything = select_kld(
    default_params, params, weights_params, ns.chunksize, ns.n_jobs, ns.maxtasksperchild, flogger)
  if isinstance(changed_anything, ValidationErrBase):
    return changed_anything

  if changed_anything and not ns.dry:
    if error := try_save_dataset(ns.dataset, dataset, logger):
      return error

  return changed_anything
