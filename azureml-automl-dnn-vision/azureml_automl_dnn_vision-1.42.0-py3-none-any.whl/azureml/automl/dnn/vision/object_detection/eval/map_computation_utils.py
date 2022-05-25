# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Implementation details: mAP score computation functions."""

import numpy as np
import torch

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.common.logging_utils import get_logger


logger = get_logger(__name__)


def map_score_voc_11_point_metric(precision_list, recall_list):
    """
    Compute mAP score using Voc 11 point metric.
    The maximum precision at 11 recall values (0, 0.1, ..., 1.0) is computed and the average of these precision
    values is used as the mAP score.
    precision_list and recall_list should have same dimensions.

    :param precision_list: List of precision values
    :type precision_list: torch.Tensor of shape (number of precision values)
    :param recall_list: List of recall values
    :type precision_list: torch.Tensor of shape (number of recall values)
    :return: mAP score computed
    :rtype: torch.Tensor of shape ()
    """

    if precision_list.shape != recall_list.shape:
        msg = "Precision list (shape {}) and recall list (shape {}) are not of same shape. " \
              "Cannot compute map score".format(precision_list.shape, recall_list.shape)
        logger.error(msg)
        raise AutoMLVisionSystemException(msg, has_pii=False)

    score = torch.tensor(0.0)
    for recall_threshold in torch.arange(0.0, 1.1, 0.1):
        valid_precisions = precision_list[recall_list >= recall_threshold]
        if valid_precisions.nelement() == 0:
            score += 0.0
        else:
            score += torch.max(valid_precisions)
    score /= 11.0
    return score


def map_score_voc_11_point_metric_np(precision_list, recall_list):
    """
    Compute mAP score using Voc 11 point metric.

    The maximum precision at 11 recall values (0, 0.1, ..., 1.0) is computed and the average of these precision
    values is used as the mAP score.
    precision_list and recall_list should have same dimensions.

    :param precision_list: List of precision values
    :type precision_list: <class 'numpy.ndarray'> of shape (number of precision values)
    :param recall_list: List of recall values
    :type precision_list: <class 'numpy.ndarray'> of shape (number of recall values)
    :return: mAP score computed
    :rtype: <class 'numpy.ndarray'> of shape ()
    """

    # Check that the precision and recall lists are of the same length.
    if precision_list.shape != recall_list.shape:
        msg = "Precision list (shape {}) and recall list (shape {}) are not of same length. " \
              "Cannot compute map score".format(precision_list.shape, recall_list.shape)
        logger.error(msg)
        raise AutoMLVisionSystemException(msg, has_pii=False)

    # Iterate over 11 recall thresholds and sum up the precision values for them.
    sum_precisions = 0.0
    for recall_threshold in np.arange(0.0, 1.1, 0.1):
        # Get the PR curve points with recall greater than the current threshold.
        mask_recall_above_threshold = recall_list >= recall_threshold

        # If points exist, add maximum precision to running sum of precisions.
        if mask_recall_above_threshold.any():
            precisions_recall_above_threshold = precision_list[mask_recall_above_threshold]
            sum_precisions += np.max(precisions_recall_above_threshold)

    # Calculate the AUC for the PR curve via the 11 recall thresholds.
    auc = sum_precisions / 11.0

    return auc


def map_score_voc_auc(precision_list, recall_list):
    """
    Compute mAP score using Voc Area Under Curve (auc) metric.
    The recall values at which maximum precision changes are identified and these points of change are used
    to compute the area under precision recall curve.
    precision_list and recall_list should have same dimensions.

    :param precision_list: List of precision values
    :type precision_list: torch.Tensor of shape (number of precision values)
    :param recall_list: List of recall values
    :type precision_list: torch.Tensor of shape (number of recall values)
    :return: mAP score computed.
    :rtype: torch.Tensor of shape ()
    """

    if precision_list.shape != recall_list.shape:
        msg = "Precision list (shape {}) and recall list (shape {}) are not of same shape. " \
              "Cannot compute map score".format(precision_list.shape, recall_list.shape)
        logger.error(msg)
        raise AutoMLVisionSystemException(msg, has_pii=False)

    # Add precision 1 at recall 0 to beginning of tensor.
    precision_list = torch.cat((torch.tensor([1.0]), precision_list))
    recall_list = torch.cat((torch.tensor([0.0]), recall_list))

    # Identify indices corresponding to unique recall values in the recall_list.
    recall_delta = recall_list[1:] - recall_list[:-1]
    # Verify that recall_list is sorted
    if torch.lt(recall_delta, 0).any():
        msg = "Recall list is not sorted in ascending order. Cannot compute map score using auc."
        logger.error(msg)
        raise AutoMLVisionSystemException(msg, has_pii=False)

    recall_change_indices = (recall_delta.nonzero(as_tuple=True)[0] + 1).tolist()

    # Maximum precision at unique recall values.
    max_precision_list = torch.zeros(len(recall_change_indices) + 1)
    # Adjusted precision at unique recall values. Computed as maximum precision to the right of that recall value.
    adjusted_precision_list = torch.zeros(len(recall_change_indices) + 1)
    # Unique recall values.
    unique_recall_list = torch.zeros(len(recall_change_indices) + 1)

    same_recall_ranges = zip([0] + recall_change_indices, recall_change_indices + [len(recall_list)])
    for index, (recall_start, recall_end) in reversed(list(enumerate(same_recall_ranges))):
        unique_recall_list[index] = recall_list[recall_start]
        max_precision_list[index] = torch.max(precision_list[recall_start:recall_end])
        adjusted_precision_list[index] = max_precision_list[index]
        if index != adjusted_precision_list.shape[0] - 1:
            adjusted_precision_list[index] = max(adjusted_precision_list[index], adjusted_precision_list[index + 1])

    # Compute mAP as sum(adjusted_precision[i] * (unique_recall[i]-unique_recall[i-1]))
    score = torch.sum(torch.mul(adjusted_precision_list[1:], unique_recall_list[1:] - unique_recall_list[:-1]))

    return score


def map_score_voc_auc_np(precision_list, recall_list):
    """
    Compute mAP score using Voc Area Under Curve (auc) metric.

    The recall values at which maximum precision changes are identified and these points of change are used
    to compute the area under precision recall curve.
    precision_list and recall_list should have the same length.

    :param precision_list: List of precision values
    :type precision_list: <class 'numpy.ndarray'> of shape (number of precision values)
    :param recall_list: List of recall values
    :type precision_list: <class 'numpy.ndarray'> of shape (number of recall values)
    :return: mAP score computed.
    :rtype: <class 'numpy.ndarray'> of shape ()
    """

    # Check that the precision and recall lists are of the same length.
    if precision_list.shape != recall_list.shape:
        msg = "Precision list (shape {}) and recall list (shape {}) are not of same length. " \
              "Cannot compute map score".format(precision_list.shape, recall_list.shape)
        logger.error(msg)
        raise AutoMLVisionSystemException(msg, has_pii=False)

    # Add precision 1 at recall 0.
    precision_list = np.concatenate((np.array([1.0]), precision_list))
    recall_list = np.concatenate((np.array([0.0]), recall_list))

    # Verify that the recalls are sorted.
    recall_delta = recall_list[1:] - recall_list[:-1]
    if np.any(recall_delta < 0):
        msg = "Recall list is not sorted in ascending order. Cannot compute map score using auc."
        logger.error(msg)
        raise AutoMLVisionSystemException(msg, has_pii=False)

    # TODO: use precision instead of max precision to the right. (investigate, propose, implement)
    # Calculate the maximum precision over the points on the curve to the right of the current point. Mathematically,
    # calculate vector p' with p'_i = max{j>=i}{p_j} .
    precision_invcummax = np.maximum.accumulate(precision_list[::-1])[::-1]

    # Calculate the AUC for the PR curve via rectangular integration.
    auc = np.sum(precision_invcummax[1:] * (recall_list[1:] - recall_list[:-1]))

    return auc
