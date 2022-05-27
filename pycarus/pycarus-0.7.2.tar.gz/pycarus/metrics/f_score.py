from typing import Tuple, Union

import torch
from pytorch3d.ops.knn import knn_points  # type: ignore
from torch import Tensor, sqrt, sum, zeros

from pycarus.geometry.pcd import batchify, unbatchify


def f_score(
    predictions: Union[Tensor, None],
    groundtruth: Union[Tensor, None],
    dist_pred_gt: Union[Tensor, None] = None,
    dist_gt_pred: Union[Tensor, None] = None,
    threshold: float = 0.01,
) -> Tuple[Tensor, Tensor, Tensor]:
    """Compute the F1-Score using the treshold as defined in:

    Knapitsch, A., Park, J., Zhou, Q. Y., & Koltun, V. (2017).
    Tanks and temples: Benchmarking large-scale scene reconstruction.
    ACM Transactions on Graphics (ToG), 36(4), 1-13.

    Args:
        predictions: the predicted point cloud(s) with shape ([B,] NUM_POINTS, 3).
        groundtruth: the groundtruth point cloud(s) with shape ([B,] NUM_POINTS, 3).
        dist_pred_gt (optional): per point distances from predictions to groundtruth
            with shape ([B,] NUM_POINTS). Defaults to None.
        dist_gt_pred (optional): per point distances from groundtruth to predictions
            with shape ([B,] NUM_PTS_GT). Defaults to None.
        threshold: the distance treshold to use. Defaults to 0.01.

    Returns:
        A Tuple with:
        - The fscore with shape ([B,]).
        - The precision with shape ([B,]).
        - The recall with shape ([B,]).
    """
    pred_gt = predictions is not None and groundtruth is not None
    distances = dist_pred_gt is not None and dist_gt_pred is not None
    error_msg = (
        "Only one couple between (predictions, grountruths) and "
        "(dist_pred_gt, dist_gt_pred) should be not None"
    )
    assert (not pred_gt and distances) or (pred_gt and not distances), error_msg

    if predictions is not None and groundtruth is not None:
        pred_copy = torch.clone(predictions)
        gt_copy = torch.clone(groundtruth)

        batched, [pred_copy, gt_copy] = batchify([pred_copy, gt_copy], 3)

        dist_precision, _, _ = knn_points(pred_copy, gt_copy)
        dist_precision = dist_precision.squeeze(-1)
        dist_precision = sqrt(dist_precision)

        dist_recall, _, _ = knn_points(gt_copy, pred_copy)
        dist_recall = dist_recall.squeeze(-1)
        dist_recall = sqrt(dist_recall)
    else:
        dist_pred_gt_copy = torch.clone(dist_pred_gt)  # type: ignore
        dist_gt_pred_copy = torch.clone(dist_gt_pred)  # type: ignore

        batched, [dist_precision, dist_recall] = batchify([dist_pred_gt_copy, dist_gt_pred_copy], 2)

    batch_size = len(dist_precision)
    f_scores = zeros(batch_size).to(dist_precision.device)
    recall = zeros(batch_size).to(dist_precision.device)
    precision = zeros(batch_size).to(dist_precision.device)

    num_samples_prec = dist_precision.shape[1]
    num_samples_rec = dist_recall.shape[1]

    precision = sum((dist_precision < threshold), dim=-1) / max(num_samples_prec, 1)
    recall = sum((dist_recall < threshold), dim=-1) / max(num_samples_rec, 1)

    prec_and_rec = recall + precision
    mask = prec_and_rec > 0

    f_scores[mask] = 2 * recall[mask] * precision[mask] / prec_and_rec[mask]

    if batched:
        f_scores, precision, recall = unbatchify([f_scores, precision, recall])

    return f_scores, precision, recall
