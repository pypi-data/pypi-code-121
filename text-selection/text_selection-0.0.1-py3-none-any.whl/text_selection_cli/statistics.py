from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path
from typing import cast

import pandas as pd
from ordered_set import OrderedSet

from text_selection_cli.argparse_helper import (ConvertToOrderedSetAction, parse_existing_file,
                                                parse_path)
from text_selection_cli.default_args import add_dataset_argument, add_file_arguments
from text_selection_cli.io_handling import try_load_data_weights, try_load_dataset, try_load_file
from text_selection_core.globals import ExecutionResult
from text_selection_core.statistics import generate_statistics
from text_selection_core.validation import ValidationErrBase

# GERMAN_MESSAGE_PATTERNS = {
#   ErrorType.LINES_MISMATCH:
#     "Zeilenanzahl stimmt nicht überein ({0} vs. {1})!",
#   ErrorType.WEIGHTS_LINES_MISMATCH:
#     "Zeilenanzahl stimmt nicht überein (Gewichte) ({0} vs. {1})!"
# }


def get_statistics_generation_parser(parser: ArgumentParser):
  parser.description = "Creates statistics (CSV file)."
  add_dataset_argument(parser)
  parser.add_argument("path", type=parse_path, metavar="OUTPUT-PATH",
                      help="statistics output path (.csv)")
  parser.add_argument("--weights", type=parse_existing_file, nargs="*", metavar="PATH",
                      help="path to weights", default=OrderedSet(), action=ConvertToOrderedSetAction)
  add_file_arguments(parser, True)
  return statistics_generation_ns


def statistics_generation_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
  dataset = try_load_dataset(ns.dataset, logger)
  if isinstance(dataset, ValidationErrBase):
    return dataset

  weights = []
  for weights_path in cast(OrderedSet[Path], ns.weights):
    current_weights = try_load_data_weights(weights_path, logger)
    if isinstance(current_weights, ValidationErrBase):
      return weights

    weights.append((weights_path.stem, current_weights))

  lines = try_load_file(ns.file, ns.encoding, ns.lsep, logger)
  if isinstance(lines, ValidationErrBase):
    return lines

  logger.debug("Generating statistics...")
  # try:
  dfs = generate_statistics(dataset, lines, ns.sep, weights, flogger)
  # except ValidationException as ex:
  #   #logger.error(f"Validation error: {ex.message}", exc_info=ex)
  #   #msg = str.format(GERMAN_MESSAGE_PATTERNS[ex.error_type], *ex.msg_args)
  #   logger.error(f"Validation error: {ex.default_message}")
  #   return False, False

  stats_path = cast(Path, ns.path)
  header_indicator = "###"
  with open(stats_path, mode="w", encoding="UTF-8") as f:
    f.write(f"{header_indicator} Statistics {header_indicator}\n\n")

  for stat_result in dfs:
    df_name, df = stat_result
    if isinstance(df, ValidationErrBase):
      return df
    logger.debug(f"Saving {df_name}...")

    with open(stats_path, mode="a", encoding="UTF-8") as f:
      header = f"{header_indicator} {df_name} {header_indicator}"
      f.write(f"{header}\n\n")
      df.to_csv(f, sep=";", index=False)
      f.write("\n")

      # no print because to much lines
      continue
      with pd.option_context(
        'display.max_rows', None,
        'display.max_columns', None,
        'display.precision', 7,
        'display.width', None,
      ):
        print(header)
        print(df)
        print()
  return None
