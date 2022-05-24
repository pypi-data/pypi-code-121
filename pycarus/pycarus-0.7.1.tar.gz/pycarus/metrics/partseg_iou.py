from typing import Dict, List, Tuple

import torch

from pycarus.metrics.metric import Metric


class PartSegmentationIoU(Metric):
    def __init__(
        self,
        use_only_category_logits: bool,
        category_to_parts_map: Dict[str, List[int]],
    ) -> None:
        """Create a Metric to compute part segmentation IoU.

        Args:
            use_only_category_logits: Whether to compute predictions considering only
                                      the logits corresponding to the parts belonging
                                      to the current category.
            category_to_parts_map: A dictionary that maps classes to parts labels.
                                   E.G. {"airplane": [0, 1, 2, ...], ...}
        """
        self.use_only_category_logits = use_only_category_logits

        self.category_to_parts_map = category_to_parts_map

        self.part_to_category_map: Dict[int, str] = {}
        for cat in category_to_parts_map:
            for part in category_to_parts_map[cat]:
                self.part_to_category_map[part] = cat

        self.ious: Dict[str, List[float]] = {}

        super().__init__()

    def reset(self) -> None:
        """Reset metric."""
        self.ious = {cat: [] for cat in self.category_to_parts_map}

    def update(self, predictions: torch.Tensor, targets: torch.Tensor) -> None:
        """Update metric.

        Args:
            predictions: A batch of predictions with shape (B, NUM_POINTS, NUM_CLASSES).
            targets: A batch of targets with shape (B, NUM_POINTS).
        """
        batch_size = predictions.shape[0]

        for b in range(batch_size):
            logits = predictions[b]
            cat = self.part_to_category_map[int(targets[b, 0])]
            parts = self.category_to_parts_map[cat]

            if self.use_only_category_logits:
                logits = logits[:, parts]
                pred_labels_per_point = logits.max(1)[1] + parts[0]
            else:
                pred_labels_per_point = logits.max(1)[1]

            part_ious: List[float] = [0.0 for _ in range(len(parts))]
            for p in parts:
                union = torch.sum((targets[b] == p) | (pred_labels_per_point == p))
                if union == 0:
                    # part is not present in this shape
                    part_ious[p - parts[0]] = 1.0
                else:
                    intersection = torch.sum((targets[b] == p) & (pred_labels_per_point == p))
                    part_ious[p - parts[0]] = float(intersection) / (float(union) + 1e-10)

            self.ious[cat].append(sum(part_ious) / (len(part_ious)) + 1e-10)

    def compute(self) -> Tuple[Dict[str, float], float, float]:
        """Compute final results.

        Returns:
            - A dictionary with the mIoU for each class.
            - Mean Class IoU: the average mIoU over all the classes.
            - Mean Instance IoU: the average IoU over all the samples.
        """
        instance_ious: List[float] = []
        mIoUs: Dict[str, float] = {}

        for cat in self.ious:
            for iou in self.ious[cat]:
                instance_ious.append(iou)
            mIoUs[cat] = sum(self.ious[cat]) / (len(self.ious[cat]) + 1e-10)

        mIoU_per_cat = list(mIoUs.values())
        mean_class_iou = sum(mIoU_per_cat) / (len(mIoU_per_cat) + 1e-10)

        mean_instance_iou = sum(instance_ious) / (len(instance_ious) + 1e-10)

        return mIoUs, mean_class_iou, mean_instance_iou
