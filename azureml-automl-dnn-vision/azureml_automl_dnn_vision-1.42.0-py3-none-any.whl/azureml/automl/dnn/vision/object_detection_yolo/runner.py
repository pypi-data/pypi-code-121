# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Entry script that is invoked by the driver script from automl."""

import argparse
import time
import torch

from distutils.util import strtobool
from typing import Any, Dict, List, Tuple, cast, Optional

from azureml.automl.core.shared.constants import Tasks

from azureml.automl.dnn.vision.common import artifacts_utils, utils
from azureml.automl.dnn.vision.common.constants import (
    ArtifactLiterals, SettingsLiterals, DistributedLiterals, TrainingLiterals as CommonTrainingLiterals,
    DistributedParameters
)
from azureml.automl.dnn.vision.common.trainer.lrschedule import setup_lr_scheduler
from azureml.automl.dnn.vision.common.trainer.optimize import setup_optimizer
from azureml.automl.dnn.vision.object_detection.data.datasets import AmlDatasetObjectDetection

from azureml.automl.dnn.vision.object_detection.common.constants import ModelNames
from azureml.automl.dnn.vision.object_detection.common.parameters import add_model_agnostic_od_train_parameters
from azureml.automl.dnn.vision.object_detection_yolo.common.constants import (
    ModelSize, YoloLiterals, YoloParameters, training_settings_defaults, yolo_hyp_defaults, safe_to_log_settings
)
from azureml.automl.dnn.vision.object_detection_yolo.data.utils import setup_dataloaders, download_required_files
from azureml.automl.dnn.vision.object_detection_yolo.models.yolo_wrapper import YoloV5Wrapper
from azureml.automl.dnn.vision.object_detection_yolo.writers.score import _score_with_model
from azureml.core.run import Run

from .data import datasets
from .trainer.train import train
from .utils.utils import init_seeds
from ..common import distributed_utils
from ..common.data_utils import validate_labels_files_paths
from ..common.exceptions import AutoMLVisionValidationException
from ..common.logging_utils import get_logger, clean_settings_for_logging
from ..common.parameters import add_task_agnostic_train_parameters
from ..common.system_meter import SystemMeter
from ..common.sku_validation import validate_gpu_sku
from ..object_detection.common.object_detection_utils import score_validation_data
from ..object_detection.models import detection

azureml_run = Run.get_context()

logger = get_logger(__name__)


@utils._exception_handler
def run(automl_settings: Dict[str, Any], mltable_data_json: Optional[str] = None, **kwargs) -> None:
    """Invoke training by passing settings and write the resulting model.

    :param automl_settings: Dictionary with all training and model settings
    :type automl_settings: Dict[str, Any]
    :param mltable_data_json: Json containing the uri for train/validation/test datasets.
    :type mltable_data_json: str
    """
    script_start_time = time.time()

    settings, unknown = _parse_argument_settings(automl_settings)

    utils._top_initialization(settings)

    task_type = settings.get(SettingsLiterals.TASK_TYPE, None)

    if not task_type:
        raise AutoMLVisionValidationException("Task type was not found in automl settings.",
                                              has_pii=False)
    utils._set_logging_parameters(task_type, settings)

    if unknown:
        logger.info("Got unknown args, will ignore them.")

    logger.info("Final settings (pii free): \n {}".format(clean_settings_for_logging(settings, safe_to_log_settings)))
    logger.info("Settings not logged (might contain pii): \n {}".format(settings.keys() - safe_to_log_settings))

    if mltable_data_json is None:
        validate_labels_files_paths(settings)

    train_ds, validation_ds = utils.get_tabular_dataset(settings=settings, mltable_json=mltable_data_json)

    # Download required files before launching train_worker to avoid concurrency issues in distributed mode
    download_required_files(settings, train_ds, validation_ds, AmlDatasetObjectDetection)

    distributed_utils.launch_single_or_distributed_training(settings=settings, train_worker_fn=train_worker,
                                                            additional_train_worker_fn_args=(mltable_data_json,),
                                                            logger=logger)

    utils.log_script_duration(script_start_time, settings, azureml_run)


# Adding handler to log exceptions directly in the child process if using multigpu
@utils._exception_logger
def train_worker(rank: int, settings: Dict[str, Any], mltable_data_json: Optional[str]):
    """Invoke training on a single device and write the resulting model.

    :param rank: Rank of the process if invoked in distributed mode. 0 otherwise.
    :type rank: int
    :param settings: Dictionary with all training and model settings
    :type settings: Dictionary
    :param mltable_data_json: MLTable json
    :param type: str
    """
    distributed_utils.enable_distributed_logging(settings, rank)

    distributed = settings[DistributedLiterals.DISTRIBUTED]
    if distributed:
        distributed_utils.setup_distributed_training(rank, settings, logger)

    system_meter = SystemMeter(log_static_sys_info=True)
    system_meter.log_system_stats()

    # TODO: check if this works in child processes
    tb_writer = utils.init_tensorboard()

    # Set random seed
    random_seed = settings.get(SettingsLiterals.RANDOM_SEED, None)
    if distributed and random_seed is None:
        # Set by default for distributed training to ensure
        # all workers have same random parameters.
        random_seed = DistributedParameters.DEFAULT_RANDOM_SEED
    if random_seed is not None:
        init_seeds(random_seed)

    if distributed:
        settings[SettingsLiterals.DEVICE] = torch.device("cuda:" + str(rank))
    device = settings[SettingsLiterals.DEVICE]
    master_process = distributed_utils.master_process()
    validate_gpu_sku(device=device)
    output_directory = ArtifactLiterals.OUTPUT_DIR

    utils.warn_for_cpu_devices(device, azureml_run)

    task_type = settings.get(SettingsLiterals.TASK_TYPE, None)
    masks_required = task_type == Tasks.IMAGE_INSTANCE_SEGMENTATION

    # Get datasets
    train_ds, validation_ds = utils.get_tabular_dataset(
        settings=settings, mltable_json=mltable_data_json)

    # Set data loaders
    train_loader, validation_loader = setup_dataloaders(
        settings, output_directory, train_ds, validation_ds, masks_required)

    # Update # of class
    nc = train_loader.dataset.dataset.num_classes

    # Create model
    settings['cls'] *= nc / 80.  # scale coco-tuned settings['cls'] to current dataset
    settings['gr'] = 1.0  # giou loss ratio (obj_loss = 1.0 or giou)

    model_wrapper = cast(YoloV5Wrapper,
                         detection.setup_model(model_name=ModelNames.YOLO_V5,
                                               number_of_classes=nc,
                                               classes=train_loader.dataset.dataset.classes,
                                               device=device,
                                               distributed=distributed,
                                               # TODO only add the relevant fields in the settings
                                               specs=settings))

    # TODO: when large or xlarge is chosen, reduce batch_size to avoid CUDA out of memory
    # TODO: make sure model_size exists in all types accepted by model_wrapper
    if device != 'cpu' and model_wrapper.model_size in ['large', 'xlarge']:
        logger.warning("[model_size (medium) is supported on 12GiB GPU memory with a batch_size of 16. "
                       "Your choice of model_size ({}) and a batch_size of {} might lead to CUDA OOM]"
                       .format(model_wrapper.model_size, settings[CommonTrainingLiterals.TRAINING_BATCH_SIZE]))

    # Load model weight from previously saved checkpoint for incremental training
    artifacts_utils.load_from_pretrained_checkpoint(settings, model_wrapper, distributed=distributed)

    num_params = sum(x.numel() for x in model_wrapper.parameters())  # number parameters
    logger.info("[model: {} ({}), # layers: {}, # param: {}]".format(
        settings[SettingsLiterals.MODEL_NAME],
        model_wrapper.model_size,
        len(list(model_wrapper.parameters())),
        num_params))

    # setup optimizer
    optimizer = setup_optimizer(model_wrapper.model, settings=settings)
    # setup lr_scheduler
    lr_scheduler = setup_lr_scheduler(optimizer, batches_per_epoch=len(train_loader), settings=settings)

    # Train
    train(model_wrapper=model_wrapper, optimizer=optimizer, scheduler=lr_scheduler,
          train_loader=train_loader, validation_loader=validation_loader,
          output_dir=output_directory, azureml_run=azureml_run, tb_writer=tb_writer)

    # Run scoring
    run_scoring = settings.get(SettingsLiterals.OUTPUT_SCORING, False)
    if master_process and run_scoring:
        score_validation_data(run=azureml_run, model_settings=model_wrapper.model_settings.get_settings_dict(),
                              settings=settings, device=device,
                              val_dataset=validation_ds,
                              score_with_model=_score_with_model)


def _parse_argument_settings(automl_settings: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Parse all arguments and merge settings

    :param automl_settings: Dictionary with all training and model settings
    :type automl_settings: Dict[str, Any]
    :return: tuple of the automl settings dictionary with all settings filled in and a list of any unknown args
    :rtype: Tuple[Dict[str, Any], List[str]]
    """

    parser = argparse.ArgumentParser(description="Object detection (using yolov5)", allow_abbrev=False)
    add_task_agnostic_train_parameters(parser, training_settings_defaults)

    add_model_agnostic_od_train_parameters(parser, training_settings_defaults)

    # Model (yolov5) Settings
    parser.add_argument(utils._make_arg(YoloLiterals.IMG_SIZE), type=int,
                        help='Image size for train and validation',
                        default=YoloParameters.DEFAULT_IMG_SIZE)

    parser.add_argument(utils._make_arg(YoloLiterals.MODEL_SIZE), type=str,
                        choices=ModelSize.ALL_TYPES,
                        help='Model size in {small, medium, large, xlarge}',
                        default=YoloParameters.DEFAULT_MODEL_SIZE)

    parser.add_argument(utils._make_arg(YoloLiterals.MULTI_SCALE),
                        type=lambda x: bool(strtobool(str(x))),
                        help='Enable multi-scale image by varying image size by +/- 50%%',
                        default=YoloParameters.DEFAULT_MULTI_SCALE)

    parser.add_argument(utils._make_arg(YoloLiterals.BOX_SCORE_THRESH), type=float,
                        help="During inference, only return proposals with a score \
                              greater than box_score_thresh. The score is the multiplication of \
                              the objectness score and classification probability",
                        default=YoloParameters.DEFAULT_BOX_SCORE_THRESH)

    parser.add_argument(utils._make_arg(YoloLiterals.NMS_IOU_THRESH), type=float,
                        help="IOU threshold used during inference in nms post processing",
                        default=YoloParameters.DEFAULT_NMS_IOU_THRESH)

    args, unknown = parser.parse_known_args()
    args_dict = vars(args)
    args_dict = utils.parse_model_conditional_space(args_dict)

    # When tile_grid_size is passed as part of conditional HP space, it would be a string. This functions parses
    # the string and converts it to a tuple.
    utils.fix_tiling_settings_in_args_dict(args_dict)

    # Update training default settings with yolo specific hyper-parameters
    training_settings_defaults.update(yolo_hyp_defaults)
    utils.set_validation_size(automl_settings, args_dict)
    # Training settings
    return utils._merge_settings_args_defaults(automl_settings, args_dict, training_settings_defaults), unknown
