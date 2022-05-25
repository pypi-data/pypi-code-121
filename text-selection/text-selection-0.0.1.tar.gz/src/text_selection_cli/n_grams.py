# from argparse import ArgumentParser, Namespace
# from logging import getLogger
# from pathlib import Path
# from typing import cast

# from text_selection_app.argparse_helper import (ConvertToOrderedSetAction, parse_existing_directory,
#                                                 parse_non_empty, parse_non_empty_or_whitespace,
#                                                 parse_positive_integer)
# from text_selection_app.default_args import (add_chunksize_argument, add_maxtaskperchild_argument,
#                                              add_n_jobs_argument)
# from text_selection_app.helper import get_datasets
# from text_selection_app.io_handling import (DATA_SYMBOLS_NAME, DATASET_NAME, get_data_n_grams_path,
#                                             get_data_symbols_path, load_data_symbols, load_dataset,
#                                             save_data_n_grams)
# from text_selection_core.preparation.n_grams import get_n_  # grams


# def get_n_grams_extraction_parser(parser: ArgumentParser):
#   parser.description = f"This command calculates n-grams."
#   parser.add_argument("directory", type=parse_existing_directory, metavar="directory",
#                       help="directory containing data")
#   parser.add_argument("subsets", type=parse_non_empty_or_whitespace, nargs="+", metavar="subsets",
#                       help="subsets for which the n-grams should be calculated", action=ConvertToOrderedSetAction)
#   parser.add_argument("n_gram", type=parse_positive_integer, metavar="n-gram",
#                       help="n-gram; needs to be greater than zero")
#   parser.add_argument("--name", type=parse_non_empty_or_whitespace, metavar="NAME",
#                       help="name of the n-grams", default="n-grams")
#   parser.add_argument("--ignore", type=parse_non_empty, nargs="*", metavar="ignore",
#                       help="ignore n-grams containing these symbols", default=[], action=ConvertToOrderedSetAction)
#   add_n_jobs_argument(parser)
#   add_chunksize_argument(parser, "items")
#   add_maxtaskperchild_argument(parser)
#   parser.add_argument("-o", "--overwrite", action="store_true",
#                       help="overwrite n-grams")
#   return n_grams_extraction_ns


# def n_grams_extraction_ns(ns: Namespace, logger: Logger, flogger: Logger) -> ExecutionResult:
#   logger = getLogger(__name__)
#   logger.debug(ns)
#   root_folder = cast(Path, ns.directory)
#   datasets = get_datasets(root_folder, logger)

#   if ns.name in {DATASET_NAME, DATA_SYMBOLS_NAME}:
#     logger.error("The given name is not valid.")
#     return

#   for i, dataset_path in enumerate(datasets, start=1):
#     data_folder = dataset_path.parent
#     data_name = str(data_folder.relative_to(root_folder)
#                     ) if root_folder != data_folder else "root"
#     logger.info(f"Processing {data_name} ({i}/{len(datasets)})")

#     symbols_path = get_data_symbols_path(data_folder)
#     if not symbols_path.exists():
#       logger.error(
#         f"Symbols were not found! Skipping...")
#       continue

#     n_grams_path = get_data_n_grams_path(data_folder, ns.name)

#     if n_grams_path.is_file() and not ns.overwrite:
#       logger.error("N-grams already exist! Skipped.")
#       continue

#     dataset = load_dataset(dataset_path)
#     symbols = load_data_symbols(symbols_path)

#     logger.debug("Selecting...")
#     error, n_grams = get_n_grams(
#       dataset, ns.subsets, symbols, ns.n_gram, ns.ignore, None, None, ns.n_jobs, ns.maxtasksperchild, ns.chunksize)

#     success = error is None

#     if not success:
#       logger.error(f"{error.default_message}")
#       logger.info("Skipped.")
#     else:
#       assert n_grams is not None
#       save_data_n_grams(n_grams_path, n_grams)
