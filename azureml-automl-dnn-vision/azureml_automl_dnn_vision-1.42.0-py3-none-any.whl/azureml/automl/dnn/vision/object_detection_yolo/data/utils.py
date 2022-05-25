# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper classes and functions for creating operating with datasets and dataloaders."""

import os

from azureml.automl.dnn.vision.common import utils, distributed_utils
from azureml.automl.dnn.vision.common.constants import DistributedLiterals, SettingsLiterals, \
    TrainingLiterals as CommonTrainingLiterals
from azureml.automl.dnn.vision.common.data_utils import get_labels_files_paths_from_settings
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.object_detection.common.constants import TilingLiterals
from azureml.automl.dnn.vision.object_detection.data.loaders import setup_dataloader
from azureml.automl.dnn.vision.object_detection.data.utils import read_aml_dataset, read_file_dataset, \
    setup_dataset_wrappers
from azureml.automl.dnn.vision.object_detection_yolo.data.datasets import \
    FileObjectDetectionDatasetYolo, AmlDatasetObjectDetectionYolo
from azureml.automl.dnn.vision.object_detection_yolo.common.constants import YoloLiterals, YoloParameters
from azureml.automl.dnn.vision.object_detection_yolo.utils.utils import check_img_size
from azureml.automl.dnn.vision.common.pretrained_model_utilities import PretrainedModelFactory, PretrainedModelUrls

logger = get_logger(__name__)


def download_required_files(settings, train_ds, validation_ds, dataset_class):
    """Download files required for Aml dataset and model setup.

    This step needs to be done before launching distributed training so that there are no concurrency issues
    where multiple processes are downloading the same file.

    :param settings: Dictionary with all training and model settings
    :type settings: Dict
    :param train_ds: Training dataset
    :type train_ds: AbstractDataset
    :param validation_ds: Validation dataset
    :type validation_ds: AbstractDataset
    :param dataset_class: DatasetWrapper used for Aml Dataset input
    :type dataset_class: Class derived from vision.common.base_aml_dataset_wrapper.AmlDatasetBaseWrapper
    """
    # Download aml dataset to local disk
    if train_ds is not None:
        logger.info("Downloading training dataset files to local disk.")
        dataset_class.download_image_files(train_ds)
        if validation_ds is not None:
            logger.info("Downloading validation dataset files to local disk.")
            dataset_class.download_image_files(validation_ds)

    # Download pretrained model weights and cache on local disk
    logger.info("Downloading pretrained model weights to local disk.")
    model_size = settings.get(YoloLiterals.MODEL_SIZE, YoloParameters.DEFAULT_MODEL_SIZE)
    size = model_size[0]
    model_name = settings.get(SettingsLiterals.MODEL_NAME)
    if model_name is None:
        model_name = YoloParameters.DEFAULT_MODEL_NAME
    model_size_with_version = model_name[:-1] + YoloParameters.DEFAULT_MODEL_VERSION + size

    # Download pretrained model weights based on model size
    PretrainedModelFactory._load_state_dict_from_url_with_retry(
        PretrainedModelUrls.MODEL_URLS[model_size_with_version])

    # Update settings with the chosen model_name
    settings[SettingsLiterals.MODEL_NAME] = model_name

    # Download a pretrained checkpoint to local disk for incremental training
    utils.download_checkpoint_for_incremental_training(settings)


def setup_dataloaders(settings, output_directory, dataset=None, validation_dataset=None, masks_required=False):
    """Settings for (file and aml) datasets and data loaders

    :param settings: Dictionary with all training and model settings
    :type settings: Dictionary
    :param output_directory: Name of dir to save files for training/validation dataset
    :type output_directory: str
    :param dataset: Training dataset
    :type dataset: AbstractDataset
    :param validation_dataset: Validation dataset
    :type validation_dataset: AbstractDataset
    :param masks_required: If masks information is required
    :type masks_required: bool
    :return: train_loader and validation_loader
    :rtype: Tuple of form (dataloaders.RobustDataLoader, dataloaders.RobustDataLoader)
    """

    # Settings for both
    validation_size = settings[CommonTrainingLiterals.VALIDATION_SIZE]
    ignore_data_errors = settings.get(SettingsLiterals.IGNORE_DATA_ERRORS, True)
    settings['img_size'] = check_img_size(settings['img_size'], settings['gs'])

    tile_grid_size = settings.get(TilingLiterals.TILE_GRID_SIZE, None)
    tile_overlap_ratio = settings.get(TilingLiterals.TILE_OVERLAP_RATIO, None)
    label_column_name = settings.get(SettingsLiterals.LABEL_COLUMN_NAME, None)
    # Setup Dataset
    if dataset is not None:
        train_ds_wrapper, val_ds_wrapper = read_aml_dataset(dataset=dataset,
                                                            validation_dataset=validation_dataset,
                                                            validation_size=validation_size,
                                                            settings=settings,
                                                            ignore_data_errors=ignore_data_errors,
                                                            output_dir=output_directory,
                                                            master_process=distributed_utils.master_process(),
                                                            dataset_class=AmlDatasetObjectDetectionYolo,
                                                            use_bg_label=False,
                                                            masks_required=masks_required,
                                                            tile_grid_size=tile_grid_size,
                                                            label_column_name=label_column_name,
                                                            tile_overlap_ratio=tile_overlap_ratio)
    else:
        image_folder = settings.get(SettingsLiterals.IMAGE_FOLDER, None)

        if image_folder is None:
            raise AutoMLVisionValidationException("images_folder or dataset_id needs to be specified",
                                                  has_pii=False)
        else:
            image_folder = os.path.join(settings[SettingsLiterals.DATA_FOLDER], image_folder)

        train_labels_file, val_labels_file = get_labels_files_paths_from_settings(settings)

        train_ds_wrapper, val_ds_wrapper = read_file_dataset(image_folder=image_folder,
                                                             annotations_file=train_labels_file,
                                                             annotations_test_file=val_labels_file,
                                                             validation_size=validation_size,
                                                             settings=settings,
                                                             ignore_data_errors=ignore_data_errors,
                                                             output_dir=output_directory,
                                                             dataset_class=FileObjectDetectionDatasetYolo,
                                                             master_process=distributed_utils.master_process(),
                                                             use_bg_label=False,
                                                             masks_required=masks_required,
                                                             tile_grid_size=tile_grid_size,
                                                             tile_overlap_ratio=tile_overlap_ratio)
        logger.info("[train file: {}, validation file: {}]".format(train_labels_file, val_labels_file))

    # Update classes
    if train_ds_wrapper.classes != val_ds_wrapper.classes:
        all_classes = list(
            set(train_ds_wrapper.classes + val_ds_wrapper.classes))
        train_ds_wrapper.reset_classes(all_classes)
        val_ds_wrapper.reset_classes(all_classes)

    logger.info("[# train images: {}, # validation images: {}, # labels: {}, image size: {}]".format(
        len(train_ds_wrapper), len(val_ds_wrapper), train_ds_wrapper.num_classes, settings['img_size']))

    distributed = settings[DistributedLiterals.DISTRIBUTED]

    training_dataset_wrapper, validation_dataset_wrapper = setup_dataset_wrappers(
        train_ds_wrapper, val_ds_wrapper, tile_grid_size)

    # Setup Dataloaders
    train_dataloader_settings = {'batch_size': settings[CommonTrainingLiterals.TRAINING_BATCH_SIZE],
                                 'shuffle': True,
                                 'num_workers': settings[SettingsLiterals.NUM_WORKERS],
                                 'distributed': distributed,
                                 'drop_last': False}
    val_dataloader_settings = {'batch_size': settings[CommonTrainingLiterals.VALIDATION_BATCH_SIZE],
                               'shuffle': False,
                               'num_workers': settings[SettingsLiterals.NUM_WORKERS],
                               'distributed': distributed,
                               'drop_last': False}

    train_loader = setup_dataloader(training_dataset_wrapper, **train_dataloader_settings)
    validation_loader = setup_dataloader(validation_dataset_wrapper, **val_dataloader_settings)

    return train_loader, validation_loader
