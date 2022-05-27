from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

from pycarus.metrics.partseg_iou import PartSegmentationIoU


def _get_ious_from_file(
    pred_file: Path,
    use_only_category_logits: bool,
    category_to_parts_map: Dict[str, List[int]],
) -> Tuple[float, float]:
    """Compute instance IoU and class IoU from a prediction file.

    Args:
        pred_file: The path to the prediction file.
        use_only_category_logits: Whether to compute predictions considering only
                                  the logits corresponding to the parts belonging
                                  to the current class.
        category_to_parts_map: A dictionary that maps classes to parts labels.
                               E.G. {"airplane": [0, 1, 2, ...], ...}

    Returns:
        - Mean Class IoU: the average mIoU for each class.
        - Mean Instance IoU: the average IoU for each sample.
    """
    data = np.load(pred_file)
    labels = torch.tensor(data["labels"])
    logits = torch.tensor(data["logits"])

    metric = PartSegmentationIoU(use_only_category_logits, category_to_parts_map)

    for i in range(labels.shape[0]):
        lbl = labels[i].unsqueeze(0)
        lgt = logits[i].unsqueeze(0)
        metric(lgt, lbl)

    mIoUs, mean_class_IoU, mean_instance_IoU = metric.compute()

    return mean_class_IoU, mean_instance_IoU


def pcd_part_segmentation_evaluation(
    pred_files: List[Path],
    outdir: Path,
    use_only_category_logits: bool,
    category_to_parts_map: Dict[str, List[int]],
) -> None:
    """Evaluation for point cloud part segmentation.

    Each prediction file is expected to be produced by a different run
    and should be a .npz file containing one array labelled as "labels"
    and one array labelled as "logits". The "labels" array is a 2-D
    array with integer labels with shape (NUM_PCDS, NUM_POINTS_PER_PCD),
    while the "logits" array is a 3-D array with logits predicted by some
    model with shape (NUM_PCDS, NUM_POINTS_PER_PCD, NUM_CLASSES).

    Args:
        pred_files: The list of files with all the predictions.
        outdir: The path to the directory where results will be saved.
        use_only_category_logits: Whether to compute predictions considering only
                                  the logits corresponding to the parts belonging
                                  to the current category.
        category_to_parts_map: A dictionary that maps classes to parts labels.
                               E.G. {"airplane": [0, 1, 2, ...], ...}
    """
    class_ious: List[float] = []
    inst_ious: List[float] = []

    for pred_file in pred_files:
        class_iou, inst_iou = _get_ious_from_file(
            pred_file,
            use_only_category_logits,
            category_to_parts_map,
        )
        class_ious.append(class_iou)
        inst_ious.append(inst_iou)

    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "results.csv", "wt") as f:
        f.write("METRIC,MEAN,STD\n")

        if len(class_ious) > 1:
            class_iou_mean = np.mean(np.array(class_ious)) * 100
            class_iou_std = np.std(np.array(class_ious)) * 100
            f.write(f"CLASS mIoU,{class_iou_mean:.3f},{class_iou_std:.3f}\n")
            inst_iou_mean = np.mean(np.array(inst_ious)) * 100
            inst_iou_std = np.std(np.array(inst_ious)) * 100
            f.write(f"INSTANCE mIoU,{inst_iou_mean:.3f},{inst_iou_std:.3f}")
        else:
            f.write(f"CLASS mIoU,{class_ious[0] * 100:.3f},-\n")
            f.write(f"INSTANCE mIoU,{inst_ious[0] * 100:.3f},-")
