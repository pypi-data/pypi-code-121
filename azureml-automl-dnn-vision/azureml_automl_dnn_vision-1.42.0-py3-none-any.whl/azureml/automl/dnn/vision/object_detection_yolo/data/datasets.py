# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" Classes and functions to inject data for yolo object detection model """

import numpy as np
import torch

from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.prediction_dataset import PredictionDataset
from azureml.automl.dnn.vision.object_detection.data.datasets import \
    FileObjectDetectionDataset, AmlDatasetObjectDetection
from azureml.automl.dnn.vision.object_detection_yolo.utils.utils import get_image_label_info, \
    convert_to_yolo_labels, letterbox, xywh2xyxy, load_image, unpad_bbox
from azureml.automl.dnn.vision.object_detection_yolo.common.constants import YoloParameters, YoloLiterals
from azureml.core import Dataset as AmlDataset


logger = get_logger(__name__)


def _collate_function(batch):
    """Custom collate function for training and validation

    :param batch: list of samples (image, label and image_info)
    :type batch: list
    :return: Images, Labels and Image Infos
    :rtype: tuple of (image pixels), tuple of (bbox information), tuple of (image info)
    """
    img, label, image_info = zip(*batch)  # transposed
    for i, l in enumerate(label):
        l[:, 0] = i  # add target image index for build_targets()
    return torch.stack(img, 0), torch.cat(label, 0), image_info


def _prepare_image_data_for_eval(image_targets, image_info):
    """ Convert image data (part of output of __getitem__) to a format suitable for calculating
    eval metrics. The output should be a tuple of image_info and box_info. box_info should be a dictionary containing
    boxes in unnormalized xyxy format and labels as a 1d torch.tensor of dtype torch.long.

    :param image_targets: Targets for an image (part of output of __getitem__)
    :type image_targets: torch.tensor
    :param image_info: Image info (part of output of __getitem__)
    :type image_info: dict
    :return: Tuple of image_info and box_info (Dictionary containing boxes, labels and optionally masks)
    :rtype: Tuple[Dict, Dict]
    """
    labels = image_targets[:, 1].to(dtype=torch.long)
    # Convert normalized xywh to pixel xyxy
    boxes = image_targets[:, 2:]
    boxes = xywh2xyxy(boxes)
    boxes[:, ::2] *= image_info["width"]
    boxes[:, 1::2] *= image_info["height"]
    height, width = unpad_bbox(boxes, (image_info["height"], image_info["width"]), (image_info["pad"]))
    image_info["width"] = width
    image_info["height"] = height
    return image_info, {"boxes": boxes, "labels": labels}


class FileObjectDetectionDatasetYolo(FileObjectDetectionDataset):
    """Wrapper for object detection dataset for Yolo"""

    def __init__(self, annotations_file=None, image_folder=".", is_train=False,
                 prob=0.5, ignore_data_errors=True,
                 use_bg_label=False, label_compute_func=convert_to_yolo_labels,
                 settings=None, masks_required=False,
                 tile_grid_size=None, tile_overlap_ratio=None, use_cv2=True):
        """TODO RK: comments"""

        # TODO RK: find a better way to pass the settings - assuming some properties in the dict is not good design
        self._img_size = settings[YoloLiterals.IMG_SIZE]
        super(FileObjectDetectionDatasetYolo, self).__init__(
            annotations_file=annotations_file, image_folder=image_folder, is_train=is_train,
            prob=prob, ignore_data_errors=ignore_data_errors, use_bg_label=use_bg_label,
            label_compute_func=label_compute_func, settings=settings, masks_required=masks_required,
            tile_grid_size=tile_grid_size, tile_overlap_ratio=tile_overlap_ratio, use_cv2=use_cv2)

    @property
    def img_size(self):
        """Image size.

        :return: Image size
        :rtype: int
        """
        return self._img_size

    def get_image_label_info(self, dataset_element):
        """TODO RK: bad design to assume the fields in the parent - rely on properties"""
        dataset_elements = self.get_dataset_elements()
        return get_image_label_info(dataset_element, dataset_elements, self._img_size, self._labels, self._annotations,
                                    self._settings, self._is_train, self._ignore_data_errors)

    def collate_function(self, batch):
        """Collate function to use to form a batch"""
        return _collate_function(batch)

    def prepare_image_data_for_eval(self, image_targets, image_info):
        """ Convert image data (part of output of __getitem__) to a format suitable for calculating
        eval metrics. The output should be a tuple of image_info and box_info. box_info should be a dictionary
        containing boxes in unnormalized xyxy format and labels as a 1d torch.tensor of dtype torch.long.

        :param image_targets: Targets for an image (part of output of __getitem__)
        :type image_targets: torch.tensor
        :param image_info: Image info (part of output of __getitem__)
        :type image_info: dict
        :return: Tuple of image_info and box_info (Dictionary containing boxes, labels and optionally masks)
        :rtype: Tuple[Dict, Dict]
        """
        return _prepare_image_data_for_eval(image_targets, image_info)


class AmlDatasetObjectDetectionYolo(AmlDatasetObjectDetection):
    """Wrapper for Aml labeled dataset for object detection dataset"""

    def __init__(self, dataset, is_train=False, settings=None,
                 ignore_data_errors=False,
                 use_bg_label=False, label_column_name=None,
                 masks_required=False, tile_grid_size=None, tile_overlap_ratio=None, use_cv2=True):
        """
        :param dataset: dataset
        :type dataset: AbstractDataset
        :param is_train: which mode (training, inferencing) is the network in?
        :type is_train: bool
        :param settings: yolo specific settings
        :type settings: dict
        :param ignore_data_errors: Setting this ignores and files in the labeled dataset that fail to download.
        :type ignore_data_errors: bool
        :param use_bg_label: flag to indicate if we use incluse the --bg-- label
        :type use_bg_label: bool
        :param label_column_name: Label column name
        :type label_column_name: str
        :param masks_required: If masks information is required
        :type masks_required: bool
        :param tile_grid_size: The grid size to split the image into, if tiling is enabled. None, otherwise
        :type tile_grid_size: Tuple[int, int]
        :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
                                   None, if tile_grid_size is None
        :type tile_overlap_ratio: float
        :param use_cv2: Use cv2 for reading image dimensions
        :type use_cv2: bool
        """
        self._img_size = settings[YoloLiterals.IMG_SIZE]
        super().__init__(dataset=dataset, is_train=is_train,
                         ignore_data_errors=ignore_data_errors,
                         use_bg_label=use_bg_label, label_compute_func=convert_to_yolo_labels,
                         label_column_name=label_column_name, settings=settings, masks_required=masks_required,
                         tile_grid_size=tile_grid_size, tile_overlap_ratio=tile_overlap_ratio,
                         use_cv2=use_cv2)

    @property
    def img_size(self):
        """Image size.

        :return: Image size
        :rtype: int
        """
        return self._img_size

    def get_image_label_info(self, dataset_element):
        """TODO RK: bad design to assume the fields in the parent - rely on properties"""
        dataset_elements = self.get_dataset_elements()
        return get_image_label_info(dataset_element, dataset_elements, self._img_size, self._labels, self._annotations,
                                    self._settings, self._is_train, self._ignore_data_errors)

    def collate_function(self, batch):
        """Collate function to use to form a batch"""
        return _collate_function(batch)

    def prepare_image_data_for_eval(self, image_targets, image_info):
        """ Convert image data (part of output of __getitem__) to a format suitable for calculating
        eval metrics. The output should be a tuple of image_info and box_info. box_info should be a dictionary
        containing boxes in unnormalized xyxy format and labels as a 1d torch.tensor of dtype torch.long.

        :param image_targets: Targets for an image (part of output of __getitem__)
        :type image_targets: torch.tensor
        :param image_info: Image info (part of output of __getitem__)
        :type image_info: dict
        :return: Tuple of image_info and box_info (Dictionary containing boxes, labels and optionally masks)
        :rtype: Tuple[Dict, Dict]
        """
        return _prepare_image_data_for_eval(image_targets, image_info)


class PredictionDatasetYolo(PredictionDataset):
    """Dataset file so that score.py can process images in batches.

    """

    def __init__(self, root_dir=None, image_list_file=None, img_size=YoloParameters.DEFAULT_IMG_SIZE,
                 ignore_data_errors=True, input_dataset=None,
                 tile_grid_size=None, tile_overlap_ratio=None):
        """
        :param root_dir: prefix to be added to the paths contained in image_list_file
        :type root_dir: str
        :param image_list_file: path to file containing list of images
        :type image_list_file: str
        :param img_size: image size for inference
        :type img_size: int
        :param ignore_data_errors: boolean flag on whether to ignore input data errors
        :type ignore_data_errors: bool
        :param input_dataset: The input dataset.  If this is specified image_list_file is not required.
        :type input_dataset: AbstractDataset
        """
        self.img_size = img_size
        super(PredictionDatasetYolo, self).__init__(root_dir=root_dir, image_list_file=image_list_file,
                                                    ignore_data_errors=ignore_data_errors,
                                                    input_dataset=input_dataset,
                                                    tile_grid_size=tile_grid_size,
                                                    tile_overlap_ratio=tile_overlap_ratio)

    def __getitem__(self, idx):
        """
        :param idx: index
        :type idx: int
        :return: item and label at index idx
        :rtype: tuple[str, image]
        """
        filename, full_path = self.get_image_full_path(idx)
        tile = self._elements[idx].tile

        _, image, image_info = self._load_image(full_path, tile, self.img_size)
        return filename, image, image_info

    def _load_image(self, image_url, tile, img_size=YoloParameters.DEFAULT_IMG_SIZE):
        # Load image
        img, (h0, w0), (h, w) = load_image(image_url, tile, img_size, augment=False,
                                           ignore_data_errors=self._ignore_data_errors)
        if img is None:
            return image_url, None, None

        # Letterbox
        img, ratio, pad = letterbox(img, new_shape=img_size, auto=False, scaleup=False)

        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x640x640
        img = np.ascontiguousarray(img)

        image_info = {"original_width": w0, "original_height": h0, "pad": pad}
        if tile is not None:
            image_info.update({"tile": tile})

        return image_url, torch.from_numpy(img), image_info

    @staticmethod
    def collate_function(batch):
        """Custom collate function for inference

        :param batch: list of samples (path, image and pad)
        :type batch: list
        :return: Paths, Images and Pads
        :rtype: tuple of (image path), tuple of (image pixels), tuple of (pad used in letterbox image)
        """
        fname, imgs, image_infos = zip(*batch)
        return fname, torch.stack(imgs, 0), image_infos
