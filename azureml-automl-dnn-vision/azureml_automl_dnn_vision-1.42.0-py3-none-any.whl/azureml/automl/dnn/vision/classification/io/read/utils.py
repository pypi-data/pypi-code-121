# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper classes and functions for creating operating with datasets and dataloaders."""

from azureml.automl.dnn.vision.classification.common.classification_utils import \
    _get_train_valid_sub_file_paths
from azureml.automl.dnn.vision.classification.io.read.dataset_wrappers import \
    AmlDatasetWrapper, ImageFolderLabelFileDatasetWrapper
from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.constants import SettingsLiterals
from azureml.core.run import Run


def read_aml_dataset(dataset, validation_dataset, validation_size, multilabel, output_dir, master_process,
                     label_column_name, ignore_data_errors):
    """Read the training and validation datasets from AML datasets.

    :param dataset: Training dataset
    :type dataset: AbstractDataset
    :param validation_dataset: Validation dataset
    :type validation_dataset: AbstractDataset
    :param validation_size: split ratio of dataset to use for validation if no validation dataset is defined.
    :type validation_size: float
    :param multilabel: boolean flag for whether its multilabel or not
    :type multilabel: bool
    :param output_dir: where to save train and val files
    :type output_dir: str
    :param master_process: boolean flag indicating whether current process is master or not.
    :type master_process: bool
    :param label_column_name: Label column name
    :type label_column_name: str
    :param ignore_data_errors: flag that specifies if data errors should be ignored
    :type ignore_data_errors: bool
    :return: Training dataset and validation dataset
    :rtype Tuple of form (BaseDatasetWrapper, BaseDatasetWrapper)
    """

    train_dataset_wrapper = AmlDatasetWrapper(dataset, multilabel=multilabel, label_column_name=label_column_name,
                                              ignore_data_errors=ignore_data_errors)
    if validation_dataset is None:
        train_dataset_wrapper, valid_dataset_wrapper = train_dataset_wrapper.train_val_split(
            validation_size)
    else:
        valid_dataset_wrapper = AmlDatasetWrapper(validation_dataset, multilabel=multilabel,
                                                  label_column_name=label_column_name,
                                                  ignore_data_errors=ignore_data_errors)

    if master_process:
        utils._save_image_df(train_df=train_dataset_wrapper._images_df,
                             val_df=valid_dataset_wrapper._images_df,
                             output_dir=output_dir,
                             label_column_name=label_column_name)

    return train_dataset_wrapper, valid_dataset_wrapper


def _get_train_valid_dataset_wrappers(root_dir, train_file=None, valid_file=None, multilabel=False,
                                      ignore_data_errors=True, settings=None, master_process=False):
    """
    :param root_dir: root directory that will be used as prefix for paths in train_file and valid_file
    :type root_dir: str
    :param train_file: labels file for training with filenames and labels
    :type train_file: str
    :param valid_file: labels file for validation with filenames and labels
    :type valid_file: str
    :param multilabel: boolean flag for whether its multilabel or not
    :type multilabel: bool
    :param ignore_data_errors: boolean flag on whether to ignore input data errors
    :type ignore_data_errors: bool
    :param settings: dictionary containing settings for training
    :type settings: dict
    :param master_process: boolean flag indicating whether current process is master or not.
    :type master_process: bool
    :return: tuple of train and validation dataset wrappers
    :rtype: tuple[BaseDatasetWrapper, BaseDatasetWrapper]
    """

    if valid_file is None:
        train_file, valid_file = _get_train_valid_sub_file_paths(output_dir=settings[SettingsLiterals.OUTPUT_DIR])

    train_dataset_wrapper = ImageFolderLabelFileDatasetWrapper(root_dir=root_dir, input_file=train_file,
                                                               multilabel=multilabel,
                                                               ignore_data_errors=ignore_data_errors)
    valid_dataset_wrapper = ImageFolderLabelFileDatasetWrapper(root_dir=root_dir, input_file=valid_file,
                                                               multilabel=multilabel,
                                                               all_labels=train_dataset_wrapper.labels,
                                                               ignore_data_errors=ignore_data_errors)

    if master_process:
        utils._save_image_lf(train_ds=train_file, val_ds=valid_file,
                             output_dir=settings[SettingsLiterals.OUTPUT_DIR])

    return train_dataset_wrapper, valid_dataset_wrapper
