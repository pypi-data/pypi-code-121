import torch.nn as nn


class KeypointLoss(object):
    def __init__(self, use_mse=False) -> None:
        super().__init__()
        if use_mse:
            self.criterion_2d = nn.MSELoss(reduction='none')
            self.criterion_3d = nn.MSELoss(reduction='none')
        else:
            self.criterion_2d = nn.L1Loss()
            self.criterion_3d = nn.L1Loss()
        self.criterion_vertices = nn.L1Loss()

    def cal_pose_2d_loss(self, pred_pose_2d, gt_pose_2d):
        """
        Compute 2D reprojection loss if 2D keypoint annotations are available.
        The confidence (conf) is binary and indicates whether the keypoints exist or not.
        """

        conf = gt_pose_2d[:, :, -1:]
        return (conf * self.criterion_2d(pred_pose_2d, gt_pose_2d[:, :, :-1])).mean()

    def cal_pose_3d_loss(self, pred_pose_3d, gt_pose_3d, has_pose_3d):
        """
        Compute 3D keypoint loss if 3D keypoint annotations are available.
        """
        gt_pose_3d = gt_pose_3d[has_pose_3d == 1]
        conf = gt_pose_3d[:, :, -1:]
        return (
            conf
            * self.criterion_3d(pred_pose_3d[has_pose_3d == 1], gt_pose_3d[:, :, :-1])
        ).mean()

    def cal_vertices_loss(self, pred_vertices, gt_vertices, has_smpl):
        """
        Compute per-vertex loss if vertex annotations are available.
        """
        return self.criterion_vertices(
            pred_vertices[has_smpl == 1], gt_vertices[has_smpl == 1]
        )
