import pickle
from logging import Logger
from pathlib import Path
from typing import Any, Optional, Union, cast

import numpy as np

from text_selection_cli.validation import CliErrorType, CliValidationErr
from text_selection_core.types import Dataset, DataWeights, Lines
from text_selection_core.validation import ValidationErrBase


def save_obj(obj: Any, path: Path) -> None:
  assert isinstance(path, Path)
  assert path.parent.exists() and path.parent.is_dir()
  with open(path, mode="wb") as file:
    pickle.dump(obj, file)


def load_obj(path: Path) -> Any:
  assert isinstance(path, Path)
  assert path.is_file()
  with open(path, mode="rb") as file:
    return pickle.load(file)


def try_load_file(path: Path, encoding: str, lsep: str, logger: Logger) -> Union[CliValidationErr, Lines]:
  logger.info(f"Reading \"{path.absolute()}\"...")
  try:
    text = path.read_text(encoding)
  except Exception as ex:
    logger.exception(ex)
    return CliValidationErr(CliErrorType.FILE_NOT_READABLE, "File", path.absolute())

  logger.info("Separating lines...")
  lines = text.split(lsep)
  del text
  return lines

def try_save_text(path: Path, text: str, encoding: str, logger: Logger) -> Optional[CliValidationErr]:
  logger.info(f"Saving text to \"{path.absolute()}\"...")
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding)
  except Exception as ex:
    logger.exception(ex)
    return CliValidationErr(CliErrorType.FILE_NOT_WRITEABLE, "Text", path.absolute())
  return None


def try_load_dataset(path: Path, logger: Logger) -> Union[CliValidationErr, Dataset]:
  logger.info(f"Reading dataset from \"{path.absolute()}\"...")
  try:
    result = cast(Dataset, load_obj(path))
  except Exception as ex:
    logger.exception(ex)
    return CliValidationErr(CliErrorType.FILE_NOT_READABLE, "Dataset", path.absolute())
  return result


def try_save_dataset(path: Path, dataset: Dataset, logger: Logger) -> Optional[CliValidationErr]:
  logger.info(f"Saving dataset to \"{path.absolute()}\"...")
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    save_obj(dataset, path)
  except Exception as ex:
    logger.exception(ex)
    return CliValidationErr(CliErrorType.FILE_NOT_WRITEABLE, "Dataset", path.absolute())
  return None


def try_load_data_weights(path: Path, logger: Logger) -> Union[CliValidationErr, DataWeights]:
  logger.info(f"Reading weights from \"{path.absolute()}\"...")
  try:
    result = np.load(path, allow_pickle=False, fix_imports=False)
  except Exception as ex:
    logger.exception(ex)
    return CliValidationErr(CliErrorType.FILE_NOT_READABLE, "Weights", path.absolute())

  return result


def try_save_data_weights(path: Path, data_weights: DataWeights, logger: Logger) -> Optional[ValidationErrBase]:
  logger.info(f"Saving weights to \"{path.absolute()}\"...")
  try:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, data_weights, allow_pickle=False, fix_imports=False)
    # save_obj(data_weights, path)
  except Exception as ex:
    logger.exception(ex)
    return CliValidationErr(CliErrorType.FILE_NOT_WRITEABLE, "Dataset", path.absolute())
  return None
