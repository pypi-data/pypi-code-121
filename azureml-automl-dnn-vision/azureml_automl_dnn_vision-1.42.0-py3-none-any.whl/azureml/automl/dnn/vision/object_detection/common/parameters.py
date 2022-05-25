# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Parameters that apply to OD model training"""

from argparse import ArgumentParser
from typing import Any, Dict

from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.constants import SettingsLiterals
from azureml.automl.dnn.vision.common.tiling_utils import parse_tile_grid_size_str
from azureml.automl.dnn.vision.object_detection.common.constants import (
    TrainingLiterals, ValidationMetricType, TilingLiterals, TrainingParameters
)


def add_model_agnostic_od_train_parameters(parser: ArgumentParser, default_values: Dict[str, Any]) -> None:
    """Adds to the parser object detection training parameters that are model agnostic.

    :param parser: args parser
    :type parser: ArgumentParser
    :param default_values: default values for the parameters
    :type default_values: dict
    :return: None
    """
    # Metric settings
    parser.add_argument(utils._make_arg(TrainingLiterals.VALIDATION_METRIC_TYPE),
                        choices=ValidationMetricType.ALL_TYPES,
                        help="Metric computation method to use for validation metrics",
                        default=default_values[TrainingLiterals.VALIDATION_METRIC_TYPE])

    parser.add_argument(utils._make_arg(TrainingLiterals.VALIDATION_IOU_THRESHOLD), type=float,
                        help="IOU threshold to use when computing validation metrics",
                        default=default_values[TrainingLiterals.VALIDATION_IOU_THRESHOLD])

    # Tiling settings
    # Note that we use parse_tile_grid_size_str here as HyperDrive doesn't support search space with
    # choice of tuples/lists. Hence, we accept a string and parse it here.
    parser.add_argument(utils._make_arg(TilingLiterals.TILE_GRID_SIZE), type=parse_tile_grid_size_str,
                        help="The tile grid size to use for tiling the image during training/validation. \
                        Should be passed as a string in one of \"(3, 2)\" or \"3x2\" or \"3X2\" formats. \
                        Example: --tile_grid_size \"(3, 2)\" or --tile_grid_size \"3x2\" or --tile_grid_size \"3X2\"")

    parser.add_argument(utils._make_arg(TilingLiterals.TILE_OVERLAP_RATIO), type=float,
                        help="Overlap ratio between adjacent tiles in each dimension",
                        default=default_values[TilingLiterals.TILE_OVERLAP_RATIO])

    parser.add_argument(utils._make_arg(TilingLiterals.TILE_PREDICTIONS_NMS_THRESH), type=float,
                        help="The iou threshold to use to perform nms while merging predictions from tiles and \
                        image. Used in validation",
                        default=default_values[TilingLiterals.TILE_PREDICTIONS_NMS_THRESH])


def add_model_agnostic_od_scoring_parameters(parser: ArgumentParser) -> None:
    """Adds to the parser object detection scoring parameters that are model agnostic.

    :param parser: args parser
    :type parser: ArgumentParser
    :return: None
    """
    parser.add_argument(utils._make_arg(SettingsLiterals.OUTPUT_DATASET_TARGET_PATH),
                        help='Datastore target path for output dataset files')

    # Tiling settings
    # should not set defaults for those tiling settings arguments to use those from training settings by default
    # Note that we use parse_tile_grid_size_str here to keep it consistent with arguments passed
    # for training in runner.py.
    parser.add_argument(utils._make_arg(TilingLiterals.TILE_GRID_SIZE), type=parse_tile_grid_size_str,
                        help="The tile grid size to use for tiling the image during inference. \
                        Should be passed as a string in one of \"(3, 2)\" or \"3x2\" or \"3X2\" formats. \
                        Example: --tile_grid_size \"(3, 2)\" or --tile_grid_size \"3x2\" or --tile_grid_size \"3X2\"")
    parser.add_argument(utils._make_arg(TilingLiterals.TILE_OVERLAP_RATIO), type=float,
                        help="Overlap ratio between adjacent tiles in each dimension")
    parser.add_argument(utils._make_arg(TilingLiterals.TILE_PREDICTIONS_NMS_THRESH), type=float,
                        help="The iou threshold to use to perform nms while merging predictions from tiles and \
                        image.")

    # Validation metric settings
    parser.add_argument(utils._make_arg(TrainingLiterals.VALIDATION_IOU_THRESHOLD), type=float,
                        help="The iou threshold value to use when computing validation metrics (eg mean average \
                        precision).",
                        default=TrainingParameters.DEFAULT_VALIDATION_IOU_THRESHOLD)
