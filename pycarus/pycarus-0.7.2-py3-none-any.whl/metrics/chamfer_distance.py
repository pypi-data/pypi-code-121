from typing import Tuple

import torch
from pytorch3d.ops.knn import knn_points  # type: ignore
from torch import Tensor, mean, sqrt

from pycarus.geometry.pcd import batchify, unbatchify


def chamfer(
    predictions: Tensor,
    groundtruth: Tensor,
    squared: bool = True,
) -> Tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
    """Compute the Chamfer Distance defined as in:

       Fan, H., Su, H., & Guibas, L. J. (2017).
       A point set generation network for 3d object reconstruction from a single image.
       In Proceedings of the IEEE conference on computer vision and pattern recognition (pp. 605-613).

    Args:
        prediction: The source point cloud(s) with shape ([B,] NUM_PTS_PRED, 3).
        groundtruth: The target point cloud(s) with shape ([B,] NUM_PTS_GT, 3).
        squared: If true return the squared euclidean distance.

    Returns:
        A tuple containing:
            - the chamfer distance with shape (B, ).
            - the accuracy, eg. point-wise distance from the prediction to the groundtruth with shape ([B,] NUM_PTS_PRED).
            - the completeness, eg. the distance from the groundtruth to the prediction with shape ([B,] NUM_PTS_GT).
            - the nearest neighbor indices from the prediction to the groundtruth with shape ([B,] NUM_PTS_PRED).
            - the nearest neighbor indices from the groundtruth to the prediction with shape ([B,] NUM_PTS_GT).
    """
    batched, [predictions, groundtruth] = batchify([predictions, groundtruth], 3)

    accuracy, indices_pred_gt, _ = knn_points(predictions, groundtruth)
    accuracy = accuracy.squeeze(-1)
    indices_pred_gt = indices_pred_gt.squeeze(-1)

    completeness, indices_gt_pred, _ = knn_points(groundtruth, predictions)
    completeness = completeness.squeeze(-1)
    indices_gt_pred = indices_gt_pred.squeeze(-1)

    if not squared:
        accuracy = sqrt(accuracy)
        completeness = sqrt(completeness)

    avg_accuracy = mean(accuracy, dim=-1)
    avg_completeness = mean(completeness, dim=-1)

    chamfer = avg_accuracy + avg_completeness

    if batched:
        chamfer, accuracy, completeness, indices_pred_gt, indices_gt_pred = unbatchify(
            [chamfer, accuracy, completeness, indices_pred_gt, indices_gt_pred]
        )

    return chamfer, accuracy, completeness, indices_pred_gt, indices_gt_pred


def chamfer_p(prediction: Tensor, groundtruth: Tensor) -> Tensor:
    """Compute the chamfer distance "P".

    The result is computed as:
        - _, cd_pred2gt, cd_gt2pred, _, _ = chamfer(prediction, groundtruth, squared=False)
        - result = (cd_pred2gt.mean(-1) + cd_gt2pred.mean(-1)) / 2.

    Args:
        prediction: The source point cloud(s) with shape ([B,] NUM_POINTS, 3).
        groundtruth: The target point cloud(s) with shape ([B,] NUM_POINTS, 3).

    Returns:
        The computed chamfer distance "P".
    """
    _, cds_pred_gt, cds_gt_pred, _, _ = chamfer(prediction, groundtruth, squared=False)
    cds_pred_gt = torch.mean(cds_pred_gt, dim=-1)
    cds_gt_pred = torch.mean(cds_gt_pred, dim=-1)

    return (cds_gt_pred + cds_pred_gt) / 2


def chamfer_t(prediction: Tensor, groundtruth: Tensor) -> Tensor:
    """Compute the chamfer distance "T".

    The result is computed as:
        - _, cd_pred2gt, cd_gt2pred, _, _ = chamfer(prediction, groundtruth, squared=True)
        - result = cd_pred2gt.mean(-1) + cd_gt2pred.mean(-1).

    Args:
        prediction: The source point cloud(s) with shape ([B,] NUM_POINTS, 3).
        groundtruth: The target point cloud(s) with shape ([B,] NUM_POINTS, 3).

    Returns:
        The computed chamfer distance "T".
    """
    _, cds_pred_gt_sq, cds_gt_pred_sq, _, _ = chamfer(prediction, groundtruth, squared=True)
    cds_pred_gt_sq = torch.mean(cds_pred_gt_sq, dim=-1)
    cds_gt_pred_sq = torch.mean(cds_gt_pred_sq, dim=-1)

    return cds_pred_gt_sq + cds_gt_pred_sq
